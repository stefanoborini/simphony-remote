from tornado import gen

from tornadowebapi import exceptions
from tornadowebapi.resource import Resource

from remoteappmanager.restresources.decorators import authenticated
from remoteappmanager.db import exceptions as db_exceptions


class Application(Resource):
    @gen.coroutine
    @authenticated
    def delete(self, identifier):
        """Stop the container."""
        db = self.application.db
        try:
            id = int(identifier)
        except ValueError:
            raise exceptions.BadRepresentation("id")

        try:
            db.remove_application(id=id)
            self.log.info("Removed application with id {}".format(identifier))
        except db_exceptions.NotFound:
            self.log.exception("Could not remove application with "
                               "id {}".format(identifier))
        except db_exceptions.UnsupportedOperation:
            raise exceptions.Unable()
