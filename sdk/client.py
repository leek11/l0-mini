import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp
from aiohttp_proxy import ProxyConnector
from web3 import AsyncWeb3, Web3
from web3.contract import Contract

from config import AFTER_APPROVE_DELAY_RANGE, PROXY_CHANGE_IP_URL
from sdk import logger
from sdk.constants import GAS_MULTIPLIER, RETRIES, APPROVE_VALUE_RANGE, CG_FETCH_TOKEN_PRICE_URL, \
    MIN_DELIVERED_VALUE_PERCENTAGE, TRANSFER_TX_SIMULATION_VALUE, MAX_LEFT_TOKEN_PERCENTAGE
from sdk.models.chain import Chain, EthMainnet
from sdk.models.token import Token, ETH_Token
from sdk.utils import retry_on_fail, sleep_pause


class Client:
    def __init__(
        self, private_key: str, proxy: str = None, chain: Chain = EthMainnet
    ) -> None:
        self.private_key = private_key
        self.chain = chain
        self.proxy = proxy
        self.w3 = self.init_web3(chain=chain)
        self.address = AsyncWeb3.to_checksum_address(
            value=self.w3.eth.account.from_key(private_key=private_key).address
        )
        self.tokens = [ETH_Token]

    def __str__(self) -> str:
        return self.address

    def __repr__(self) -> str:
        return self.address

    def init_web3(self, chain: Chain = None):
        if self.proxy:
            request_kwargs = {"proxy": f"http://{self.proxy}"}
        else:
            request_kwargs = {}

        try:
            if not chain.rpc:
                raise NoRPCEndpointSpecifiedError

            return AsyncWeb3(
                AsyncWeb3.AsyncHTTPProvider(
                    endpoint_uri=chain.rpc, request_kwargs=request_kwargs
                )
            )

        except NoRPCEndpointSpecifiedError as e:
            logger.error(e)
            exit()

    def change_chain(self, chain: Chain) -> None:
        self.chain = chain
        self.w3 = self.init_web3(chain=chain)

    async def send_transaction(
        self,
        to: str,
        data: str = None,
        from_: str = None,
        value: int = None,
    ):
        tx_params = await self._get_tx_params(
            to=to, data=data, from_=from_, value=value
        )

        tx_params["gas"] = await self._get_gas_estimate(tx_params=tx_params)

        sign = self.w3.eth.account.sign_transaction(tx_params, self.private_key)

        try:
            return await self.w3.eth.send_raw_transaction(sign.rawTransaction)

        except Exception as e:
            logger.error(f"Error while sending transaction: {e}")

    async def _get_gas_estimate(
        self, tx_params: dict, gas_multiplier: float = GAS_MULTIPLIER
    ):
        try:
            return int(await self.w3.eth.estimate_gas(tx_params) * gas_multiplier)

        except Exception as e:
            logger.exception(f"Transaction estimate failed: {e}")
            return None

    async def _get_tx_params(
        self, to: str, data: str = None, from_: str = None, value: int = None
    ) -> Dict:
        if not from_:
            from_ = self.address

        tx_params = {
            "chainId": await self.w3.eth.chain_id,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "from": self.w3.to_checksum_address(from_),
            "to": self.w3.to_checksum_address(to),
        }

        if data:
            tx_params["data"] = data

        if value:
            tx_params["value"] = value

        if self.chain.chain_id == 56:
            tx_params["gasPrice"] = Web3.to_wei(1.5, "gwei")
        else:
            tx_params["gasPrice"] = await self.w3.eth.gas_price

        return tx_params

    async def verify_tx(self, tx_hash: str) -> bool:
        try:
            response = await self.w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=600
            )

            if "status" in response and response["status"] == 1:
                logger.success(
                    f"Transaction was successful: {self.chain.explorer}tx/{self.w3.to_hex(tx_hash)}"
                )
                return True
            else:
                logger.error(
                    f"Transaction failed: {self.chain.explorer}tx/{self.w3.to_hex(tx_hash)}"
                )
                return False

        except Exception as e:
            logger.error(f"Unexpected error in verify_tx function: {e}")
            return False

    @retry_on_fail(tries=RETRIES)
    async def get_allowance(
        self, token_contract: Contract, spender: str, owner: str = None
    ) -> float:
        if not owner:
            owner = self.address

        return await token_contract.functions.allowance(owner, spender).call()

    @retry_on_fail(tries=RETRIES)
    async def get_native_balance(self, chain: Chain):
        w3 = self.init_web3(chain=chain)

        try:
            return await w3.eth.get_balance(self.address)
        except Exception as e:
            logger.exception(f"[CLIENT] Could not get balance of: {self.address}: {e}")
            return None

    @retry_on_fail(tries=RETRIES)
    async def approve(
        self, spender: str, token, value: int = None, ignore_allowance: bool = False
    ) -> bool:
        if APPROVE_VALUE_RANGE:
            value = token.to_wei(value=random.randint(*APPROVE_VALUE_RANGE))

        if token.is_native_token_mapping[self.chain.name]:
            return True

        token_contract = self.w3.eth.contract(
            address=token.chain_to_contract_mapping[self.chain.name], abi=token.abi
        )
        allowance = await self.get_allowance(
            token_contract=token_contract, spender=spender
        )

        if self.chain.chain_id == 56 and token.symbol == "USDT":
            decimals = 18
        else:
            decimals = token.decimals

        if not ignore_allowance:
            if allowance >= value:
                logger.warning(
                    f"Allowance is greater than approve value: {allowance / pow(10, decimals)} >= {value / pow(10, decimals)}"
                )
                return True

        logger.info(
            f"Approving {value / pow(10, decimals)} {token.symbol} for spender: {spender}"
        )

        response = token_contract.encodeABI("approve", args=(spender, value))
        tx_hash = await self.send_transaction(token_contract.address, data=response)

        if await self.verify_tx(tx_hash=tx_hash):
            await sleep_pause(delay_range=AFTER_APPROVE_DELAY_RANGE)
            return True

        logger.error("Error in approve transaction")
        return False

    @retry_on_fail(tries=RETRIES)
    async def get_token_balance(self, token):
        if token.is_native_token_mapping[self.chain.name]:
            balance = await self.get_native_balance()

            if not balance:
                return None

            return float(self.w3.from_wei(balance, "ether"))

        token_contract = self.w3.eth.contract(
            address=token.chain_to_contract_mapping[self.chain.name], abi=token.abi
        )

        try:
            balance = await token_contract.functions.balanceOf(self.address).call()
        except Exception as e:
            logger.error(f"Exception in get_token_balance function: {e}")
            return None

        if token.symbol == "USDT" and self.chain.chain_id == 56:
            balance_from_wei = balance / 10 ** 18
        else:
            balance_from_wei = token.from_wei(value=balance)

        return balance_from_wei

    @retry_on_fail(tries=RETRIES)
    async def get_token_balance_batch(self, token_list: List[Token] = None):
        token_balances = {}

        if not token_list:
            token_list = self.tokens

        tasks = []

        for token in token_list:
            if token == ETH_Token:
                tasks.append(self.get_native_balance())

            else:
                tasks.append(self.get_token_balance(token=token))

        results = await asyncio.gather(*tasks)

        for token, balance in zip(token_list, results):
            if token == ETH_Token:
                balance_in_ether = float(self.w3.from_wei(balance, "ether"))
                token_balances[token] = balance_in_ether
            else:
                token_balances[token] = balance

        return token_balances

    @retry_on_fail(tries=RETRIES)
    async def send_get_request(self, url: str, use_proxy: bool = True):
        if not use_proxy:
            connector = None
        else:
            connector = self.get_proxy_connector()

        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url=url, timeout=100) as response:
                    response.raise_for_status()
                    json_data = await response.json()
                    return json_data

        except aiohttp.ClientResponseError as e:
            logger.error(f"Recieved non-200 response: {e}")
            return None

        except aiohttp.ClientConnectionError as e:
            logger.error(f"Connection Error: {e}")
            return None

        except aiohttp.InvalidURL as e:
            logger.error(f"Wrong URL format")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None

    @retry_on_fail(tries=RETRIES)
    async def send_post_request(self, url: str, data: dict):
        try:
            async with aiohttp.ClientSession(
                connector=self.get_proxy_connector()
            ) as session:
                async with session.post(url=url, json=data, timeout=100) as response:
                    response.raise_for_status()
                    return await response.json()

        except aiohttp.ClientConnectionError as e:
            logger.error(f"Connection Error: {e}")
            return None

        except aiohttp.ClientResponseError as e:
            logger.error(f"Recieved non-200 response: {e}")
            return None

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None

    def get_proxy_connector(self):
        if self.proxy is not None:
            proxy_url = f"http://{self.proxy}"
            return ProxyConnector.from_url(url=proxy_url)
        else:
            return None

    @retry_on_fail(tries=RETRIES)
    async def fetch_token_price_batch(self, token_list: List[Token] = None):
        if not token_list:
            token_list = self.tokens

        coingecko_ids = [token.coingecko_id for token in token_list]
        coingecko_ids_string = ",".join(coingecko_ids)

        token_prices = {}

        url = CG_FETCH_TOKEN_PRICE_URL.format(coingecko_ids_string)
        response = await self.send_get_request(url=url)

        for token in token_list:
            coingecko_id = token.coingecko_id
            if coingecko_id in response and "usd" in response[coingecko_id]:
                token_prices[token] = response[coingecko_id]["usd"]

        return token_prices

    @retry_on_fail(tries=RETRIES)
    async def get_tokens_balance_to_usd_batch(
        self, tokens_to_prices: Dict, token_list: List[Token] = None
    ):
        if not token_list:
            token_list = self.tokens

        token_balances = await self.get_token_balance_batch(token_list)

        token_to_usd_value = {}

        for token, balance in token_balances.items():
            price = tokens_to_prices.get(token)

            if price is not None and balance is not None:
                usd_value = float(balance) * price
                token_to_usd_value[token] = usd_value

        return token_to_usd_value

    @retry_on_fail(tries=RETRIES)
    async def get_token_with_largest_balance(self):
        tokens_prices = await self.fetch_token_price_batch()
        client_tokens_values = await self.get_client_tokens_values(
            tokens_prices=tokens_prices
        )

        if not client_tokens_values:
            return None

        # get a token from client_tokens_values with a biggest value
        max_token = max(
            client_tokens_values, key=lambda token: client_tokens_values[token]
        )
        token_balance = await self.get_token_balance(token=max_token)

        return max_token, token_balance

    def get_deadline(self, seconds: int = 1800):
        return int(datetime.now(timezone.utc).timestamp()) + seconds

    @retry_on_fail(tries=RETRIES)
    async def get_client_tokens_values(
        self, tokens_prices: Dict[str, float], token_list: List = None
    ):
        if not token_list:
            token_list = self.tokens

        try:
            token_balances = await self.get_token_balance_batch(token_list=token_list)
            tokens_values = {}

            for token, balance in token_balances.items():
                if token in tokens_prices:
                    price = tokens_prices[token]
                    value = balance * price
                    tokens_values[token] = value

            return tokens_values

        except Exception as e:
            logger.error(f"Failed to fetch client's token's values: {e}")
            return None

    @staticmethod
    def calculate_tokens_values_sum(tokens_to_values: Dict[Token, float]):
        return sum(tokens_to_values.values())

    async def wait_for_tokens_recieved_on_wallet(
            self,
            initial_balance: int,
            chain: Chain,
            token,
            checkup_sleep_time_range: int,
            attempts: int | None = None,
    ) -> bool:
        if not attempts:
            attempts = True

        if self.chain != chain:
            self.change_chain(chain=chain)

        logger.info(f"[CLIENT] Waiting for funds on {chain.name}")

        while attempts:
            final_balance = await self.get_token_balance(token=token)
            if final_balance > initial_balance:
                logger.success(
                    f"[CLIENT] Funds on {chain.name} recieved: Final balance: {self.w3.from_wei(final_balance, 'ether')}, initial balance: {self.w3.from_wei(initial_balance, 'ether')}"
                )
                return True
            if attempts is not True:
                attempts -= 1
            await sleep_pause(
                delay_range=checkup_sleep_time_range,
                enable_message=False,
                enable_pr_bar=False,
            )
        logger.error(f"[CLIENT] Funds not recieved on {chain.name}")
        return False

    async def send_all_native_balance(
        self, to: str, chain: Chain, keep_token_amount: int = 0
    ):
        if self.chain != chain:
            self.change_chain(chain=chain)

        tx_params = await self._get_tx_params(to=to, value=TRANSFER_TX_SIMULATION_VALUE)
        gas = await self._get_gas_estimate(tx_params=tx_params)
        if not gas:
            return False

        gas_fee = int((gas * tx_params["gasPrice"]))
        balance = await self.get_native_balance(chain=chain)
        max_send_value = int((balance - gas_fee) - ETH_Token.to_wei(keep_token_amount))

        logger.info(
            f"[CLIENT] Sending {self.w3.from_wei(max_send_value, 'ether')} to {to}"
        )
        tx_hash = await self.send_transaction(to=to, value=max_send_value)
        if tx_hash:
            return await self.verify_tx(tx_hash=tx_hash)
        return False

    async def wait_for_gas(self, desired_gas, delay_range) -> bool:
        while await self.w3.eth.gas_price > desired_gas:
            await sleep_pause(
                delay_range=delay_range, enable_message=False, enable_pr_bar=False
            )
        return True

    async def send_erc20(
            self, token, recipient: str, amount: int | None = None
    ) -> bool:
        if amount is None:
            amount = await self.get_token_balance(token=token)
            if amount is None:
                return False
            amount = int(amount * (1 - MAX_LEFT_TOKEN_PERCENTAGE))

        recipient = AsyncWeb3.to_checksum_address(value=recipient)
        token_contract_address = token.chain_to_contract_mapping[self.chain.name]
        contract = self.w3.eth.contract(address=token_contract_address, abi=token.abi)
        data = contract.encodeABI(fn_name="transfer", args=(recipient, amount))

        logger.info(f"[CLIENT] Sending {token.from_wei(amount)} to {recipient}")
        tx_hash = await self.send_transaction(to=token_contract_address, data=data)

        if not tx_hash:
            return False

        return await self.verify_tx(tx_hash=tx_hash)

    async def wait_for_block_confirmations(
            self,
            sent_block: int,
            confirmation_blocks: int,
            sleep_time: list[int],
            extra_blocks: int,
    ) -> bool:
        logger.info(
            f"[CLIENT] Waiting for {confirmation_blocks} blockchain confirmations"
        )
        while True:
            try:
                current_block = await self.w3.eth.get_block_number()
                if current_block - sent_block > confirmation_blocks + extra_blocks:
                    logger.success(
                        f"[CLIENT] Successfully reached {confirmation_blocks} confirmations"
                    )
                    return True
                await sleep_pause(
                    delay_range=sleep_time, enable_message=False, enable_pr_bar=False
                )
            except Exception as e:
                logger.error(f"[CLIENT] Failed to get current block number {e}")

class NoRPCEndpointSpecifiedError(Exception):
    def __init__(
        self,
        message: str = "No RPC endpoint specified. Specify one in config.py file",
        *args: object,
    ) -> None:
        self.message = message
        super().__init__(self.message, *args)