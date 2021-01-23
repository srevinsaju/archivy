from archivy.logging import make_logger


class SearchEngine:
    logger = make_logger("search_engine")

    def __init__(
        self,
        config: dict = None
    ):
        self.config = config
        
    @property
    def engine(self):
        raise NotImplementedError

    def bootstrap(self) -> None:
        raise NotImplementedError

    def pre_init(self) -> None:
        pass

    def cleanup(self) -> None:
        pass

    def set_config(self, config: dict):
        self.config = config

    def add(self, dataobj_id: str) -> None:
        raise NotImplementedError()

    def remove(self, dataobj_id: str) -> None:
        raise NotImplementedError()

    def query(self, query: str) -> list:
        raise NotImplementedError()

    def create(self) -> None:
        raise NotImplementedError()
