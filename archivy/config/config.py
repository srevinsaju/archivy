import os
import appdirs
import yaml
from flask import Config

from .constants import SEARCH_CONF
from ..logging import make_logger

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class ArchivyConfig(object):
    """Configuration object for the application"""

    logger = make_logger("config")

    def __init__(
        self,
        flask_config: Config = None,
        config_path: str = None,
        static_directory: str = None,
        template_directory: str = None,
        static_host: str = None,
    ):
        self.config_path = config_path
        self._config = dict(
            VERSION=2,
            DATA_DIR=appdirs.user_data_dir("archivy"),
            CONFIG_DIR=appdirs.user_config_dir("archivy"),
            HOST="127.0.0.1",
            PORT=5000,
            SECRET_KEY=os.urandom(32),
            SEARCH_CONF=SEARCH_CONF,
            USER_DIR=os.getcwd(),
            TEMPLATE_DIRECTORY=template_directory,
            STATIC_DIRECTORY=static_directory,
            STATIC_HOST=static_host,
        )
        self._flask_config = flask_config

    def __dict__(self):
        return self._config

    def __repr__(self):
        return f"ArchivyConfig({self._config})"

    def __getitem__(self, item: str):
        if self._flask_config is None or item not in self._flask_config:
            return self._config[item]
        else:
            return self._flask_config[item]

    def __setitem__(self, key: str, value: str):
        self._config[key] = value

    def add_flask_config(self, config: Config):
        self._flask_config = config

    def override(self, user_conf: dict = None):
        if user_conf:
            self._config.update(user_conf)
        with open(self.config_path) as fp:
            _data = yaml.dump(self._config, fp, Loader=Loader)

    def read(self, yaml_config_path: str = None):
        if yaml_config_path is None:
            yaml_config_path = self.config_path

        with open(yaml_config_path) as fp:
            _data = yaml.load(fp, Loader=Loader)
        return _data

    def update(self):
        """
        Updates the internal config
        :return:
        :rtype:
        """

        if self.exists():
            self.logger.info("Custom user configuration found.")
            self.override(self.read())

        # env variables take precedence
        self._config["TEMPLATE_DIRECTORY"] = os.getenv("ARCHIVY_TEMPLATE_DIR")
        self._config["STATIC_DIRECTORY"] = os.getenv("ARCHIVY_STATIC_DIR")

        # make directories
        self.make_dirs()

    def exists(self):
        return self.config_path and os.path.exists(self.config_path)

    def make_dirs(self):
        for i in self._config:
            if self._config[i] and (i.endswith("DIR") or i.endswith("DIRECTORY")):
                os.makedirs(self._config[i], exist_ok=True)

    def _migrate_from_v1(self, old_config: str):
        self.logger.warning("Migrating from v1 Archivy config to v2")
        _data = self.read(old_config)
        with open(self.config_path, "w") as fp:
            fp.write(_data)

    def migration(self, old_config: str):
        self._migrate_from_v1(old_config)

    def get(self, item, default=None):
        try:
            return self.__getitem__(item=item)
        except KeyError:
            return default

    def setdefault(self, k, v):
        self._flask_config[k] = v
