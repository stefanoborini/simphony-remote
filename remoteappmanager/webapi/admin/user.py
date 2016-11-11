from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource

from remoteappmanager.webapi.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class User(Resource):
    def validate_representation(self, representation):
        representation["name"] = str(representation["name"]).strip()
        if len(representation["name"]) == 0:
            raise ValueError("name cannot be empty")
        return representation

    def validate_identifier(self, identifier):
        return int(identifier)

    @gen.coroutine
    @authenticated
    def delete(self, identifier):
        db = self.application.db

        try:
            db.remove_user(id=identifier)
            self.log.info("Removed user with id {}".format(identifier))
        except db_exceptions.NotFound:
            raise exceptions.NotFound()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

    @gen.coroutine
    @authenticated
    def create(self, representation):
        name = representation["name"]

        db = self.application.db
        try:
            id = db.create_user(name)
        except db_exceptions.Exists:
            raise exceptions.Exists()
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()

        return id