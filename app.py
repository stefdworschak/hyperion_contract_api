import json
import os
from hexbytes import HexBytes
from datetime import datetime

from web3 import EthereumTesterProvider
from web3.datastructures import AttributeDict

from flask import Flask, render_template, jsonify, request

import env_vars

from logic.contract_helper import EthContract, get_abi_bytecode, compile_contract, to_json

CONTRACT_NAME = 'Validator'
NODE_ADDRESS = os.environ.get('IPCProvider', 'No Value Set')
CONTRACT_ADDRESS = '0x4A8A51797Cde3aAC2F7Dc5C81c548428056a6D12'

app = Flask(__name__, static_url_path='/static')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/api', methods=['GET','POST'])
def api():
    """This is the function you can put your API logic into

    Returns a JSON object
    """
    try:
        data = json.loads(request.form.get("data"))
        user = data.get('user')
        hashes = data.get('hashes')
        action = data.get('action')
        abi, bytecode = get_abi_bytecode(CONTRACT_NAME)
        contract = EthContract(
                node_address=NODE_ADDRESS, contract_address=CONTRACT_ADDRESS, 
                abi=abi, bytecode=bytecode, already_deployed=True, provider='ipc')
        status = 200
        if action == "addDocument":
            print("Add Document")
            resp = contract.send(function='addDocument', attrs=[user, hashes[0]], num_attr=2)
            data_type = "add"
        elif action == "addMultiple":
            print("Add Multiple Documents")
            for h  in hashes:
                resp = contract.send(function='addDocument', attrs=[user, h], num_attr=2)
            data_type = "add"
        elif action == "validateOne":
            print("Validate One")
            resp = contract.call(function='validateOne', attrs=[user, hashes[0]], num_attr=2)
            data_type = "validate"
        elif action == "validateMultiple":
            print("Validate Multiple")
            resp = []
            for h in hashes:
                r = contract.call(function='validateOne', attrs=[user, h], num_attr=2)
                resp.append(r)
            data_type = "validate"
        else:
            print("Wrong Action")
            status = 505
            resp = "An unexpected error occurred"
            data_type = "error"
    except Exception as e:
        status = 505
        data_type = "error"
        resp = str(e)

    response_item = {
        "status": status,
        "data_type": data_type,
        "data" :resp
    }
    print(response_item)
    return json.dumps(response_item)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)