from data_storage.memory_storage import MemoryStorage
import logging
from artifacts.abi.lending_pool_abi import LENDING_POOL_ABI
from artifacts.abi.recorder import RECORDER
from artifacts.abi.multi_sig_wallet_factory import MULTI_SIG_WALLET_FACTORY
from ethereumetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from ethereumetl.mappers.receipt_lending_log_mapper import EthReceiptLendingLogMapper
from configs.config import Contracts


_LOGGER = logging.getLogger(__name__)


def update_events_with_err(event_list):
    for event in event_list:
        event['related_wallets'] = []
    return


class ExportEvent(BaseJob):
    def __init__(self,
                 start_block,
                 end_block,
                 batch_size,
                 max_workers,
                 item_exporter,
                 web3,
                 contract_name,
                 network,
                 abi=LENDING_POOL_ABI,):
        self.web3 = web3
        self.abi = abi
        self.item_exporter = item_exporter
        self.start_block = start_block
        self.end_block = end_block
        self.contract_name = contract_name
        self.network = network
        self.contract_addresses=[Contracts.contracts[contract_name]['addresses'][network]]
        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.receipt_log = EthReceiptLendingLogMapper()
        self.localstorage = MemoryStorage.getInstance()
        self.private_key = '34eae52835122ace28aa1aa77afda645527d90c7ba16b106b991e5de3c22fdc3'
        self.sender = '0x716CC3A781E39ef20375d1B2eCc39A8Bd6b2Efcf'

    def _start(self):
        self.event_data = []
        self.list_abi = self.receipt_log.build_list_info_event(self.abi)
        self.item_exporter.open()
        _LOGGER.info(f'start crawl events')

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.export_token_transfers(self.event_data)
        self.item_exporter.close()
        _LOGGER.info(f'Crawled {len(self.event_data)} events from {self.start_block} to {self.end_block}!')

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self.export_batch
        )

    def export_batch(self, block_number_batch):
        _LOGGER.info(f'crawling event data from {block_number_batch[0]} to {block_number_batch[-1]}')
        for abi in self.list_abi:
            e_list = self.export_events(block_number_batch[0], block_number_batch[-1], abi[0], abi[1],
                                        pools=self.contract_addresses)
            self.event_data += e_list

    def run(self):
        try:
            self._start()
            self._export()
        finally:
            self._end()

    def export_events(self, start_block, end_block, event_subscriber, topic, pools=None):
        filter_params = {
            'fromBlock': start_block,
            'toBlock': end_block,
            'topics': [topic]
        }
        if pools is not None and len(pools) > 0:
            filter_params['address'] = pools

        event_filter = self.web3.eth.filter(filter_params)
        events = event_filter.get_all_entries()
        events_list = []
        for event in events:
            log = self.receipt_log.web3_dict_to_receipt_log(event)
            eth_event = self.receipt_log.extract_event_from_log(log, event_subscriber)
            if eth_event is not None:
                eth_event_dict = self.receipt_log.eth_event_to_dict(eth_event)
                transaction_hash = eth_event_dict.get('transaction_hash')
                event_type = eth_event_dict.get('event_type')
                # if event_type == "MERGEREQUESTCREATED" and self.contract_name == 'recoder':
                #     MultiSigFactory = self.web3.contract(address = Contracts.MultiSigFactory['addresses'][self.network], abi = MULTI_SIG_WALLET_FACTORY)
                #     MultiSigFactory_tx = MultiSigFactory.functions.updaterConnectAddress(
                #         address,
                #         address[],
                #     ).buildTransaction({
                #         'chainId' : x,
                #         'gas': 300000,
                #         'maxFeePerGas': self.web3.toWei('2', 'gwei'),
                #         'maxPriorityFeePerGas': self.web3.toWei('1', 'gwei'),
                #         'nonce': self.web3.eth.get_transaction_count(Contracts.MultiSigFactory['addresses'][self.network]) ,
                #     })
                #     signed_txn = self.web3.eth.account.sign_transaction(MultiSigFactory_tx, private_key=self.private_key)
                #     self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)  
                #     print("Transacion hash:" , self.web3.toHex(w3.keccak(signed_txn.rawTransaction)))
                block_number = eth_event_dict.get('block_number')
                log_index = eth_event_dict.get('log_index')
                eth_event_dict['_id'] = f"transaction_{transaction_hash}_{event_type}_{block_number}_{log_index}"
                events_list.append(eth_event_dict)

        self.web3.eth.uninstallFilter(event_filter.filter_id)

        return events_list
