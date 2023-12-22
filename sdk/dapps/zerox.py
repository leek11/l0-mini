import asyncio

import aiohttp
from web3 import Web3

from config import ZEROX_API_KEY, MAX_SLIPPAGE, TX_DELAY_RANGE
from sdk.client import Client
from sdk.decorators import wait
from sdk.logger import logger
from sdk.models.chain import Chain
from sdk.models.token import Token


class ZeroX:
    def __init__(self, client: Client, chain: Chain):
        self.account = client
        self.name = "0x"

        if self.account.chain != chain:
            self.account.change_chain(chain)

    async def get_0x_quote(self, value, from_token: Token, to_token: Token):
        from_token = from_token.chain_to_contract_mapping[self.account.chain.name]
        to_token = to_token.chain_to_contract_mapping[self.account.chain.name]

        url_chains = {
            'ethereum': '',
            'bsc': 'bsc.',
            'arbitrum': 'arbitrum.',
            'optimism': 'optimism.',
            'polygon': 'polygon.',
            'fantom': 'fantom.',
            'avalanche': 'avalanche.',
            'celo': 'celo.',
        }

        url = f'https://{url_chains[self.account.chain.name.lower()]}' \
              f'api.0x.org/swap/v1/quote?' \
              f'buyToken={to_token}' \
              f'&sellToken={from_token}' \
              f'&sellAmount={value}' \
              f'&slippagePercentage={MAX_SLIPPAGE / 100}'

        headers = {'0x-api-key': ZEROX_API_KEY}

        try:
            if not self.account.proxy:
                connector = None
            else:
                connector = self.account.get_proxy_connector()
            max_attempts = 10

            for attempt in range(max_attempts):
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result
                        logger.info(f'Attempt to get a response {attempt + 1}/{max_attempts}')
                        await asyncio.sleep(1)
            logger.error("Couldn't get a response")
            return False
        except Exception as ex:
            logger.error(f"[{self.name}] Failed to fetch quote: {ex}")
            return False

    @wait(delay_range=TX_DELAY_RANGE)
    async def swap(self, from_token: Token, to_token: Token, amount: float = None):
        try:
            if ZEROX_API_KEY == "":
                logger.error(f"[{self.name}] No API key provided")
                return False

            logger.info(
                f"[{self.name}] Swapping {amount} {from_token.symbol} -> {to_token.symbol} on {self.account.chain.name}"
            )

            if not amount:
                amount = await self.account.get_token_balance(from_token)

            value = from_token.to_wei(value=amount)
            json_data = await self.get_0x_quote(from_token=from_token, to_token=to_token, value=value)
            if json_data is False:
                return False

            spender = json_data['allowanceTarget']

            if not await self.account.approve(spender=spender, token=from_token, value=from_token.to_wei(value=value)):
                return False

            tx = await self.account.send_transaction(
                to=Web3.to_checksum_address(json_data["to"]),
                data=json_data["data"],
                value=int(json_data["value"])
            )

            if tx:
                if await self.account.verify_tx(tx_hash=tx):
                    return True
            return False

        except Exception as ex:
            logger.error(f"[{self.name}] Error occurred: {ex}")
