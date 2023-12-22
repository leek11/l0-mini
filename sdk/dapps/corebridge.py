from __future__ import annotations

from config import TX_DELAY_RANGE, USE_SWAP_BEFORE_BRIDGE, ROUND_TO, TOKEN_USE_PERCENTAGE
from sdk import Client, logger
from sdk.constants import CORE_BRIDGE_CONTRACT_ADDRESS, CORE_BRIDGE_ABI
from sdk.dapps import ZeroX
from sdk.decorators import wait
from sdk.models.chain import Chain, BSC
from sdk.models.token import USDT_Token, BNB_Token


class CoreBridge:
    def __init__(self, client: Client, chain: Chain = BSC):
        self.name = "CoreBridge"
        self.account = client

        if self.account.chain != chain:
            self.account.change_chain(chain)

        self.bridge_contract = self.account.w3.eth.contract(
            abi=CORE_BRIDGE_ABI,
            address=CORE_BRIDGE_CONTRACT_ADDRESS
        )

    @wait(delay_range=TX_DELAY_RANGE)
    async def bridge(self, amount: float | None = None):
        try:
            if amount is None:
                amount = (await self.account.get_token_balance(USDT_Token) * (1 - 0.01)) / 10 ** 12
            value = int(amount * 10 ** 18)

            if not await self.account.approve(spender=CORE_BRIDGE_CONTRACT_ADDRESS, token=USDT_Token, value=value):
                logger.error(f"[{self.name}] Failed to approve.")
                return False

            logger.info(f'[{self.name}] Bridging {amount} USDT from BSC to Core')

            data_args = (
                USDT_Token.chain_to_contract_mapping["BSC"],
                value,
                self.account.address,
                [self.account.address, '0x0000000000000000000000000000000000000000'],
                '0x'
            )

            fee_args = (True, '0x')
            data = self.bridge_contract.encodeABI('bridge', args=data_args)

            native_fee: list = await self.bridge_contract.functions.estimateBridgeFee(*fee_args).call()
            tx = await self.account.send_transaction(to=CORE_BRIDGE_CONTRACT_ADDRESS, data=data, value=native_fee[0])
            if tx:
                return await self.account.verify_tx(tx_hash=tx)
            return False
        except Exception as ex:
            logger.error(f"[{self.name}] Error while bridging: {ex}")

    async def swap_and_bridge(self, amount: float):
        zerox = ZeroX(client=self.account, chain=self.account.chain)

        usdt_balance = await self.account.get_token_balance(USDT_Token)

        if usdt_balance == 0 or USE_SWAP_BEFORE_BRIDGE:
            if not await zerox.swap(from_token=BNB_Token, to_token=USDT_Token, amount=amount):
                logger.error(f"[{self.name}] Aborting")
                return False

            usdt_balance = await self.account.get_token_balance(USDT_Token)

        if USE_SWAP_BEFORE_BRIDGE:
            amount_to_bridge = round(usdt_balance * 0.999, ROUND_TO)
        else:
            amount_to_bridge = round(usdt_balance * TOKEN_USE_PERCENTAGE, ROUND_TO)

        return await self.bridge(amount=amount_to_bridge)
