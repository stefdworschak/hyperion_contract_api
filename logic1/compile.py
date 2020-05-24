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
from web3 import Web3, HTTPProvider
from solc import compile_standard

import env_vars

INFURA_URL = os.environ.get('INFURA_URL', 'No Value Set')
#My Account
ETH_PK = os.environ.get('ETH_PK', 'No Value Set')


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
    w3 = Web3(HTTPProvider(INFURA_URL))

    # Pre funded account 
    #w3.eth.defaultAccount = w3.eth.accounts[0]

    # Get account from private key
    account = w3.eth.account.privateKeyToAccount(ETH_PK)

    # To deploy a Solidity Contract on Ethereum you need the contract's
    # bytecode and ABI
    bytecode = compiled_sol['contracts']['contracts/Tester.sol']['Tester']['evm']['bytecode']['object']
    abi = json.loads(compiled_sol['contracts']['contracts/Tester.sol']['Tester']['metadata'])['output']['abi']
    SolContract = w3.eth.contract(abi=abi, bytecode=bytecode)

    construct_txn = SolContract.constructor().buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')})

    signed = account.signTransaction(construct_txn)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print(tx_receipt.contractAddress)

    sol_contract = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=abi)

    tx = sol_contract.functions.setMessage("Hello, World!").buildTransaction({
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 100000,
        'gasPrice': w3.toWei('21', 'gwei')})
    signed = account.signTransaction(tx)
    tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    time.sleep(10)
    print(sol_contract.functions.getMessage().call())
    

if __name__ == '__main__':
    main()
