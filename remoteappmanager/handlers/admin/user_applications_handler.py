from tornado import gen, web

from remoteappmanager.handlers.base_handler import BaseHandler


class UserApplicationsHandler(BaseHandler):
    """Render the user list"""
    @web.authenticated
    @gen.coroutine
    def get(self, id):
        try:
            id = int(id)
        except ValueError:
            raise web.HTTPError(404)

        db = self.application.db
        user = db.get_user(id=id)

        if user is None:
            raise web.HTTPError(404)

        apps = db.get_apps_for_user(user)

        info = [{"mapping_id": mapping_id,
                 "app": app,
                 "policy": policy}
                for mapping_id, app, policy in apps]

        self.render('admin/user_applications.html',
                    info=info,
                    user=user,
                    tab="users")
