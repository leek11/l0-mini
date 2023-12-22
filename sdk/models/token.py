from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from sdk.constants import (
    NATIVE_TOKEN_CONTRACT_ADDRESS,
    POLYGON_USDC_CONTRACT_ADDRESS,
    GNOSIS_USDC_CONTRACT_ADDRESS,
    USDC_CONTRACT_ABI,
    L2_ETH_TOKEN_ABI,
    FIAT_TOKEN_ABI,
    BSC_USDT_CONTRACT_ADDRESS,
    STG_TOKEN_CONTRACT_ADDRESS,
    STG_TOKEN_ABI
)


@dataclass
class Token:
    chain_to_contract_mapping: Dict
    decimals: int
    symbol: str
    is_native_token_mapping: Dict[str, bool] | None = None
    abi: dict | None = None
    is_stable_coin: bool = False
    coingecko_id: str | None = None
    round_decimal_places: int | None = None

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return self.symbol

    def __hash__(self):
        return hash(self.chain_to_contract_mapping["ZKERA"])

    def __eq__(self, other):
        return (
                isinstance(other, Token)
                and self.chain_to_contract_mapping["ZKERA"] == other.chain_to_contract_mapping["ZKERA"]
        )

    def to_wei(self, value: float, decimals: int = None) -> int:
        if not decimals:
            decimals = self.decimals
        return int(value * pow(10, decimals))

    def from_wei(self, value: int) -> int:
        return value / pow(10, self.decimals)


MATIC_Token = Token(
    chain_to_contract_mapping={"Polygon": NATIVE_TOKEN_CONTRACT_ADDRESS},
    decimals=18,
    symbol="MATIC",
    is_stable_coin=False,
    is_native_token_mapping={"Polygon": True, "Celo": False, "Gnosis": False},
)

USDC_Token = Token(
    chain_to_contract_mapping={
        "Polygon": POLYGON_USDC_CONTRACT_ADDRESS,
        "Cel": "",
        "Gnosis": GNOSIS_USDC_CONTRACT_ADDRESS,
    },
    abi=USDC_CONTRACT_ABI,
    decimals=6,
    symbol="USDC",
    is_stable_coin=True,
    coingecko_id="usd-coin",
    is_native_token_mapping={"POLYGON": False, "CELO": False, "GNOSIS": False},
)

BNB_Token = Token(
    chain_to_contract_mapping={
        "BSC": NATIVE_TOKEN_CONTRACT_ADDRESS,
    },
    is_native_token_mapping={"BSC": True},
    decimals=18,
    symbol="BNB"
)

USDT_Token = Token(
    chain_to_contract_mapping={
        "BSC": BSC_USDT_CONTRACT_ADDRESS,
    },
    is_native_token_mapping={"BSC": False},
    abi=FIAT_TOKEN_ABI,
    decimals=6,
    symbol="USDT",
    round_decimal_places=2,
    is_stable_coin=True,
    coingecko_id="tether",
)

ETH_Token = Token(
    chain_to_contract_mapping={
        "ZKERA": NATIVE_TOKEN_CONTRACT_ADDRESS,
    },
    abi=L2_ETH_TOKEN_ABI,
    decimals=18,
    symbol="ETH",
    round_decimal_places=6,
    is_native_token_mapping={"ZKERA": True},
    coingecko_id="ethereum",
)

STG_Token = Token(
    chain_to_contract_mapping={
        "Polygon": STG_TOKEN_CONTRACT_ADDRESS
    },
    is_native_token_mapping={"Polygon": False},
    abi=STG_TOKEN_ABI,
    decimals=18,
    symbol="STG"
)
