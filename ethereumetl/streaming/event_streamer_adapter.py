import logging
import os
import pathlib
from web3 import Web3
from web3.middleware import geth_poa_middleware
from ethereumetl.jobs.export_event_job import ExportEvent
from configs.config import Networks, Contracts


class EventStreamerAdapter:
    def __init__(
            self,
            network,
            contract_names,
            provider,
            item_exporter,
            batch_size=96,
            max_workers=8
    ):
        self.network = network
        self.item_exporter = None
        self.contract_names = contract_names
        self.w3 = Web3(provider)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.item_exporter = item_exporter
        """
        log performance realtime for mr.dat
        """
        root_path = str(pathlib.Path(__file__).parent.resolve()) + "/../../"
        self.log_performance_file = root_path + "log_performance_file.csv"
        if not os.path.exists(self.log_performance_file):
            with open(self.log_performance_file, 'w+') as f:
                f.write("start_block,end_block,start,end\n")

    def open(self):
        self.item_exporter.open()

    def get_current_block_number(self):
        block_number = int(self.w3.eth.blockNumber)
        return block_number

    def export_all(self, start, end):
        # Extract token transfers
        for contract_name in self.contract_names:
            logging.info(f"Crawling data for {contract_name} in {self.network} from {start} to {end}")
            self._export_token_transfers(start, end, contract_name)

    def _export_token_transfers(self, start, end, contract_name):
        job = ExportEvent(
            start_block=start,
            end_block=end,
            batch_size=self.batch_size,
            web3=self.w3,
            item_exporter=self.item_exporter,
            max_workers=self.max_workers,
            contract_addresses=[Contracts.contracts[contract_name]['addresses'][self.network]],
            abi=Contracts.contracts[contract_name]['abi'],
        )
        job.run()

    def close(self):
        self.item_exporter.close()
