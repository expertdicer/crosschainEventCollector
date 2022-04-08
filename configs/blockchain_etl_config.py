import os


class BlockchainEtlConfig:
    LOG_FILE = os.environ.get("BLOCKCHAIN_ETL_LOG_FILE") or None
    PROVIDER_URI = os.environ.get("BLOCKCHAIN_ETL_PROVIDER_URI") or "https://bsc-dataseed.binance.org/"
    LAG = os.environ.get("BLOCKCHAIN_ETL_LAG") or 0
    BATCH_SIZE = os.environ.get("BLOCKCHAIN_ETL_BATCH_SIZE") or 4
    MAX_WORKERS = os.environ.get("BLOCKCHAIN_ETL_MAX_WORKERS") or 8
    START_BLOCK = os.environ.get("BLOCKCHAIN_ETL_START_BLOCK") or 0
    PERIOD_SECONDS = os.environ.get("BLOCKCHAIN_ETL_PERIOD_SECONDS") or 10
    PID_FILE = os.environ.get("BLOCKCHAIN_ETL_PID_FILE") or None
    BLOCK_BATCH_SIZE = os.environ.get("BLOCKCHAIN_ETL_BLOCK_BATCH_SIZE") or 32
    OUTPUT = os.environ.get("BLOCKCHAIN_ETL_OUTPUT") or "mongodb://just_for_dev:password_for_dev@localhost:27027/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false"
    ENTITY_TYPES = os.environ.get("BLOCKCHAIN_ETL_ENTITY_TYPES") or "block,transaction,log,token_transfer,trace,contract,token"
    STREAM_ID = os.environ.get("BLOCKCHAIN_ETL_STREAM_ID") or None
