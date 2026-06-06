#imports
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from dotenv import load_dotenv
import json
import os
load_dotenv()

#constants
RPC_URL = os.getenv("BSC_RPC_URL")
contract_address =  os.getenv("contract_address")
owner_address =  os.getenv("owner_address")
spender_address =  os.getenv("spender_address")
private_key =  os.getenv("private_key")
private_key_builder =  os.getenv("private_key_builder")
abi = None
_abi_path = os.path.join(os.path.dirname(__file__), "ABI.json")
with open(_abi_path, "r") as file:
    abi = json.load(file)

#initialize web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

w3.middleware_onion.inject(
    ExtraDataToPOAMiddleware,
    layer=0
)

contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

def read(function_name, *args):
    try:
        print(f"Reading {function_name} with args: {args}")

        fn = getattr(contract.functions, function_name)

        result = fn(*args).call()

        print(f"Result: {result}")

        return result

    except AttributeError:
        error_msg = f"Function '{function_name}' not found in contract ABI"
        print(error_msg)
        return {"error": error_msg}

    except Exception as e:
        error_msg = f"Error calling '{function_name}': {str(e)}"
        print(error_msg)
        return {"error": error_msg}


# count = read("allowance", owner_address, spender_address)
# # print("Count:", count)
# balanceOfOwner = read("balanceOf", owner_address)
# print("Balance of Owner:", balanceOfOwner)

def write(function_name, *args):
    nonce = w3.eth.get_transaction_count(owner_address)

    fn = getattr(contract.functions, function_name)

    tx = fn(*args).build_transaction({
        "from": owner_address,
        "nonce": nonce,
        "chainId": 97,
        "gas": 100000,
        "gasPrice": w3.to_wei(3, "gwei"),
    })

    print(tx)

    signed = w3.eth.account.sign_transaction(
        tx,
        private_key
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed.raw_transaction
    )

    return tx_hash.hex()

