import sys

from flask import Flask
from flask_compress import Compress
from flask_login import LoginManager

from archivy.api import api_bp
from archivy.models import User
from archivy import helpers
from archivy.config import ArchivyConfig
from archivy.logging import make_logger
from archivy.search import ElasticSearchEngine
from archivy.routes import views


class ArchivyFlaskApp(Flask):
    logger = make_logger()

    def __init__(self):
        self.archivy_config = ArchivyConfig()
        self.archivy_config.update()
        super(ArchivyFlaskApp, self).__init__(
            __name__,
            template_folder=self.archivy_config["TEMPLATE_DIRECTORY"],
            static_folder=self.archivy_config["STATIC_DIRECTORY"],
            static_host=self.archivy_config["STATIC_HOST"],
        )

        self.archivy_config.add_flask_config(self.config)  # noqa:
        self.config = self.archivy_config
        sys.path.append(self.archivy_config["USER_DIR"])

    def bootstrap_search(self) -> bool:
        if not self.config["SEARCH_CONF"]["enabled"]:
            return False

        search_engine = ElasticSearchEngine()
        search_engine.bootstrap()
        return True

    def bootstrap_login(self):
        login_manager = LoginManager()
        login_manager.login_view = "login"
        login_manager.init_app(self)

        @login_manager.user_loader
        def load_user(user_id):
            db = helpers.get_db()
            res = db.get(doc_id=int(user_id))
            if res and res["type"] == "user":
                return User.from_db(res)
            return None

    def bootstrap_routes(self):
        self.register_blueprint(api_bp, url_prefix="/api")
        self.register_blueprint(views)

    def initialize_extensions(self):
        self.jinja_options["extensions"].append("jinja2.ext.do")


def main():
    app = ArchivyFlaskApp()
    app.bootstrap_search()
    app.bootstrap_login()
    app.bootstrap_routes()
    Compress(app)

    @app.template_filter("pluralize")
    def pluralize(number, singular="", plural="s"):
        if number == 1:
            return singular
        else:
            return plural




