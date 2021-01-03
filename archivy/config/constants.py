SEARCH_CONF = {
    "enabled": 0,
    "url": "http://localhost:9200",
    "index_name": "dataobj",
    "search_conf": {
        "settings": {
            "highlight": {"max_analyzed_offset": 100000000},
            "analysis": {
                "analyzer": {
                    "rebuilt_standard": {
                        "stopwords": "_english_",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "kstem", "trim", "unique"],
                    }
                }
            },
        },
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "rebuilt_standard",
                    "term_vector": "with_positions_offsets",
                },
                "tags": {"type": "text", "analyzer": "rebuilt_standard"},
                "body": {"type": "text", "analyzer": "rebuilt_standard"},
            }
        },
    },
}
