from __future__ import annotations

from typing import Dict

from ccxt.async_support import okx
from loguru import logger

from sdk import Client
from sdk.constants import (
    OKX_AFTER_ERROR_SLEEP_TIME,
    OKX_ON_FAIL_RETRY_COUNT,
    OKX_WAIT_FOR_WITHDRAWAL_FINAL_STATUS_ATTEMPTS,
    OKX_WAIT_FOR_WITHDRAWAL_FINAL_STATUS_MAX_WAIT_TIME,
    OKX_WAIT_FOR_WITHDRAWAL_RECEIVED_ATTEMPTS,
    OKX_WAIT_FOR_WITHDRAWAL_RECIEVED_SLEEP_TIME,
    RETRIES,
    OKX_WITHDRAWAL_CHAIN_TO_DATA
)
from sdk.models.chain import Polygon, Chain
from sdk.models.token import USDC_Token, Token
from sdk.utils import retry_on_fail, sleep_pause


class OKX:
    def __init__(self, api_key: str, secret: str, password: str, client: Client) -> None:
        self.client = client
        self._api_key = api_key
        self._secret = secret
        self._password = password
        self.exchange = okx(config=self._get_config())

    def _get_config(self) -> Dict:
        return {
            "apiKey": self._api_key,
            "secret": self._secret,
            "password": self._password,
            "enableRateLimit": True
        }

    @retry_on_fail(tries=RETRIES)
    async def withdraw(
            self,
            amount_to_withdraw: float,
            token: Token | str = USDC_Token,
            chain: Chain = Polygon,
            retry_count=0
    ) -> str:
        async with self.exchange as exchange:
            try:
                if type(token) is str:
                    token_symbol = token
                    initial_client_balance = await self.client.get_native_balance(chain=chain) / 10 ** 18
                else:
                    token_symbol = token.symbol
                    initial_client_balance = await self.client.get_token_balance(token=token)

                logger.info(f"[OKX] Trying to withdraw {amount_to_withdraw} {token_symbol} to {self.client.address}")

                okx_chain_name = "CELO" if chain.chain_id == 42220 else chain.name

                data = await exchange.withdraw(
                    token_symbol,
                    amount_to_withdraw,
                    self.client.address,
                    params={
                        "toAddress": self.client.address,
                        "chainName": f"{token_symbol}-{okx_chain_name}",
                        "dest": 4,
                        "fee": OKX_WITHDRAWAL_CHAIN_TO_DATA[chain.name]["fee"],
                        "pwd": "-",
                        "amt": amount_to_withdraw,
                        "network": okx_chain_name,
                    },
                )
                withdrawal_id = data["info"]["wdId"]

            except Exception as e:
                error_message = str(e)

                if "Withdrawal address is not allowlisted for verification exemption" in error_message:
                    logger.error(f"[OKX] Address {self.client.address} is not allowlisted")
                    return False
                elif "Insufficient balance" in error_message:
                    logger.error(f"[OKX] Insufficient funds for withdrawal")
                    return False
                else:
                    logger.error(f"[OKX] Error while withdrawing {amount_to_withdraw} {token_symbol}: {error_message}")

                if retry_count < OKX_ON_FAIL_RETRY_COUNT:
                    logger.info(f"[OKX] Withdrawal unsuccessful, waiting for another try")
                    await sleep_pause(delay_range=OKX_AFTER_ERROR_SLEEP_TIME, enable_message=False)
                    return await self.withdraw(
                        retry_count=retry_count + 1,
                        amount_to_withdraw=amount_to_withdraw,
                        token=token,
                        chain=chain
                    )
                else:
                    logger.error(f"[OKX] Withdraw failed: {str(e)}")
                    return False

            tokens_delivered = await self._watch_for_delivery(
                initial_client_balance=initial_client_balance,
                withdrawal_id=withdrawal_id,
                token=token,
                chain=chain
            )

            if tokens_delivered:
                logger.success(f"[OKX] Successfully withdrew {amount_to_withdraw} {token_symbol}")
                return True
            return False

    async def _wait_for_withdrawal_final_status(self, withdrawal_id: str) -> bool:
        attempt_count = 1
        max_wait_time = OKX_WAIT_FOR_WITHDRAWAL_FINAL_STATUS_MAX_WAIT_TIME
        max_attempts = OKX_WAIT_FOR_WITHDRAWAL_FINAL_STATUS_ATTEMPTS

        logger.info(f"[OKX] Waiting for withdrawal final status")
        while attempt_count <= max_attempts:
            async with self.exchange as exchange:
                try:
                    status = await exchange.private_get_asset_deposit_withdraw_status(params={"wdId": withdrawal_id})

                    if "Cancelation complete" in status["data"][0]["state"]:
                        raise WithdrawalCancelledError
                    if "Withdrawal complete" not in status["data"][0]["state"]:
                        attempt_count += 1
                        await sleep_pause(delay_range=max_wait_time, enable_message=False, enable_pr_bar=False)
                    else:
                        logger.info("[OKX] Withdrawal sent from OKX")
                        return True

                except WithdrawalCancelledError as e:
                    logger.error(f"[OKX] {e}")
                    return False
                except Exception as e:
                    logger.error(f"[OKX] Error in wait_for_withdrawal_final_status function: {e}")
                    return False
        logger.error("[OKX] Max attempts reached. Withdrawal status not finalized.")
        return False

    async def _watch_for_delivery(self, withdrawal_id: str, initial_client_balance: float, token, chain) -> bool:
        withdrawal_completed_status = await self._wait_for_withdrawal_final_status(withdrawal_id)

        if not withdrawal_completed_status:
            logger.error(f"[OKX] Withdrawal could not be completed")
            return False

        withdrawal_received_status = await self._wait_for_withdrawal_received(
            initial_client_balance,
            token=token,
            chain=chain
        )

        if not withdrawal_received_status:
            logger.error(f"[OKX] Withdrawal could not be recieved")
            return False

        return withdrawal_completed_status and withdrawal_received_status

    async def _wait_for_withdrawal_received(self, initial_balance: float, token: Token | str, chain: Chain) -> bool:
        attempt_count = 0
        max_attempts = OKX_WAIT_FOR_WITHDRAWAL_RECEIVED_ATTEMPTS
        max_wait_time = OKX_WAIT_FOR_WITHDRAWAL_RECIEVED_SLEEP_TIME

        try:
            logger.info(f"[OKX] Waiting for funds on the wallet")
            while attempt_count < max_attempts:
                if type(token) is str:
                    final_balance = await self.client.get_native_balance(chain=chain) / 10 ** 18
                else:
                    final_balance = await self.client.get_token_balance(token=token)

                if final_balance > initial_balance:
                    return True

                attempt_count += 1
                await sleep_pause(max_wait_time, enable_message=False)
            raise WithdrawalNotReceivedError

        except WithdrawalNotReceivedError as e:
            logger.error(f"[OKX] {e}")
        except Exception as e:
            logger.error(f"[OKX] {e}")


class WithdrawalCancelledError(Exception):
    def __init__(self, message: str = "Withdrawal cancelled", *args: object) -> None:
        self.message = message
        super().__init__(self.message, *args)


class WithdrawalNotReceivedError(Exception):
    def __init__(self, message: str = "Withdrawal not recieved", *args: object) -> None:
        self.message = message
        super().__init__(self.message, *args)
