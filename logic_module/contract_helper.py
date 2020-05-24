from hexbytes import HexBytes
import json
import os
import web3
from web3 import (Web3, HTTPProvider, IPCProvider, EthereumTesterProvider, 
                  WebsocketProvider)
from web3.middleware import geth_poa_middleware
from solc import compile_standard

import env_vars

NODE_ADDRESS = os.environ.get('IPCProvider', 'No Value Set')
ETH_PK_FILE = os.environ.get('ETH_PK_FILE', 'No Value Set')
CONTRACT_NAME = 'Validator'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

class AbiBytecodeMissing(Exception):
    pass

class WrongAttributeNumber(Exception):
    pass

class NoContractName(Exception):
    pass

class EthContract:
    def __init__(self, node_address, contract_address=None, abi=None, bytecode=None, already_deployed=True, provider="test"):
        self._contract = None
        self._functions = None
        self.abi = abi
        self.bytecode = bytecode
        if provider == 'test':
            self.w3 = Web3(EthereumTesterProvider())
        elif provider == 'ipc':
            self.w3 = Web3(IPCProvider(node_address))
        elif provider == 'websocket':
            self.w3 = Web3(Web3.WebsocketProvider(node_address))
        else: 
            self.w3 = Web3(Web3.HTTPProvider(node_address))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        # Pre funded account 
        self.w3.eth.defaultAccount = self.w3.eth.accounts[0]
        if already_deployed:
            self._contract = self.w3.eth.contract(address=contract_address, abi=abi)
            self._functions = self._contract.functions



    def send(self, function, attrs, num_attr=1):
        _contract_function = getattr(self._functions, function)
        tx_hash = _contract_function(*attrs).transact()
        #tx_hash = self._contract.functions.setMessage('Nihao').transact()
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        return Web3.toJSON(tx_receipt)


    def call(self, function, attrs, num_attr=1):
        #if len(attrs[1]) > 1:
            #attrs = [attr for attr in attrs[1]]
        _contract_function = getattr(self._functions, function)
        response = _contract_function(*attrs).call()
        return _unescape_hex(response)


    def deploy(self, abi=None, bytecode=None):
        if abi is None:
            abi = self.abi
        if bytecode is None:
            bytecode = self.bytecode
        if not abi and not bytecode:
            raise AbiBytecodeMissing("ABI or Bytecode missing")
        deployed_contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = deployed_contract.constructor().transact()
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        self._contract = self.w3.eth.contract(
            address=tx_receipt.contractAddress, abi=abi)
        self._functions = self._contract.functions
        return tx_receipt.contractAddress
    
    def get_latest_block(self):
        return self.w3.eth.getBlock("latest")._dict__


def _hex_converter(attr_dict):
    response_dict = {}
    for key, item in attr_dict.__dict__.items():
        if isinstance(item, type(HexBytes(0))):
            response_dict[key] = item.hex()
        else:
            response_dict[key] = item
    return response_dict


def _unescape_hex(contract_response):
    if isinstance(contract_response, list):
        return [Web3.toHex(response)
                for response in contract_response]
    return Web3.toHex(contract_response)



def compile_contract(contract_name):
    with open(os.path.join(APP_ROOT, f'contracts/sol/{contract_name}.sol'), 'r') as file:
        contract_name = file.name
        contract_content = file.read()
        file.close()
    
    options = {}
    options['language'] = 'Solidity'
    options['sources'] = {
        contract_name: {
            'content': contract_content,
        },
    }

    options['settings'] = {
        "outputSelection": {
            "*": {
                "*": [
                    "metadata", "evm.bytecode", 
                    "evm.bytecode.sourceMap"]
                }
            }
        }

    return compile_standard(options)


def to_json(contract_name=None):
    if contract_name is None:
        raise NoContractName
    compiled_contract = compile_contract(contract_name)
    with open(os.path.join(APP_ROOT, f'contracts/json/{contract_name}.json'), 'w+') as contract:
        contract.write(json.dumps(compiled_contract))
        contract.close()
    return contract.name


def from_json(contract_name=None):
    if contract_name is None:
        raise NoContractName
    with open(os.path.join(APP_ROOT, f'contracts/json/{contract_name}.json'), 'r') as file:
        contract_content = json.loads(file.read())
        file.close()
    return contract_content


def get_abi(contract):
    return json.loads(contract['contracts'][f'/home/pi/hyperion_contract_api/logic_module/contracts/sol/{CONTRACT_NAME}.sol'][CONTRACT_NAME]['metadata'])['output']['abi']


def get_bytecode(contract):
    return contract['contracts'][f'/home/pi/hyperion_contract_api/logic_module/contracts/sol/{CONTRACT_NAME}.sol'][CONTRACT_NAME]['evm']['bytecode']['object']


def get_abi_bytecode(contract_name):
    contract = from_json(contract_name)
    return [get_abi(contract), get_bytecode(contract)]
