from archivy.logging import make_logger
from archivy.main import ArchivyFlaskApp


class SearchEngine:
    logger = make_logger("search_engine")

    def __init__(
        self,
        app: ArchivyFlaskApp = None,
        config: dict = None
    ):
        self.config = config
        self.app = app

    def bootstrap(self):
        raise NotImplementedError

    def pre_init(self):
        pass

    def cleanup(self):
        pass

    def set_config(self, config: dict):
        self.config = config
