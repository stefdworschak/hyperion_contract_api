import json
from hexbytes import HexBytes
import os
import unittest
from datetime import datetime
import warnings

from web3 import EthereumTesterProvider
from web3.datastructures import AttributeDict

import env_vars

from contract_helper import EthContract, get_abi_bytecode, compile_contract, to_json

CONTRACT_NAME = 'Validator'
NODE_ADDRESS = os.environ.get('IPCProvider', 'No Value Set')
CONTRACT_ADDRESS = '0x4A8A51797Cde3aAC2F7Dc5C81c548428056a6D12'


class ContractTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print("\n----------------------------------------------------------------------")
        print("\nStarting Tests.")
        print("\n----------------------------------------------------------------------")

    def setUp(self):
        warnings.simplefilter("ignore")
        self.contract = None

    def test_compile_contract(self):
        """ Testing compiling a contract """
        self.contract = compile_contract(CONTRACT_NAME)
        self.assertTrue(isinstance(self.contract, dict),
            "Expected type json, received %s" % type(self.contract))
        print("\ntest_compile_contract: 1 assertion passed")

    def test_compile_and_save_contract_to_json(self):
        """ Testing compiling a contract """
        start_timestamp = datetime.now().timestamp()
        write_json_file = to_json(CONTRACT_NAME)
        updated_timestamp = os.path.getmtime(os.path.join(
            os.getcwd(), 'contracts', 'json', CONTRACT_NAME + '.json'))
        self.assertTrue(start_timestamp < updated_timestamp,
            (f"Expected the updated time to be newer than when the test started, ",
             f"but {datetime.fromtimestamp(start_timestamp)} > {datetime.fromtimestamp(updated_timestamp)}"))
        print("\ntest_compile_and_save_contract_to_json: 1 assertion passed")

    def test_create_empty_contract(self):
        """ Testing to create an empty contract """
        self.contract = EthContract(NODE_ADDRESS, already_deployed=False, provider='ipc')
        self.assertTrue(isinstance(self.contract, EthContract), 
            "Expected type EthContract, received %s" % type(self.contract))
        print("\ntest_create_empty_contract: 1 assertion passed")

    def test_importing_abi_bytecode(self):
        """ Testing the ABI and Bytecode import functionality """
        abi, bytecode = get_abi_bytecode(CONTRACT_NAME)
        self.assertTrue(isinstance(abi, list), 
            "Expected type str, received %s" % type(abi))
        self.assertTrue(isinstance(bytecode, str), 
            "Expected type str, received %s" % type(bytecode))
        print("\ntest_importing_abi_bytecode: 2 assertion passed")

    def test_deploy_contract(self):
        """ Testing to deploy a new contract to the POA distributed ledger """
        self.contract = EthContract(NODE_ADDRESS, already_deployed=False, provider='ipc')
        abi, bytecode = get_abi_bytecode(CONTRACT_NAME)
        address = self.contract.deploy(abi=abi, bytecode=bytecode)
        self.assertTrue(address, 
            "Expected address to be returned, but nothig was returned")
        self.assertNotEqual(self.contract._contract, None,
            "Expected the contract to have a _contract, however _contract was type None")
        self.assertNotEqual(self.contract._functions, None,
            "Expected the contract to have a _functions, however _functions was type None")
        print("\ntest_deploy_contract: 3 assertion passed")

    def test_create_existing_contract(self):
        """ Load already deployed contract structure to be used """
        abi, bytecode = get_abi_bytecode(CONTRACT_NAME)
        self.contract = EthContract(
            node_address=NODE_ADDRESS, contract_address=CONTRACT_ADDRESS, 
            abi=abi, bytecode=bytecode, already_deployed=True, provider='ipc')
        self.assertTrue(isinstance(self.contract, EthContract), 
            "Expected type EthContract, received %s" % type(self.contract))
        self.assertNotEqual(self.contract._contract, None,
            "Expected the contract to have a _contract, however _contract was type None")
        self.assertNotEqual(self.contract._functions, None,
            "Expected the contract to have a _functions, however _functions was type None")
        print("\ntest_create_existing_contract: 3 assertion passed")

    def test_add_document(self):
        abi, bytecode = get_abi_bytecode(CONTRACT_NAME)
        self.contract = EthContract(
            node_address=NODE_ADDRESS, contract_address=CONTRACT_ADDRESS, 
            abi=abi, bytecode=bytecode, already_deployed=True, provider='ipc')
        resp = self.contract.send(
           'addDocument', 
            ["a@b.com", "0x949e6011110eee750c48cd49e7b1d298ca2e66d42d8aee6dc4623532ffbd996c"], 
            num_attr=2)
        self.assertTrue(isinstance(json.loads(resp), dict), 
            "Expected type %s, received %s" % (type({}), type(resp)))
        print("\ntest_add_document: 1 assertion passed")
    
    def test_validate_one_document(self):
        test_hex = "0x949e6011110eee750c48cd49e7b1d298ca2e66d42d8aee6dc4623532ffbd996c"
        abi, bytecode = get_abi_bytecode(CONTRACT_NAME)
        self.contract = EthContract(
            node_address=NODE_ADDRESS, contract_address=CONTRACT_ADDRESS, 
            abi=abi, bytecode=bytecode, already_deployed=True, provider='ipc')
        resp = self.contract.call(
            function='validateOne', 
            attrs=["a@b.com", test_hex], 
            num_attr=2)
        self.assertEqual(resp, [test_hex],
            "Expected something to return, but nothing did")
        print("\ntest_validate_one_document: 1 assertion passed")
    
    @classmethod
    def tearDownClass(self):
        print("\n----------------------------------------------------------------------")
        print("\nRan 13 assertions. All passed.")

if __name__ == '__main__':
    unittest.main()
    