from tornado import web

from remoteappmanager.base_application import BaseApplication
from remoteappmanager.handlers.api import (
    AdminHomeHandler,
    ContainersHandler,
    UsersHandler,
    ApplicationsHandler)
from remoteappmanager.utils import url_path_join, with_end_slash


class AdminApplication(BaseApplication):
    """Tornado main application"""

    def _webapi_resources(self):
        return []

    def _web_handlers(self):
        base_urlpath = self.command_line_config.base_urlpath
        return [
            (base_urlpath, AdminHomeHandler),
            (with_end_slash(
                url_path_join(base_urlpath, "containers")
            ), ContainersHandler),
            (with_end_slash(
                url_path_join(base_urlpath, "users")
            ), UsersHandler),
            (with_end_slash(
                url_path_join(base_urlpath, "applications")
            ), ApplicationsHandler),
            (base_urlpath.rstrip('/'),
             web.RedirectHandler, {"url": base_urlpath}),
        ]
