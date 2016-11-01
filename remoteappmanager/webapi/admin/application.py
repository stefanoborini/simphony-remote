from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Application(Resource):
    def validate_representation(self, representation):
        representation["image_name"] = str(representation["image_name"])
        if len(representation["image_name"]) == 0:
            raise ValueError("image_name cannot be empty")

        return representation

    def validate_identifier(self, identifier):
        return int(identifier)

    @gen.coroutine
    @authenticated
    def delete(self, identifier):
        """Removes the application."""
        db = self.application.db

        try:
            db.remove_application(id=identifier)
            self.log.info("Removed application with id {}".format(identifier))
        except db_exceptions.NotFound:
            raise exceptions.NotFound()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

    @gen.coroutine
    @authenticated
    def create(self, representation):
        image_name = representation["image_name"]

        db = self.application.db
        try:
            id = db.create_application(image_name)
        except db_exceptions.Exists:
            raise exceptions.Exists()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

        return id
