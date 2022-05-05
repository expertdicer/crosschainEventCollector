import os
import random
from artifacts.abi.multi_sig_wallet import MULTI_SIG_WALLET
from artifacts.abi.multi_sig_wallet_factory import MULTI_SIG_WALLET_FACTORY
from artifacts.abi.recorder import RECORDER


class Config:
    HOST = '0.0.0.0'
    PORT = 8000


class MongoDBConfig:
    NAME = os.environ.get("MONGO_USERNAME") or "just_for_dev"
    PASSWORD = os.environ.get("MONGO_PASSWORD") or "password_for_dev"
    HOST = os.environ.get("MONGO_HOST") or "localhost"
    PORT = os.environ.get("MONGO_PORT") or "27027"
    DATABASE = "blockchain_etl"
    BLOCKS = "blocks"
    TRANSACTIONS = "transactions"
    TOKEN_TRANSFERS = "token_transfers"
    CONTRACTS = "contracts"
    TOKENS = "tokens"
    RECEIPTS = "receipts"
    LOGS = "logs"
    COLLECTORS = "collectors"
    WALLETS = "wallets"
    LENDING_EVENTS = 'lending_events'
    EVENTS = 'events'


class SIZES:
    UPDATE_SIZE = 10000
    BALANCE_BATCH_SIZE = 100
    ETL_JOB_BATCH_SIZE = 1000
    MAX_RETRIES_COUNT = 5
    DAY_ASYNC = 20
    HOLDERS_BATCH_SIZE_MORALIS = 1000
    HOLDERS_BATCH_SIZE_PRIVATE = 1000
    TIME_SLEEP = 0
    SYNC_TIME = UPDATE_SIZE * 3 + 6000
    # SYNC_TIME = 10


class Contracts:
    MultiSigFactory = {
        'addresses': {
            'kovan': "0x9aBF2D0Daa0BD252c0a0c542BBbB171877bffDee",
            'ropsten': "0xE5d62b5597e453F97f1302399F94337df88d3F96",
            'rinkeby': "0xE5d62b5597e453F97f1302399F94337df88d3F96"
        },
        'abi': MULTI_SIG_WALLET_FACTORY,
    }
    TravaToken = {
        'addresses': {
            'kovan': "0x27E356837F9df025e8827D412c55a78b3A655bce",
            'ropsten': "0x02cA24361754E5dF1B6B69BBf85C51AF16309896",
            'rinkeby': "0x02cA24361754E5dF1B6B69BBf85C51AF16309896"
        },
        'abi': MULTI_SIG_WALLET,
    }
    Recoder = {
        'addresses': {
            'kovan': "0xc8c7ACD7686721da8CefCAfdccF60D73BD6e477C",
            'ropsten': "0x6E3ef7F0410Ce0e0194614C6D276bA088981609E",
            'rinkeby': "0x6E3ef7F0410Ce0e0194614C6D276bA088981609E"
        },
        'abi': RECORDER,
    }
    contracts = {
        'multi_sig_factory': MultiSigFactory,
        'trava_token': TravaToken,
        'recoder': Recoder
    }


class Networks:
    Kovan = {
        'provider': ['https://eth-kovan.alchemyapi.io/v2/ZvZEjsjUaSUJsatHIqdi9n832zW4PPAD'],
        'db_prefix': 'kovan',
    }
    Ropsten = {
        'provider': ['https://eth-ropsten.alchemyapi.io/v2/6-4ym1CfcELADjm9VVFIOpvkh71FhVjo'],
        'db_prefix': 'ropsten'
    }
    Rinkeby = {
        'provider': ['https://eth-rinkeby.alchemyapi.io/v2/SluErBaJPnPl9PSGUYKtyoNl5cMf06hW'],
        'db_prefix': 'rinkeby'
    }
    networks = {
        'kovan': Kovan,
        'rinkeby': Rinkeby,
        'ropsten': Ropsten
    }
