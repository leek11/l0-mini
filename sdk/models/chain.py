from __future__ import annotations

from dataclasses import dataclass
from enum import unique, Enum

from config import (
    MAINNET_RPC_URL,
    POLYGON_RPC_URL,
    MOONBEAM_RPC_URL,
    DFK_RPC_URL,
    HARMONY_RPC_URL,
    CELO_RPC_URL,
    KAVA_RPC_URL,
    MOONRIVER_RPC_URL,
    BSC_RPC_URL,
    GNOSIS_RPC_URL,
    CORE_RPC_URL,
    LINEA_RPC_URL,
    SCROLL_RPC_URL,
    CONFLUX_RPC_URL,
    ZORA_RPC_URL,
    ARBITRUM_RPC_URL,
)


@dataclass
class Chain:
    name: str
    chain_id: int | None = None
    coin_symbol: str | None = None
    explorer: str | None = None
    eip_1559: bool | None = None
    rpc: str | None = None
    binance_chain_name: str | None = None
    okx_chain_name: str | None = None
    okx_withdrawal_fee: int | None = None
    orbiter_chain_id: int | None = None
    orbiter_dst_chain_code: int | None = None
    lz_chain_id: int | None = None

    def __str__(self) -> str:
        return self.name


EthMainnet = Chain(
    name="ERC20",
    rpc=MAINNET_RPC_URL,
    chain_id=1,
    orbiter_chain_id=1,
    orbiter_dst_chain_code=9001,
    lz_chain_id=101,
    coin_symbol="ETH",
    explorer="https://etherscan.io/",
    okx_chain_name="ERC20",
    okx_withdrawal_fee=0.0016,
    eip_1559=False
)

BSC = Chain(
    name="BSC",
    rpc=BSC_RPC_URL,
    chain_id=56,
    coin_symbol="BNB",
    explorer="https://bscscan.com/",
    lz_chain_id=102,
    eip_1559=False
)

Polygon = Chain(
    name="Polygon",
    rpc=POLYGON_RPC_URL,
    chain_id=137,
    coin_symbol="MATIC",
    explorer="https://polygonscan.com/",
    lz_chain_id=109,
    eip_1559=False
)

Moonbeam = Chain(
    name="Moonbeam",
    rpc=MOONBEAM_RPC_URL,
    chain_id=1284,
    coin_symbol="GLMR",
    explorer="https://moonscan.io/",
    lz_chain_id=126,
    eip_1559=False
)

Arbitrum = Chain(
    name="Arbitrum",
    rpc=ARBITRUM_RPC_URL,
    chain_id=42161,
    coin_symbol="ETH",
    explorer="https://arbiscan.io/",
    lz_chain_id=110,
    eip_1559=False
)

DFK = Chain(
    name="DFK",
    rpc=DFK_RPC_URL,
    chain_id=53935,
    coin_symbol="JEWEL",
    explorer="https://subnets.avax.network/defi-kingdoms/",
    lz_chain_id=115,
    eip_1559=False
)

Harmony = Chain(
    name="Harmony ONE",
    rpc=HARMONY_RPC_URL,
    chain_id=1666600000,
    coin_symbol="ONE",
    explorer="https://explorer.harmony.one/",
    lz_chain_id=116,
    eip_1559=False
)

Celo = Chain(
    name="Celo",
    rpc=CELO_RPC_URL,
    chain_id=42220,
    coin_symbol="CELO",
    explorer="https://celoscan.io/",
    lz_chain_id=125,
    eip_1559=False
)

Moonriver = Chain(
    name="Moonriver",
    rpc=MOONRIVER_RPC_URL,
    chain_id=1285,
    coin_symbol="MOVR",
    explorer="https://moonriver.moonscan.io/",
    lz_chain_id=167,
    eip_1559=False
)

Kava = Chain(
    name="Kava",
    rpc=KAVA_RPC_URL,
    chain_id=2222,
    coin_symbol="KAVA",
    lz_chain_id=177,
    explorer="https://kavascan.com/",
    eip_1559=False
)

Gnosis = Chain(
    name="Gnosis",
    rpc=GNOSIS_RPC_URL,
    chain_id=100,
    coin_symbol="XDAI",
    explorer="https://gnosisscan.io/",
    lz_chain_id=145,
    eip_1559=False
)

CoreDAO = Chain(
    name="Core",
    rpc=CORE_RPC_URL,
    chain_id=1116,
    coin_symbol="CORE",
    explorer="https://scan.coredao.org/",
    lz_chain_id=153,
    eip_1559=False
)

Linea = Chain(
    name="Linea",
    rpc=LINEA_RPC_URL,
    chain_id=59144,
    coin_symbol="ETH",
    explorer="https://lineascan.build/",
    lz_chain_id=183,
    eip_1559=False
)

Base = Chain(
    name="Base",
    rpc=BSC_RPC_URL,
    chain_id=8453,
    coin_symbol="ETH",
    explorer="https://basescan.org/",
    lz_chain_id=184,
    eip_1559=False
)

Scroll = Chain(
    name="Scroll",
    rpc=SCROLL_RPC_URL,
    chain_id=534352,
    coin_symbol="ETH",
    explorer="https://scrollscan.com/",
    lz_chain_id=214,
    eip_1559=False
)

Zora = Chain(
    name="Zora",
    rpc=ZORA_RPC_URL,
    chain_id=7777777,
    coin_symbol="ETH",
    explorer="https://explorer.zora.energy/",
    lz_chain_id=195,
    eip_1559=False
)

Conflux = Chain(
    name="Conflux",
    rpc=CONFLUX_RPC_URL,
    chain_id=1030,
    coin_symbol="CFX",
    lz_chain_id=212,
    explorer="https://www.confluxscan.io/",
    eip_1559=False
)

NAMES_TO_CHAINS = {
    "BSC": BSC,
    "Polygon": Polygon,
    "Moonbeam": Moonbeam,
    "Arbitrum": Arbitrum,
    "DFK": DFK,
    "Harmony": Harmony,
    "Celo": Celo,
    "Moonriver": Moonriver,
    "Kava": Kava,
    "Gnosis": Gnosis,
    "Core": CoreDAO,
    "Linea": Linea,
    "Base": Base,
    "Scroll": Scroll,
    "Zora": Zora,
    "Conflux": Conflux
}


@unique
class ChainEnum(Enum):
    Polygon = Polygon
    Gnosis = Gnosis
    Celo = Celo
    EthMainnet = EthMainnet
