from eth_utils import keccak
from utils.utils import *
import logging
from ethereumetl.domain.receipt_log import EthReceiptLog
from ethereumetl.domain.lending_log_subcriber import EventSubscriber
from ethereumetl.domain.receipt_lending_log import EthEvent

logger = logging.getLogger('EthLendingService')


class EthReceiptLendingLogMapper(object):

    def build_list_info_event(self, abi):
        list_ = []
        for i in abi:
            arr = self.init_events_subscription(i)
            if not arr:
                continue
            else:
                list_.append(arr)
        return list_

    def init_events_subscription(self, abi):
        event_abi = abi
        if event_abi.get('type') == 'event':
            method_signature_hash = get_topic_filter(event_abi)
            list_params_in_order = get_list_params_in_order(event_abi)
            event_name = event_abi.get('name')
            event_subscriber = EventSubscriber(method_signature_hash, event_name, list_params_in_order)
            topic = method_signature_hash
            address_name_field = get_all_address_name_field(event_abi)
            return [event_subscriber, topic, address_name_field]
        return []

    def eth_event_to_dict(self, eth_event: EthEvent):
        d1 = {
            'type': 'event',
            'event_type': convert_even_type(eth_event.event_type),
            'contract_address': eth_event.contract_address,
            'transaction_hash': eth_event.transaction_hash,
            'log_index': eth_event.log_index,
            'block_number': eth_event.block_number,
        }
        d2 = eth_event.params
        return {**d1, **d2}

    def web3_dict_to_receipt_log(self, dict):
        receipt_log = EthReceiptLog()

        receipt_log.log_index = dict.get('logIndex')

        transaction_hash = dict.get('transactionHash')
        if transaction_hash is not None:
            transaction_hash = transaction_hash.hex()
        receipt_log.transaction_hash = transaction_hash

        block_hash = dict.get('blockHash')
        if block_hash is not None:
            block_hash = block_hash.hex()
        receipt_log.block_hash = block_hash
        receipt_log.block_number = dict.get('blockNumber')
        receipt_log.address = dict.get('address')
        receipt_log.data = dict.get('data')

        if 'topics' in dict:
            receipt_log.topics = [topic.hex() for topic in dict['topics']]

        return receipt_log

    def decode_data_by_type(self, data, type):
        if self.is_integers(type):
            return str(hex_to_dec(data))
        elif type == "address":
            return str(word_to_address(data))
        elif type == "bool":
            return bool(int(hex_to_dec(data)))
        else:
            return data

    def is_integers(self, type):
        return type == "uint256" or type == "uint128" or type == "uint64" or type == "uint32" or type == "uint16" or type == "uint8" or type == "uint" \
               or type == "int256" or type == "init128" or type == "init64" or type == "init32" or type == "init16" or type == "init8" or type == "init"

    def extract_event_from_log(self,receipt_log, event_subscriber):
        topics = receipt_log.topics
        if topics is None or len(topics) < 1:
            logger.warning("Topics are empty in log {} of transaction {}".format(receipt_log.log_index,
                                                                                receipt_log.transaction_hash))
            return None
        if event_subscriber.topic_hash == topics[0]:
            list_params_in_order = event_subscriber.list_params_in_order
            list_params_indexed = [param for param in list_params_in_order if param.get('indexed') == True]
            list_params_unindexed = [param for param in list_params_in_order if param.get('indexed') == False]
            
            num_params_index = len(list_params_indexed)
            num_params_unindex = len(list_params_unindexed)
        
            # Handle indexed event fields
            topics = topics[1:]
            if len(topics) != (num_params_index):
                logger.warning("The number of topics parts is not equal to {} in log {} of transaction {}"
                            .format(str(num_params_index), receipt_log.log_index, receipt_log.transaction_hash))
                return None
            
            event = EthEvent()
            event.contract_address = to_normalized_address(receipt_log.address)
            event.transaction_hash = receipt_log.transaction_hash
            event.log_index = receipt_log.log_index
            event.block_number = receipt_log.block_number
            event.event_type = event_subscriber.name
            for i in range(num_params_index):
                param_i = list_params_indexed[i]
                name = param_i.get("name")
                type = param_i.get("type")
                data = topics[i]
                event.params[name] = self.decode_data_by_type(data, type)

            # Handle unindexed event fields
            event_data = split_to_words(receipt_log.data)
            # if the number of topics and fields in data part != len(list_params_unindexed), then it's a weird event
            if len(event_data) != num_params_unindex:
                element_count = 0       # Count total element in array param and param
                for i in range(num_params_unindex):
                    element_count += 1          # Param lưu offset của mảng
                    param_i = list_params_unindexed[i]
                    name = param_i.get("name")
                    type = param_i.get("type")
                    data = event_data[i]

                    # Hanlde params is array
                    if type.endswith(']'):
                        if type.endswith('[]'):
                            event.params[name] = []
                            element_type = type.split('[')[0]
                            offset = int(int(self.decode_data_by_type(data, "uint256")) / 32)
                            length = int(self.decode_data_by_type(event_data[offset], "uint256"))
                            for index in range(offset+1, offset+length+1):
                                if type == "bytes[]":
                                    offset_byte = int(int(self.decode_data_by_type(event_data[index], "uint256")) / 32)
                                    offset_byte = offset + offset_byte + 1

                                    length_byte = int(self.decode_data_by_type(event_data[offset_byte], "uint256"))
                                    length_params = int(length_byte / 32) + 1

                                    data_byte = ""
                                    for index_byte in range(offset_byte+1, offset_byte+length_params+1):
                                        data_temp = self.decode_data_by_type(event_data[index_byte], element_type)
                                        data_byte = data_byte + data_temp[2:]
                                        element_count += 1      # Param lưu giá trị phần tử byte

                                    data_byte = "0x" + data_byte[:(length_byte*2)]
                                    event.params[name].append(data_byte)

                                    element_count += 1      # Param lưu offset của phần tử mảng byte
                                else:
                                    event.params[name].append(self.decode_data_by_type(event_data[index], element_type))

                                element_count += 1     # Param lưu giá trị phần tử mảng
                            element_count += 1    # Param lưu số phần tử mảng
                    else:
                        event.params[name] = self.decode_data_by_type(data, type)

                if len(event_data) != element_count:
                    logger.warning("The number of data parts is not equal to {} in log {} of transaction {}"
                                .format(str(num_params_unindex), receipt_log.log_index, receipt_log.transaction_hash))
                    return None
            else:
                for i in range(num_params_unindex):
                    param_i = list_params_unindexed[i]
                    name = param_i.get("name")
                    type = param_i.get("type")
                    data = event_data[i]
                    event.params[name] = self.decode_data_by_type(data, type)
                    
            return event

        return None


