import elasticsearch

from archivy import helpers
from archivy.logging import make_logger
from archivy.main import ArchivyFlaskApp
from archivy.search.base import SearchEngine

es = helpers.get_elastic_client()


class ElasticSearchEngine(SearchEngine):
    logger = make_logger("elastic_search_engine")

    def __init__(self, app: ArchivyFlaskApp = None, config: dict = None):
        super().__init__(app, config)
        self.create_index()

    def create_index(self):
        try:
            es.indices.create(
                index=self.app.config["SEARCH_CONF"]["index_name"],
                body=self.app.config["SEARCH_CONF"]["search_conf"],
            )
        except elasticsearch.exceptions.RequestError:
            self.logger.info("Elasticsearch index already created")
