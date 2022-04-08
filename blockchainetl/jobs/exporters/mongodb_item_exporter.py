import collections
import logging
import sys
import threading
import time

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

from configs.config import MongoDBConfig
from data_storage.memory_storage_test_performance import MemoryStoragePerformance

logger = logging.getLogger("Mongo item exporter")


class Wallet:
    def __init__(self, address=""):
        self.address = address
        self.created_at = sys.maxsize
        self.created_at_block_number = sys.maxsize
        self.last_updated_at_block_number = 0
        self.last_updated_at = 0
        self.transaction_number = 0


class MongodbItemExporter(object):
    """Manages connection to  database and makes async queries
    """

    def __init__(self, connection_url, db_prefix="", add_wallets=True):
        self._conn = None
        # url = f"mongodb://{MongoDBConfig.NAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}"
        url = connection_url
        self.add_wallets = add_wallets
        self.mongo = MongoClient(url)

        if db_prefix:
            mongo_db_str = db_prefix + "_" + MongoDBConfig.DATABASE
        else:
            mongo_db_str = MongoDBConfig.DATABASE
        self.mongo_db = self.mongo[mongo_db_str]
        self.mongo_blocks = self.mongo_db[MongoDBConfig.BLOCKS]
        self.mongo_transactions = self.mongo_db[MongoDBConfig.TRANSACTIONS]
        self.token_transfers = self.mongo_db[MongoDBConfig.TOKEN_TRANSFERS]
        self.contracts = self.mongo_db[MongoDBConfig.CONTRACTS]
        self.mongo_tokens = self.mongo_db[MongoDBConfig.TOKENS]
        self.mongo_receipts = self.mongo_db[MongoDBConfig.RECEIPTS]
        self.mongo_logs = self.mongo_db[MongoDBConfig.LOGS]
        self.mongo_collectors = self.mongo_db[MongoDBConfig.COLLECTORS]
        self.mongo_wallets = self.mongo_db[MongoDBConfig.WALLETS]

        self.local_storage = MemoryStoragePerformance.getInstance()

    def open(self):
        pass

    def export_items(self, items):
        items_grouped_by_type, wallets = group_by_item_type(items, self.add_wallets)
        start = time.time()
        threads = []
        for type in items_grouped_by_type:
            collection_name = type + "s"
            try:
                t = threading.Thread(target=self.mongo_db[collection_name].insert_many,
                                     args=(items_grouped_by_type[type], False))
                threads.append(t)
                # self.mongo_db[collection_name].insert_many(items_grouped_by_type[type], ordered=False)
            except BulkWriteError as e:
                logger.warning(f"err duplicate with {type} : {e} ")
            except Exception as e:
                logger.warning(f"err with {type} : {e}")

        # logger.info(f"Success write items to collections take {end - start}")
        if self.add_wallets:
            t = threading.Thread(target=self.update_wallet_history, args=(wallets,))
            threads.append(t)
            # self.update_wallet_history(wallets)
        for t in threads:
            t.start()

        for t in threads:
            t.join()
        end = time.time()
        logger.info(f"Success write items to collections take {end - start}")

    def update_wallet_history(self, wallets: dict):
        """

        :param wallets:
        :return:
        """
        start = time.time()
        if not wallets:
            return
        bulk_operations = []
        for address in wallets:
            wallet = wallets[address]
            bulk_operations.append(self._wrap_update_wallet_history(wallet))
        self.mongo_wallets.bulk_write(bulk_operations, ordered=False)
        end = time.time()
        logger.info(f"Success write wallet history to database take {end - start}")

    def _wrap_update_wallet_history(self, wallet_history: Wallet) -> UpdateOne:

        filter = {"_id": wallet_history.address}
        set_update = {
            "_id": wallet_history.address,
            "address": wallet_history.address
        }

        update = {
            "$set": set_update,
            "$inc": {
                "transaction_number": wallet_history.transaction_number
            },
            "$max": {
                "last_updated_at_block_number": wallet_history.last_updated_at_block_number,
                "last_updated_at": wallet_history.last_updated_at
            },
            "$min": {
                "created_at_block_number": wallet_history.created_at_block_number,
                "created_at": wallet_history.created_at
            }
        }

        return UpdateOne(filter, update, upsert=True)

    def close(self):
        pass


def group_by_item_type(items, add_wallets):
    wallets = dict()
    result = collections.defaultdict(list)
    for item in items:
        add_id_to_item(item)
        result[item.get('type')].append(item)
        if add_wallets and item.get('type') == "transaction":
            from_address = item.get("from_address")
            to_address = item.get("to_address")
            timestamp = item.get("block_timestamp")
            block_number = item.get("block_number")
            tx_id = item.get("hash")
            if not wallets.get(from_address):
                wallets[from_address] = Wallet(from_address)
            if not wallets.get(to_address):
                wallets[to_address] = Wallet(to_address)

            wallets[from_address].created_at = min(wallets[from_address].created_at, timestamp)
            wallets[to_address].created_at = min(wallets[to_address].created_at, timestamp)

            wallets[from_address].created_at_block_number = min(wallets[from_address].created_at_block_number,
                                                                block_number)
            wallets[to_address].created_at_block_number = min(wallets[to_address].created_at_block_number, block_number)

            wallets[from_address].last_updated_at = max(wallets[from_address].last_updated_at, timestamp)
            wallets[to_address].last_updated_at = max(wallets[to_address].last_updated_at, timestamp)

            wallets[from_address].last_updated_at_block_number = max(wallets[from_address].last_updated_at_block_number,
                                                                     block_number)
            wallets[to_address].last_updated_at_block_number = max(wallets[to_address].last_updated_at_block_number,
                                                                   block_number)

            wallets[from_address].transaction_number += 1
            wallets[to_address].transaction_number += 1

    return result, wallets


type_to_id_field = {
    "block": "number",
    "contract": "address",
    "log": "item_id",
    "receipt": "transaction_hash",
    "token_transfer": "item_id",
    "token": "address",
    "transaction": "hash"
}


def add_id_to_item(item):
    # id_field = type_to_id_field.get(item.get("type"))
    id_field = "item_id"
    if id_field:
        item["_id"] = item.pop(id_field)
