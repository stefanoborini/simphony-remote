import os
from unittest.mock import patch

from remoteappmanager.docker.image import Image
from remoteappmanager.rest.http import httpstatus
from remoteappmanager.docker.container import Container as DockerContainer
from remoteappmanager.tests.mocking import dummy
from remoteappmanager.tests.temp_mixin import TempMixin
from remoteappmanager.tests.utils import (
    AsyncHTTPTestCase,
    mock_coro_factory,
    mock_coro_new_callable)
from tornado import escape


class TestContainer(TempMixin, AsyncHTTPTestCase):
    def setUp(self):
        self._old_proxy_api_token = os.environ.get("PROXY_API_TOKEN", None)
        os.environ["PROXY_API_TOKEN"] = "dummy_token"

        def cleanup():
            if self._old_proxy_api_token is not None:
                os.environ["PROXY_API_TOKEN"] = self._old_proxy_api_token
            else:
                del os.environ["PROXY_API_TOKEN"]

        self.addCleanup(cleanup)

        super().setUp()

    def get_app(self):
        app = dummy.create_application()
        app.hub.verify_token.return_value = {
            'pending': None,
            'name': app.settings['user'],
            'admin': False,
            'server': app.settings['base_urlpath']}
        return app

    def test_items(self):
        manager = self._app.container_manager
        manager.image = mock_coro_factory(Image())
        manager.containers_from_mapping_id = mock_coro_factory(
            [DockerContainer()])

        res = self.fetch(
            "/user/username/api/v1/containers/",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
        )

        self.assertEqual(res.code, httpstatus.OK)

        self.assertEqual(escape.json_decode(res.body),
                         {"items": ["", ""]})

    def test_create(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            manager = self._app.container_manager
            manager.start_container = mock_coro_factory(DockerContainer(
                url_id="3456"
            ))
            res = self.fetch(
                "/user/username/api/v1/containers/",
                method="POST",
                headers={
                    "Cookie": "jupyter-hub-token-username=foo"
                },
                body=escape.json_encode(dict(
                    mapping_id="mapping_id"
                )))

            self.assertEqual(res.code, httpstatus.CREATED)

            # The port is random due to testing env. Check if it's absolute
            self.assertIn("http://", res.headers["Location"])
            self.assertIn("/api/v1/containers/3456/", res.headers["Location"])

    def test_create_fails(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable(
                       side_effect=TimeoutError("timeout"))):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            res = self.fetch(
                "/user/username/api/v1/containers/",
                method="POST",
                headers={
                    "Cookie": "jupyter-hub-token-username=foo"
                },
                body=escape.json_encode(dict(
                    mapping_id="mapping_id"
                )))

            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)
            self.assertTrue(
                self._app.container_manager.stop_and_remove_container.called)
            self.assertEqual(escape.json_decode(res.body), {
                "type": "Unable",
                "message": "timeout"})

    def test_create_fails_for_reverse_proxy_failure(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            self._app.reverse_proxy.register = mock_coro_factory(
                side_effect=Exception("Boom!"))

            res = self.fetch(
                "/user/username/api/v1/containers/",
                method="POST",
                headers={
                    "Cookie": "jupyter-hub-token-username=foo"
                },
                body=escape.json_encode(dict(
                    mapping_id="mapping_id"
                )))

            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)
            self.assertTrue(
                self._app.container_manager.stop_and_remove_container.called)
            self.assertEqual(escape.json_decode(res.body), {
                "type": "Unable",
                "message": "Boom!"})

    def test_create_fails_for_start_container_failure(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_new_callable()):

            self._app.container_manager.stop_and_remove_container = \
                mock_coro_factory()
            self._app.container_manager.start_container = mock_coro_factory(
                side_effect=Exception("Boom!"))

            res = self.fetch(
                "/user/username/api/v1/containers/",
                method="POST",
                headers={
                    "Cookie": "jupyter-hub-token-username=foo"
                },
                body=escape.json_encode(dict(
                    mapping_id="mapping_id"
                )))

            self.assertEqual(res.code, httpstatus.INTERNAL_SERVER_ERROR)
            self.assertEqual(escape.json_decode(res.body), {
                "type": "Unable",
                "message": "Boom!"})

    def test_create_fails_for_missing_mapping_id(self):
        res = self.fetch(
            "/user/username/api/v1/containers/",
            method="POST",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
            body=escape.json_encode(dict(
                whatever="123"
            )))

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(escape.json_decode(res.body),
                         {"type": "BadRequest",
                          "message": "missing mapping_id"})

    def test_create_fails_for_invalid_mapping_id(self):
        res = self.fetch(
            "/user/username/api/v1/containers/",
            method="POST",
            headers={
                "Cookie": "jupyter-hub-token-username=foo"
            },
            body=escape.json_encode(dict(
                mapping_id="whatever"
            )))

        self.assertEqual(res.code, httpstatus.BAD_REQUEST)
        self.assertEqual(escape.json_decode(res.body),
                         {"type": "BadRequest",
                          "message": "unrecognized mapping_id"})

    def test_retrieve(self):
        self._app.container_manager.container_from_url_id = mock_coro_factory(
            DockerContainer()
        )
        res = self.fetch("/user/username/api/v1/containers/found/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.OK)

        content = escape.json_decode(res.body)
        self.assertEqual(content["image_name"], "")
        self.assertEqual(content["name"], "")

        self._app.container_manager.container_from_url_id = \
            mock_coro_factory(return_value=None)
        res = self.fetch("/user/username/api/v1/containers/notfound/",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_delete(self):
        self._app.container_manager.container_from_url_id = mock_coro_factory(
            DockerContainer()
        )
        res = self.fetch("/user/username/api/v1/containers/found/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NO_CONTENT)

        self._app.container_manager.container_from_url_id = \
            mock_coro_factory(return_value=None)
        res = self.fetch("/user/username/api/v1/containers/notfound/",
                         method="DELETE",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         })
        self.assertEqual(res.code, httpstatus.NOT_FOUND)

    def test_post_start(self):
        with patch("remoteappmanager"
                   ".restresources"
                   ".container"
                   ".wait_for_http_server_2xx",
                   new_callable=mock_coro_factory):
            self._app.container_manager.containers_from_mapping_id = \
                mock_coro_factory(return_value=[DockerContainer()])

            self.assertFalse(self._app.reverse_proxy.register.called)
            self.fetch("/user/username/api/v1/containers/",
                       method="POST",
                       headers={
                                "Cookie": "jupyter-hub-token-username=foo"
                       },
                       body=escape.json_encode({"mapping_id": "mapping_id"}))

            self.assertTrue(self._app.reverse_proxy.register.called)

    def test_post_failed_auth(self):
        self._app.hub.verify_token.return_value = {}

        res = self.fetch("/user/username/api/v1/containers/",
                         method="POST",
                         headers={
                             "Cookie": "jupyter-hub-token-username=foo"
                         },
                         body=escape.json_encode({"mapping_id": "12345"}))

        self.assertGreaterEqual(res.code, 400)

    def test_stop(self):
        self._app.container_manager.container_from_url_id = mock_coro_factory(
            DockerContainer()
        )
        self.fetch("/user/username/api/v1/containers/12345/",
                   method="DELETE",
                   headers={
                      "Cookie": "jupyter-hub-token-username=foo"
                   })

        self.assertTrue(self._app.reverse_proxy.unregister.called)