import os
import appdirs
import yaml

from .constants import SEARCH_CONF
from ..logging import make_logger

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Config:
    """Configuration object for the application"""

    logger = make_logger("config")

    def __init__(
        self,
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
            TEMPLATE_DIRECTORY=template_directory,
            STATIC_DIRECTORY=static_directory,
            STATIC_HOST=static_host,
        )

    def __repr__(self):
        return f"ArchivyConfig({self._config})"

    def __getitem__(self, item: str):
        return self._config[item.upper()]

    def __setitem__(self, key: str, value: str):
        self._config[key.upper()] = value

    def __getattr__(self, item: str):
        return self._config[item.upper()]

    def override(self, user_conf: dict):
        self._config.update(user_conf)

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

        if self.config_path and os.path.exists(self.config_path):
            self.logger.info("Custom user configuration found.")
            self.override(self.read())

        # env variables take precedence
        self._config["TEMPLATE_DIRECTORY"] = os.getenv("ARCHIVY_TEMPLATE_DIR")
        self._config["STATIC_DIRECTORY"] = os.getenv("ARCHIVY_STATIC_DIR")

        # make directories
        self.make_dirs()

    def make_dirs(self):
        for i in self._config:
            if not self._config[i] and (i.endswith("DIR") or i.endswith("DIRECTORY")):
                os.makedirs(self._config[i], exist_ok=True)

    def migrate_from_v1(self, old_config: str):
        self.logger.warning("Migrating from v1 Archivy config to v2")
        _data = self.read(old_config)
        with open(self.config_path, "w") as fp:
            fp.write(_data)
