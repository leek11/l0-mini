from typing import Dict

from config import GAS_THRESHOLD, GAS_DELAY_RANGE, INCH_API_KEY
from sdk import Client, logger
from sdk.constants import INCH_BASE_URL, INCH_ROUTER_CONTRACT_ADDRESS, MAX_LEFT_TOKEN_PERCENTAGE
from sdk.dapps import Dapp
from sdk.decorators import gas_delay
from sdk.models.token import Token
from sdk.models.chain import Polygon


class Inch(Dapp):
    def __init__(self, client: Client) -> None:
        self.client: Client = client
        self.base_url: str = INCH_BASE_URL
        self.request_headers: Dict[str, str] = {
            "Authorization": INCH_API_KEY,
            "accept": "application/json",
        }

    async def _get_swap_data(
        self, amount: int, token_in: Token, token_out: Token, slippage: int | float
    ):
        data = await self.client.send_get_request(
            url=self.base_url.format(
                self.client.chain.chain_id,
                token_in.chain_to_contract_mapping[self.client.chain.name],
                token_out.chain_to_contract_mapping[self.client.chain.name],
                amount,  # amount in WEI
                self.client.address,
                slippage,
            ),
            headers=self.request_headers,
        )

        if not data:
            return None

        return data["tx"]["data"]

    @gas_delay(gas_threshold=GAS_THRESHOLD, delay_range=GAS_DELAY_RANGE)
    async def swap(
        self,
        token_in: Token,
        token_out: Token,
        slippage: float,
        amount: int | None = None,
    ):
        if self.client.chain != Polygon:
            self.client.change_chain(chain=Polygon)

        if amount is None:
            amount = await self.client.get_token_balance(token=token_in)
            if not amount:
                return False
            amount = int(amount * (1 - MAX_LEFT_TOKEN_PERCENTAGE))

        if await self.client.approve(
            spender=INCH_ROUTER_CONTRACT_ADDRESS, token=token_in, value=amount
        ):
            data = await self._get_swap_data(
                amount=amount, token_in=token_in, token_out=token_out, slippage=slippage
            )
            logger.info(
                f"[1INCH] Swapping {token_in.from_wei(value=amount)} {token_in.symbol} to {token_out.symbol}"
            )
            tx_hash = await self.client.send_transaction(
                to=INCH_ROUTER_CONTRACT_ADDRESS, data=data
            )

            if tx_hash:
                return await self.client.verify_tx(tx_hash=tx_hash)

            return False
        return False