# remove redundancy in topic
def split_to_words(data):
    if data and len(data) > 2:
        data_without_0x = data[2:]
        words = list(chunk_string(data_without_0x, 64))
        words_with_0x = list(map(lambda word: '0x' + word, words))
        return words_with_0x
    return []


# convert topic to address
def word_to_address(param):
    if param is None:
        return None
    elif len(param) >= 40:
        return to_normalized_address('0x' + param[-40:])
    else:
        return to_normalized_address(param)


# hash abi to be topic
def get_topic_filter(event_abi):
    input_string = event_abi.get("name") + "("
    for input in event_abi.get("inputs"):
        input_string += input.get("type") + ","
    input_string = input_string[:-1] + ")"
    hash = keccak(text=input_string)
    return '0x' + hash.hex()


# get params from abi
def get_list_params_in_order(event_abi):
    indexed = []
    non_indexed = []
    for input in event_abi.get('inputs'):
        if input.get('indexed'):
            indexed.append(input)
        else:
            non_indexed.append(input)
    return indexed + non_indexed


def get_all_address_name_field(event_abi):
    address_name_field = []
    for input in event_abi.get('inputs'):
        if input.get('type') == 'address':
            address_name_field.append(input.get('name'))
    return address_name_field


def convert_even_type(event_type):
    event_type = event_type.upper()
    if event_type == 'LIQUIDATIONCALL':
        return 'LIQUIDATE'
    return event_type