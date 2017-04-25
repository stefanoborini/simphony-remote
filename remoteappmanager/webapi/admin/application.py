from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource
from tornadowebapi.resource_handler import ResourceHandler
from tornadowebapi.traitlets import Unicode

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Application(Resource):
    image_name = Unicode(allow_empty=False, strip=True)


class ApplicationHandler(ResourceHandler):
    resource_class = Application

    @gen.coroutine
    @authenticated
    def delete(self, resource, **kwargs):
        """Removes the application."""
        db = self.application.db
        try:
            id = int(resource.identifier)
        except ValueError:
            raise exceptions.NotFound()

        try:
            db.remove_application(id=id)
            self.log.info("Removed application with id {}".format(id))
        except db_exceptions.NotFound:
            raise exceptions.NotFound()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

    @gen.coroutine
    @authenticated
    def create(self, resource, **kwargs):
        db = self.application.db
        try:
            id = db.create_application(resource.image_name)
        except db_exceptions.Exists:
            raise exceptions.Exists()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

        resource.identifier = str(id)
