from flask_login import LoginManager


class ArchivyLoginManager(LoginManager):

    def user_loader(self, callback):
        super(self).user_loader(callback)
