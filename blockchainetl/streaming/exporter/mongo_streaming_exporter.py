import logging
from pprint import pprint

from pymongo import MongoClient, InsertOne
from pymongo.errors import DuplicateKeyError, BulkWriteError
from configs.mongo_constant import MongoIndexConstant
from configs.config import MongoDBConfig
from data_storage.memory_storage_test_performance import MemoryStoragePerformance

logger = logging.getLogger("MongodbStreamingExporter")


class MongodbStreamingExporter(object):
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
        self.token_transfer_col = self.mongo_db[MongoDBConfig.TOKEN_TRANSFERS]
        self.transactions_col = self.mongo_db[MongoDBConfig.TRANSACTIONS]
        self.collector_id = collector_id
        self.local_storage = MemoryStoragePerformance.getInstance()
        self._create_index()

    def _create_index(self):
        if MongoIndexConstant.transaction_block_number_input not in self.transactions_col.index_information():
            self.transactions_col.create_index([("block_number", -1), ("input", "hashed")], background=True,
                                               name=MongoIndexConstant.transaction_block_number_input)

        if MongoIndexConstant.token_transfer not in self.token_transfer_col.index_information():
            self.token_transfer_col.create_index([("block_number", 1), ("log_index", 1)], background=True, unique=True,
                                                 name='block_number_log_index')

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

    def export_token_transfers(self, items):
        if not items:
            return
        for item in items:
            item['_id'] = f"{item['block_number']}_{item['transaction_hash']}_{item['log_index']}"
        try:
            self.token_transfer_col.insert_many(items, ordered=False)
        except BulkWriteError as bwe:
            w_errors = bwe.details['writeErrors']
            for w_error in w_errors:
                code_err = w_error.get('code')
                if code_err == 11000:
                    duplicate_key = w_error.get('keyValue')
                    logger.warning(f'Ignore insert duplicate key: {duplicate_key}')

    def export_token_transfer(self, item):
        item['_id'] = f"{item['block_number']}_{item['transaction_hash']}_{item['log_index']}"
        try:
            self.token_transfer_col.insert_one(item)
        except DuplicateKeyError:
            pass

    def close(self):
        pass
