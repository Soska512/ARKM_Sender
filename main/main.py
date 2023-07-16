from web3 import Web3, Account
from web3.auto import w3
import json


rpc_url = 'https://eth.llamarpc.com' # your node
eth_w3 = Web3(Web3.HTTPProvider(rpc_url))

arkm_address = w3.to_checksum_address('0x6E2a43be0B1d33b726f0CA3b8de60b3482b8b050')
arkm_abi = json.load(open('./abis/token_abi.json'))

arkm_contract = eth_w3.eth.contract(arkm_address, abi=arkm_abi)

binance_address = w3.to_checksum_address('0x0d8857b238fc134e94cdc4fc2e818c2c60a5569b') # where to send tokens


def get_arkm_balance(address):
    return arkm_contract.functions.balanceOf(address).call()


def transfer(account):
    address = account.address
    nonce = eth_w3.eth.get_transaction_count(address)

    transfer_txn = arkm_contract.functions.transferFrom(
        address, binance_address, get_arkm_balance(address)
        ).build_transaction({
            'from': address,
            'nonce': nonce,
        })
        
    transfer_txn.update({'maxFeePerGas': eth_w3.eth.fee_history(eth_w3.eth.get_block_number(), 'latest')['baseFeePerGas'][-1] + eth_w3.eth.max_priority_fee})
    transfer_txn.update({'maxPriorityFeePerGas': eth_w3.eth.max_priority_fee})

    gasLimit = eth_w3.eth.estimate_gas(transfer_txn)
    transfer_txn.update({'gas': gasLimit})

    signed_swap_txn = eth_w3.eth.account.sign_transaction(transfer_txn, account.key)
    swap_txn_hash = eth_w3.eth.send_raw_transaction(signed_swap_txn.rawTransaction)
    return swap_txn_hash



def main():
    with open('keys.txt', 'r') as keys_file:
        accounts = [Account.from_key(line.replace("\n", "")) for line in keys_file.readlines()]
    for account in accounts:
        txn = transfer(account)
        print(f'Hash: https://etherscan.io/tx/{txn.hex()}')

main()