import os
import sys
from pathlib import Path

from sdk.utils import read_from_json

if getattr(sys, "frozen", False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.absolute()

ABI_DIR = os.path.join(ROOT_DIR, "abis")

# path to private_keys.txt file
PRIVATE_KEYS_PATH = "data/private_keys.txt"

# path to proxies.txt file
PROXIES_PATH = "data/proxies.txt"

# path to deposit_addresses.txt file
DEPOSIT_ADDRESSES_PATH = "data/deposit_addresses.txt"

# path to a database.json file
DATABASE_PATH = "data/database.json"

GAS_MULTIPLIER = 1.2

RETRIES = 1

APPROVE_VALUE_RANGE = None

# tokens abis
FIAT_TOKEN_ABI = read_from_json(os.path.join(ABI_DIR, "fiat_token_abi.json"))
L2_ETH_TOKEN_ABI = read_from_json(os.path.join(ABI_DIR, "l2_eth_token_abi.json"))

# stargate
STG_TOKEN_CONTRACT_ADDRESS = "0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590"
STG_TOKEN_ABI = read_from_json(os.path.join(ABI_DIR, "stg_token_abi.json"))

# merkly
MERKLY_MINTER_MB_CONTRACT_ADDRESS = "0x766b7aC73b0B33fc282BdE1929db023da1fe6458"
MERKLY_MINTER_MR_CONTRACT_ADDRESS = "0x97337A9710BEB17b8D77cA9175dEFBA5e9AFE62e"
MERKLY_MINTER_ABI = read_from_json(os.path.join(ABI_DIR, "merkly_minter_abi.json"))

MERKLY_CHAIN_TO_REFUEL_CONTRACT_ADDRESS = {
    "BSC": "0xeF1eAE0457e8D56A003d781569489Bc5466E574b",
    "Polygon": "0x0E1f20075C90Ab31FC2Dd91E536e6990262CF76d",
    "Celo": "0xC20A842e1Fc2681920C1A190552A2f13C46e7fCF",
    "Gnosis": "0x556F119C7433b2232294FB3De267747745A1dAb4",
    "Arbitrum": "0x4Ae8CEBcCD7027820ba83188DFD73CCAD0A92806",
    "Moonbeam": "0x671861008497782F7108D908D4dF18eBf9598b82",
    "Moonriver": "0xd379c3D0930d70022B3C6EBA8217e4B990705540",
    "Conflux": "0xE47b05F2026a82048caAECf5caE58e5AAE2405eA"
}

MERKLY_REFUEL_ABI = read_from_json(os.path.join(ABI_DIR, "merkly_refuel_abi.json"))

# core bridge
BSC_USDT_CONTRACT_ADDRESS = "0x55d398326f99059fF775485246999027B3197955"

CORE_BRIDGE_CONTRACT_ADDRESS = "0x52e75D318cFB31f9A2EdFa2DFee26B161255B233"
CORE_BRIDGE_ABI = read_from_json(os.path.join(ABI_DIR, "core_bridge_abi.json"))

# USDC
GNOSIS_USDC_CONTRACT_ADDRESS = "0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83"
POLYGON_USDC_CONTRACT_ADDRESS = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"

USDC_CONTRACT_ABI = read_from_json(os.path.join(ABI_DIR, "usdc_token_abi.json"))

# GNOSIS GAS
GNOSIS_GAS_CHECKUP_SLEEP_TIME_RANGE = [5, 10]

# native ETH address
NATIVE_TOKEN_CONTRACT_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

# zero address
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# OKX
OKX_WITHDRAWAL_CHAIN_TO_DATA = {
    "BSC": {
        "fee": 0.002,
    },
    "Polygon": {
        "fee": 0.1,
    },
    "Celo": {
        "fee": 0.0008,
    },
    "Moonbeam": {
        "fee": 0.01,
    },
    "Moonriver": {
        "fee": 0.0001,
    },
    "Conflux": {
        "fee": 0.01  # ?
    }
}

OKX_WITHDRAWAL_FEE = 0.1

OKX_ON_FAIL_RETRY_COUNT = 5

OKX_AFTER_ERROR_SLEEP_TIME = [60, 60]

OKX_WAIT_FOR_WITHDRAWAL_FINAL_STATUS_MAX_WAIT_TIME = [10, 10]

OKX_WAIT_FOR_WITHDRAWAL_FINAL_STATUS_ATTEMPTS = 100

OKX_WAIT_FOR_WITHDRAWAL_RECEIVED_ATTEMPTS = 100

OKX_WAIT_FOR_WITHDRAWAL_RECIEVED_SLEEP_TIME = [60, 60]

WAIT_FOR_BRIDGED_FUNDS_SLEEP_TIME = [60, 60]

MAX_LEFT_TOKEN_PERCENTAGE = 0.0000001
