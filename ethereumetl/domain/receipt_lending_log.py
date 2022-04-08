class EthEvent(object):
    def __init__(self):
        self.contract_address = None
        self.transaction_hash = None
        self.log_index = None
        self.block_number = None
        self.params = {}
        self.event_type = None
