from typing import TypedDict, Literal, Union

import requests
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder
from hyperliquid.utils import constants
from hyperliquid.utils.signing import get_timestamp_ms, sign_l1_action

CreateInputParams = TypedDict("CreateInputParams", {"nonce": int})
CreateInput = TypedDict("CreateInput", {"create": CreateInputParams})
FinalizeEvmContractInput = Union[Literal["firstStorageSlot"], CreateInput]
FinalizeEvmContractAction = TypedDict(
    "FinalizeEvmContractAction",
    {"type": Literal["finalizeEvmContract"], "token": int, "input": FinalizeEvmContractInput},
)

SHOULD_DEPLOY_CONTRACT = False  # Skip deployment - using existing contract
SHOULD_LINK_CONTRACT = True  # Link your existing contract to Hyperliquid
DEFAULT_CONTRACT_ADDRESS = Web3.to_checksum_address(
    "0x44900A4543C09f8C8EC848eCE93CF4F9Ba83C708"  # Your deployed contract address
)
TOKEN = 1  # note that if changing this you likely should also change the abi to have a different name and perhaps also different decimals and initial supply
PRIVATE_KEY = "0xPRIVATE_KEY"  # Change this to your private key

# Connect to the JSON-RPC endpoint
rpc_url = "https://rpc.hyperliquid-testnet.xyz/evm"
w3 = Web3(Web3.HTTPProvider(rpc_url))

# The account will be used both for deploying the ERC20 contract and linking it to your native spot asset
# You can also switch this to create an account a different way if you don't want to include a secret key in code
if PRIVATE_KEY == "0xPRIVATE_KEY":
    raise Exception("must set private key or create account another way")
account: LocalAccount = Account.from_key(PRIVATE_KEY)
print(f"Running with address {account.address}")
w3.middleware_onion.add(SignAndSendRawMiddlewareBuilder.build(account))
w3.eth.default_account = account.address
# Verify connection
if not w3.is_connected():
    raise Exception("Failed to connect to the Ethereum network")

purr_abi = {
    "_format": "hh-sol-artifact-1",
    "contractName": "Purr",
    "sourceName": "contracts/Purr.sol",
    "abi": [
        {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
                {"indexed": True, "internalType": "address", "name": "spender", "type": "address"},
                {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"},
            ],
            "name": "Approval",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"},
                {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"},
            ],
            "name": "OwnershipTransferred",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"},
            ],
            "name": "Transfer",
            "type": "event",
        },
        {
            "inputs": [],
            "name": "DOMAIN_SEPARATOR",
            "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "owner", "type": "address"},
                {"internalType": "address", "name": "spender", "type": "address"},
            ],
            "name": "allowance",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"},
            ],
            "name": "approve",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "decimals",
            "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "subtractedValue", "type": "uint256"},
            ],
            "name": "decreaseAllowance",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "addedValue", "type": "uint256"},
            ],
            "name": "increaseAllowance",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
            "name": "mint",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "name",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
            "name": "nonces",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "owner",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "owner", "type": "address"},
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "value", "type": "uint256"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                {"internalType": "uint8", "name": "v", "type": "uint8"},
                {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                {"internalType": "bytes32", "name": "s", "type": "bytes32"},
            ],
            "name": "permit",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {"inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
        {
            "inputs": [],
            "name": "symbol",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"},
            ],
            "name": "transfer",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "from", "type": "address"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "amount", "type": "uint256"},
            ],
            "name": "transferFrom",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
            "name": "transferOwnership",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
    ],
    "bytecode": "0x6101406040523480156200001257600080fd5b5060405180604001604052806004815260200163282aa92960e11b81525080604051806040016040528060018152602001603160f81b815250604051806040016040528060[...]",
    "deployedBytecode": "0x608060405234801561001057600080fd5b50600436106101365760003560e01c80637ecebe00116100b2578063a457c2d711610081578063d505accf11610066578063d505accf14610287578063dd62ed3e1461[...]",
    "linkReferences": {},
    "deployedLinkReferences": {},
}

creation_nonce: int
if SHOULD_DEPLOY_CONTRACT:
    Purr = w3.eth.contract(abi=purr_abi["abi"], bytecode=purr_abi["bytecode"])
    creation_nonce = w3.eth.get_transaction_count(account.address)
    tx_hash = Purr.constructor().transact()
    print("constructor tx_hash", tx_hash, creation_nonce)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("constructor tx_receipt", tx_receipt)
    contract_address = tx_receipt["contractAddress"]
    purr = w3.eth.contract(address=contract_address, abi=purr_abi["abi"])

    initial_supply = w3.to_wei(1_000_000_000, "ether")  # this should match the max supply on the L1
    tx_hash = purr.functions.mint(initial_supply).transact()
    print("mint tx_hash", tx_hash)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("mint tx_receipt", tx_receipt)

    system_address = "0x2000000000000000000000000000000000000001"
    tx_hash = purr.functions.transfer(system_address, initial_supply).transact()
    print("transfer tx_hash", tx_hash)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("transfer tx_receipt", tx_receipt)
    print(purr.functions.balanceOf(system_address).call())
else:
    contract_address = DEFAULT_CONTRACT_ADDRESS
    creation_nonce = 0

if SHOULD_LINK_CONTRACT:
    assert contract_address is not None
    action = {
        "type": "spotDeploy",
        "requestEvmContract": {
            "token": TOKEN,
            "address": contract_address.lower(),
            "evmExtraWeiDecimals": 13,
        },
    }
    nonce = get_timestamp_ms()
    signature = sign_l1_action(account, action, None, nonce, False)
    payload = {
        "action": action,
        "nonce": nonce,
        "signature": signature,
        "vaultAddress": None,
    }
    response = requests.post(constants.TESTNET_API_URL + "/exchange", json=payload)
    print(response.json())

    use_create_finalization = True
    finalize_action: FinalizeEvmContractAction
    if use_create_finalization:
        finalize_action = {
            "type": "finalizeEvmContract",
            "token": TOKEN,
            "input": {"create": {"nonce": creation_nonce}},
        }
    else:
        finalize_action = {"type": "finalizeEvmContract", "token": TOKEN, "input": "firstStorageSlot"}
    nonce = get_timestamp_ms()
    signature = sign_l1_action(account, finalize_action, None, nonce, False)
    payload = {
        "action": finalize_action,
        "nonce": nonce,
        "signature": signature,
        "vaultAddress": None,
    }
    response = requests.post(constants.TESTNET_API_URL + "/exchange", json=payload)
    print(response.json())
