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
            'kovan': "0x4cffae6847DF4Fe1710cb9Ac7aCc943c82748064",
            'ropsten': "0xc8c7ACD7686721da8CefCAfdccF60D73BD6e477C",
            'rinkeby': "0x98ee4AbDb529668fcc7D9291D61CAe4B64DE3aBa"
        },
        'abi': MULTI_SIG_WALLET_FACTORY,
    }
    TravaToken = {
        'addresses': {
            'kovan': "0xd0dFaC175FD0E50120b3407597530Fb8283a9e4c",
            'ropsten': "0xa2f7968ae4c4Bd434e7Ee2F6d9C552fE3061E0FE",
            'rinkeby': "0xB25719D8408696872ff38c445290fab0F117d201"
        },
        'abi': MULTI_SIG_WALLET,
    }
    Recoder = {
        'addresses': {
            'kovan': "0xd0dD2b7f0a287DE5383Fc3776bF91F071a10332A",
            'ropsten': "0xA8BaB078Db497C68920d45c64D68733f4bf6A873",
            'rinkeby': "0xeAb6AE2d09051ACb6876CD1bc608202E2fd7fb6b"
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
