""" Build the Validator.sol contract and deploy it to the test environment
    Solidity executables (solc, solctest) downloaded from 
    https://github.com/ethereum/solidity/releases

    Using version 0.4.25
    https://github.com/ethereum/solidity/releases/tag/v0.4.25

    Reference using this official example:
    https://web3py.readthedocs.io/en/stable/contracts.html
"""
import json
import os
import time

import web3
from web3 import Web3, HTTPProvider, IPCProvider
from solc import compile_standard

import env_vars

NODE_ADDRESS = os.environ.get('IPCProvider', 'No Value Set')


def create_options(filename):
    with open(filename, 'r') as file:
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

    return options


def main():
    """ Compile the Solidity contract using the set options and 
        write it to a file JSON file

    """
    compiled_sol = compile_standard(create_options('contracts/Tester.sol'))
    
    # Test intstance
    w3 = Web3(IPCProvider(NODE_ADDRESS))

    # Pre funded account 
    #w3.eth.defaultAccount = w3.eth.accounts[0]

    # Get account from private key
    account = w3.eth.accounts[0]

    # To deploy a Solidity Contract on Ethereum you need the contract's
    # bytecode and ABI
    bytecode = compiled_sol['contracts']['contracts/Tester.sol']['Tester']['evm']['bytecode']['object']
    abi = json.loads(compiled_sol['contracts']['contracts/Tester.sol']['Tester']['metadata'])['output']['abi']

if __name__ == '__main__':
    main()
