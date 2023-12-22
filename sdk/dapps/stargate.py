from eth_abi.packed import encode_packed

from config import TX_DELAY_RANGE, TOKEN_USE_PERCENTAGE, ROUND_TO, USE_SWAP_BEFORE_BRIDGE
from sdk import Client, logger
from sdk.constants import STG_TOKEN_CONTRACT_ADDRESS, ZERO_ADDRESS, STG_TOKEN_ABI
from sdk.dapps import ZeroX
from sdk.decorators import wait
from sdk.models.chain import Chain
from sdk.models.chain import Polygon, Kava
from sdk.models.token import ETH_Token, MATIC_Token, STG_Token


class Stargate:
    def __init__(self, client: Client, chain: Chain = Polygon):
        self.account = client
        self.name = "Stargate"

        if self.account.chain != chain:
            self.account.change_chain(chain=chain)

        self.contract = self.account.w3.eth.contract(
            abi=STG_TOKEN_ABI,
            address=STG_TOKEN_CONTRACT_ADDRESS
        )

    async def get_bridge_fee_params(self):
        data = self.account.w3.to_hex(encode_packed(["uint16", "uint"], [1, 85000]))
        fee = await self.contract.functions.estimateSendTokensFee(177, False, data).call()
        return data, int(fee[0] * 1.01)

    @wait(delay_range=TX_DELAY_RANGE)
    async def bridge(self, amount: float):
        try:
            value = ETH_Token.to_wei(amount)

            adapter_params, fee = await self.get_bridge_fee_params()

            data = self.contract.encodeABI('sendTokens', args=(
                Kava.lz_chain_id,
                self.account.address,
                value,
                ZERO_ADDRESS,
                adapter_params
            ))

            logger.info(f"[{self.name}] Bridging {amount} STG from {Polygon.name} to {Kava.name}")
            tx_hash = await self.account.send_transaction(to=STG_TOKEN_CONTRACT_ADDRESS, data=data, value=fee)
            if tx_hash:
                if await self.account.verify_tx(tx_hash=tx_hash):
                    return True
            return False
        except Exception as ex:
            logger.error(f"[{self.name}] Error while bridging: {ex}")

    async def swap_and_bridge(self, amount: float):
        zerox = ZeroX(client=self.account, chain=self.account.chain)

        stg_balance = await self.account.get_token_balance(STG_Token)

        if stg_balance == 0 or USE_SWAP_BEFORE_BRIDGE:
            if not await zerox.swap(from_token=MATIC_Token, to_token=STG_Token, amount=amount):
                logger.error(f"[{self.name}] Aborting")
                return False

            stg_balance = await self.account.get_token_balance(STG_Token)

        if USE_SWAP_BEFORE_BRIDGE:
            amount_to_bridge = round(stg_balance * 0.999, ROUND_TO)
        else:
            amount_to_bridge = round(stg_balance * TOKEN_USE_PERCENTAGE, ROUND_TO)

        return await self.bridge(amount=amount_to_bridge)
