
import sys
import elasticsearch

from pathlib import Path
from elasticsearch import Elasticsearch
from flask import current_app, g
from tinydb import TinyDB, Query, operations

from archivy.hooks import BaseHooks


def load_hooks():
    try:
        from local_hooks import Hooks
    except ImportError:
        pass
    hooks = BaseHooks()
    return hooks


def get_db(force_reconnect=False):
    """
    Returns the database object that you can use to
    store data persistently
    """
    if "db" not in g or force_reconnect:
        g.db = TinyDB(str(Path(current_app.config["INTERNAL_DIR"]) / "db.json"))

    return g.db


def get_max_id():
    """Returns the current maximum id of dataobjs in the database."""
    db = get_db()
    max_id = db.search(Query().name == "max_id")
    if not max_id:
        db.insert({"name": "max_id", "val": 0})
        return 0
    return max_id[0]["val"]


def set_max_id(val):
    """Sets a new max_id"""
    db = get_db()
    db.update(operations.set("val", val), Query().name == "max_id")

