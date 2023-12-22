from eth_abi.packed import encode_packed

from config import TX_DELAY_RANGE
from sdk import Client, logger
from sdk.constants import (
    MERKLY_CHAIN_TO_REFUEL_CONTRACT_ADDRESS,
    MERKLY_REFUEL_ABI,
    RETRIES
)
from sdk.decorators import wait
from ..models.chain import Chain
from ..models.token import ETH_Token
from ..utils import retry_on_fail


class Merkly:
    def __init__(self, client: Client, chain: Chain):
        self.account = client
        self.name = "Merkly"

        if self.account.chain != chain:
            self.account.change_chain(chain=chain)

        self.refuel_address = MERKLY_CHAIN_TO_REFUEL_CONTRACT_ADDRESS[chain.name]
        self.contract = self.account.w3.eth.contract(
            address=self.refuel_address,
            abi=MERKLY_REFUEL_ABI
        )

    @retry_on_fail(tries=RETRIES)
    async def get_bridge_fee_params(self, dst_chain_id: int, value: int):
        data = self.account.w3.to_hex(
            encode_packed(
                ["uint16", "uint", "uint", "address"],
                [2, 250000, value, self.account.address]
            )
        )

        fee = await self.contract.functions.estimateSendFee(dst_chain_id, '0x', data).call()

        return data, int(fee[0] * 1.01)

    @wait(delay_range=TX_DELAY_RANGE)
    async def bridge(self, src_chain: Chain, dst_chain: Chain, amount: float) -> bool:
        logger.info(
            f"[{self.name}] Bridging {amount} {dst_chain.coin_symbol} from {src_chain.name} to {dst_chain.name}")

        balance = ETH_Token.from_wei(await self.account.get_native_balance(chain=src_chain))

        try:
            value = ETH_Token.to_wei(amount)
            adapter_params, fee = await self.get_bridge_fee_params(dst_chain.lz_chain_id, value=value)

            amount = ETH_Token.from_wei(fee)
            if balance < amount:
                logger.error(f"[{self.name}] Insufficient balance to bridge: {balance} < {amount}")
                return False

            data = self.contract.encodeABI('bridgeGas', args=(
                dst_chain.lz_chain_id,
                self.account.address,
                adapter_params
            ))

            tx_hash = await self.account.send_transaction(to=self.refuel_address, data=data, value=fee)
            if tx_hash:
                return await self.account.verify_tx(tx_hash=tx_hash)
        except Exception as e:
            if "dstNativeAmt too large" in str(e):
                logger.error(
                    f"[{self.name}] Amount to bridge exceeds max possible value for {src_chain.name}-{dst_chain.name}"
                )
            else:
                logger.error(f"[{self.name}] Exception in bridge function: {e}")
            return False
