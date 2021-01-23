import sys
from pathlib import Path

import elasticsearch
from elasticsearch import Elasticsearch

from archivy.logging import make_logger
from archivy.models import DataObj
from archivy.search.base import SearchEngine


class ElasticSearchEngine(SearchEngine):
    logger = make_logger("elasticsearch_engine")

    @property
    def engine(self):
        """Returns the elasticsearch client you can use to search and insert / delete data"""
        if not self.config["SEARCH_CONF"]["enabled"]:
            return None

        es = Elasticsearch(self.config["SEARCH_CONF"]["url"])
        try:
            health = es.cluster.health()
        except elasticsearch.exceptions.ConnectionError:
            self.logger.error(
                "Elasticsearch does not seem to be running on "
                f"{self.config['SEARCH_CONF']['url']}. Please start "
                "it, for example with: sudo service elasticsearch restart"
            )
            self.logger.error(
                "You can disable Elasticsearch by modifying the `enabled` variable "
                f"in {str(Path(self.config['INTERNAL_DIR']) / 'config.yml')}"
            )
            sys.exit(1)

        if health["status"] not in ("yellow", "green"):
            self.logger.warning(
                "Elasticsearch reports that it is not working "
                "properly. Search might not work. You can disable "
                "Elasticsearch by setting ELASTICSEARCH_ENABLED to 0."
            )
        return es

    def bootstrap(self):
        self.create()

    def create(self):
        try:
            self.engine.indices.create(
                index=self.config["SEARCH_CONF"]["index_name"],
                body=self.config["SEARCH_CONF"]["search_conf"],
            )
        except elasticsearch.exceptions.RequestError:
            self.logger.info("Elasticsearch index already created")

    def add(self, model: DataObj):
        """
        Adds dataobj to given index. If object of given id already exists, it will be updated.

        :param model: Instance of `archivy.models.Dataobj`, the object you want to index.
        :type model: DataObj
        :return: Returns True, if addition of the model was successful
        :rtype: bool
        """

        payload = {}
        for field in model.__searchable__:
            payload[field] = getattr(model, field)
        self.engine.index(
            index=self.config["SEARCH_CONF"]["index_name"], id=model.id, body=payload
        )
        return True

    def query(self, query: str) -> list:
        """
        Does an elasticsearch query
        :param query: Query to search
        :type query: basestring
        :return: Returns search results for your given query
        :rtype: list
        """

        search = self.engine.search(
            index=self.config["SEARCH_CONF"]["index_name"],
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"],
                        "analyzer": "rebuilt_standard",
                    }
                },
                "highlight": {
                    "fragment_size": 0,
                    "fields": {
                        "content": {
                            "pre_tags": "==",
                            "post_tags": "==",
                        }
                    },
                },
            },
        )

        hits = []
        for hit in search["hits"]["hits"]:
            formatted_hit = {"id": hit["_id"], "title": hit["_source"]["title"]}
            if "highlight" in hit:
                formatted_hit["highlight"] = hit["highlight"]["content"]
            hits.append(formatted_hit)

        return hits

    def remove(self, dataobj_id):
        """Removes object of given id"""
        self.engine.delete(index=self.config["SEARCH_CONF"]["index_name"], id=dataobj_id)
