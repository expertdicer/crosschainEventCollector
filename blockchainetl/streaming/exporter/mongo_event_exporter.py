import logging
from pprint import pprint

from pymongo import MongoClient, InsertOne
from pymongo.errors import DuplicateKeyError, BulkWriteError
from pymongo import UpdateOne
from blockchainetl.streaming.exporter.streaming_exporter_interface import StreamingExporterInterface
from configs.mongo_constant import MongoIndexConstant
from configs.config import MongoDBConfig
from data_storage.memory_storage_test_performance import MemoryStoragePerformance
import time

logger = logging.getLogger("MongodbEventExporter")


class MongodbEventExporter(StreamingExporterInterface):
    """Manages connection to  database and makes async queries
    """

    def __init__(self, connection_url, collector_id, db_prefix=""):
        self._conn = None
        # url = f"mongodb://{MongoDBConfig.NAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}"
        url = connection_url
        self.mongo = MongoClient(url)
        if db_prefix:
            mongo_db_str = db_prefix + "_" + MongoDBConfig.DATABASE
        else:
            mongo_db_str = MongoDBConfig.DATABASE
        self.mongo_db = self.mongo[mongo_db_str]
        self.mongo_collectors = self.mongo_db[MongoDBConfig.COLLECTORS]
        self.event = self.mongo_db[MongoDBConfig.EVENTS]
        self.collector_id = collector_id
        self.local_storage = MemoryStoragePerformance.getInstance()

    def get_collector(self, collector_id):
        key = {"id": collector_id}
        collector = self.mongo_collectors.find_one(key)
        if not collector:
            collector = {
                "_id": collector_id,
                "id": collector_id
            }
            self.update_collector(collector)
        return collector

    def update_collector(self, collector):
        key = {'id': collector['id']}
        data = {"$set": collector}

        self.mongo_collectors.update_one(key, data, upsert=True)

    def update_latest_updated_at(self, collector_id, latest_updated_at):
        key = {'_id': collector_id}
        update = {"$set": {
            "last_updated_at_block_number": latest_updated_at
        }}
        self.mongo_collectors.update_one(key, update)

    def open(self):
        pass

    def export_items(self, items):
        self.export_token_transfers(items)

    def export_token_transfers(self, operations_data):
        if not operations_data:
            logger.debug(f"Error: Don't have any data to write")
            return
        start = time.time()
        bulk_operations = [UpdateOne({'_id': data['_id']}, {"$set": data}, upsert=True) for data in operations_data]
        logger.info("Updating into events ........")
        try:
            self.event.bulk_write(bulk_operations)
        except Exception as bwe:
            logger.error(f"Error: {bwe}")
        end = time.time()
        logger.info(f"Success write events to database take {end - start}s")

    def export_token_transfer(self, item):
        try:
            self.event.insert_one(item)
        except DuplicateKeyError:
            pass

    def close(self):
        pass