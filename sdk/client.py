from __future__ import annotations

import random
from typing import Dict

from aiohttp_proxy import ProxyConnector
from web3 import AsyncWeb3, Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware

from config import AFTER_APPROVE_DELAY_RANGE
from sdk import logger
from sdk.constants import GAS_MULTIPLIER, RETRIES, APPROVE_VALUE_RANGE
from sdk.models.chain import Chain, EthMainnet
from sdk.models.token import ETH_Token
from sdk.utils import retry_on_fail, sleep_pause


class Client:
    def __init__(self, private_key: str, proxy: str = None, chain: Chain = EthMainnet) -> None:
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
        request_kwargs = {"proxy": f"http://{self.proxy}"} if self.proxy else {}

        try:
            if not chain.rpc:
                raise NoRPCEndpointSpecifiedError

            return AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(endpoint_uri=chain.rpc, request_kwargs=request_kwargs))

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
        elif self.chain.eip_1559:
            w3 = Web3(provider=Web3.HTTPProvider(endpoint_uri=self.chain.rpc))
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            last_block = w3.eth.get_block("latest")
            max_priority_fee_per_gas = Client.get_max_priority_fee_per_gas(w3=w3, block=last_block)
            base_fee = int(last_block["baseFeePerGas"] * GAS_MULTIPLIER)
            max_fee_per_gas = base_fee + max_priority_fee_per_gas
            tx_params["maxPriorityFeePerGas"] = max_priority_fee_per_gas
            tx_params["maxFeePerGas"] = max_fee_per_gas
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

    @staticmethod
    def get_max_priority_fee_per_gas(w3: Web3, block: dict) -> int:
        block_number = block["number"]
        latest_block_transaction_count = w3.eth.get_block_transaction_count(block_number)
        max_priority_fee_per_gas_list = []
        for i in range(latest_block_transaction_count):
            try:
                transaction = w3.eth.get_transaction_by_block(block_number, i)
                if "maxPriorityFeePerGas" in transaction:
                    max_priority_fee_per_gas_list.append(transaction["maxPriorityFeePerGas"])
            except Exception:
                continue

        if not max_priority_fee_per_gas_list:
            max_priority_fee_per_gas = w3.eth.max_priority_fee
        else:
            max_priority_fee_per_gas_list.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_list[len(max_priority_fee_per_gas_list) // 2]
        return max_priority_fee_per_gas

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

        token_contract = self.w3.eth.contract(address=token.chain_to_contract_mapping[self.chain.name], abi=token.abi)
        allowance = await self.get_allowance(token_contract=token_contract, spender=spender)

        if self.chain.chain_id == 56 and token.symbol == "USDT":
            decimals = 18
        else:
            decimals = token.decimals

        if not ignore_allowance:
            if allowance >= value:
                logger.warning(
                    f"Allowance is greater than approve value: {allowance / pow(10, decimals)} >= {value / pow(10, decimals)}")
                return True

        logger.info(f"Approving {value / pow(10, decimals)} {token.symbol} for spender: {spender}")

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

    def get_proxy_connector(self):
        if self.proxy is not None:
            proxy_url = f"http://{self.proxy}"
            return ProxyConnector.from_url(url=proxy_url)
        else:
            return None


class NoRPCEndpointSpecifiedError(Exception):
    def __init__(
            self,
            message: str = "No RPC endpoint specified. Specify one in config.py file",
            *args: object,
    ) -> None:
        self.message = message
        super().__init__(self.message, *args)
