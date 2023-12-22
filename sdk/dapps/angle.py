from typing import Dict, List, Tuple

from eth_abi.packed import encode_packed
from eth_account.messages import encode_structured_data, SignableMessage
from web3.constants import ADDRESS_ZERO
from web3.contract import Contract

from config import AFTER_APPROVE_DELAY_RANGE, GAS_THRESHOLD, GAS_DELAY_RANGE, REQUEST_SLEEP_TIME_RANGE, TX_DELAY_RANGE
from sdk import Client, logger
from sdk.constants import ANGLE_BASE_URL, RETRIES, AGEUR_CONTRACT_NAME, AGEUR_CONTRACT_VERSION, ANGLE_CONTRACT_ABI, \
    MAX_GNOSIS_GAS, GNOSIS_GAS_CHECKUP_SLEEPTIME_RANGE, POLYGON_ANGLE_CONTRACT_ADDRESS, CELO_ANGLE_CONTRACT_ADDRESS, \
    GNOSIS_ANGLE_CONTRACT_ADDRESS, WAIT_FOR_BRIDGED_FUNDS_SLEEP_TIME, MAX_LEFT_TOKEN_PERCENTAGE
from sdk.dapps import Dapp
from sdk.decorators import gas_delay, wait
from sdk.models.chain import Chain
from sdk.models.chain import Celo, Gnosis
from sdk.models.token import AGEUR_Token, Token
from sdk.utils import sleep_pause, retry_on_fail


class Angle(Dapp):
    def __init__(self, client: Client) -> None:
        super().__init__(name="AngleMoney")
        self.client: Client = client
        self.base_url: str = ANGLE_BASE_URL
        self.chain_to_contract_addrs_mapping: Dict[str, str] = {
            "POLYGON": POLYGON_ANGLE_CONTRACT_ADDRESS,
            "CELO": CELO_ANGLE_CONTRACT_ADDRESS,
            "GNOSIS": GNOSIS_ANGLE_CONTRACT_ADDRESS,
        }
        self.contract: Contract | None = None

    async def _wait_for_suitable_limits(
        self, amount: int, src_chain: Chain, dst_chain: Chain, sleep_time: List[int]
    ) -> bool:
        while True:
            limit_data = await self._get_to_chain_bridge_limit(
                src_chain=src_chain, dst_chain=dst_chain
            )
            if limit_data is None:
                return False

            from_limit, to_limit = limit_data
            if from_limit < amount or to_limit < amount:
                logger.warning(f"[{self.name}] From or to limit is lower than amount")
                await sleep_pause(delay_range=sleep_time, enable_message=False)
            else:
                return True

    @retry_on_fail(tries=RETRIES)
    async def _get_to_chain_bridge_limit(
        self, src_chain: Chain, dst_chain: Chain
    ) -> None | List[int]:
        data = await self.client.send_get_request(
            url=self.base_url.format(
                self.client.address, src_chain.chain_id, dst_chain.chain_id
            )
        )

        if not data:
            return None

        return (
            int(data[f"{src_chain.chain_id}"][AGEUR_Token.symbol]["fromLimit"]),
            int(data[f"{dst_chain.chain_id}"][AGEUR_Token.symbol]["toLimit"]),
        )

    def _get_adapter_params(self) -> str:
        return self.client.w3.to_hex(encode_packed(["uint16", "uint256"], [1, 200000]))

    # amount passed in wei
    def _get_bridge_calldata(
        self, dst_chain: Chain, amount: int | float, token: Token = AGEUR_Token
    ) -> Tuple:
        return (
            dst_chain.lz_chain_id,
            self.client.address,
            amount,
            self.client.address,
            ADDRESS_ZERO,
            self._get_adapter_params(),
        )

    # amount passed in wei
    async def _estimate_send_fee(
        self, dst_chain: Chain, amount: int, adapter_params: str
    ):
        try:
            data = await self.contract.functions.estimateSendFee(
                dst_chain.lz_chain_id,
                self.client.address,
                amount,
                False,  # USE ZRO
                adapter_params,
            ).call()
            native_fee, _ = data
            return native_fee
        except Exception as e:
            logger.error(f"[{self.name}] Couldn't estimate LayerZero send fee: {e}")
            return None

    async def _get_contract_nonce(self):
        try:
            token_address = AGEUR_Token.chain_to_contract_mapping[self.client.chain.name]
            token_contract = self.client.w3.eth.contract(
                address=token_address, abi=AGEUR_Token.abi
            )
            nonce = await token_contract.functions.nonces(self.client.address).call()
            return nonce
        except Exception as e:
            logger.error(f"[{self.name}] Couldn't get token nonce")
            return None

    def _generate_message(
        self, spender: str, value: int, nonce: int, src_chain: Chain, deadline: int
    ) -> SignableMessage:
        message = {
            "owner": self.client.address,
            "spender": spender,
            "value": value,
            "nonce": nonce,
            "deadline": deadline,
        }

        domain = {
            "name": AGEUR_CONTRACT_NAME,
            "version": AGEUR_CONTRACT_VERSION,
            "chainId": src_chain.chain_id,
            "verifyingContract": AGEUR_Token.chain_to_contract_mapping[
                self.client.chain.name
            ],
        }

        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Permit": [
                    {"name": "owner", "type": "address"},
                    {"name": "spender", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "nonce", "type": "uint256"},
                    {"name": "deadline", "type": "uint256"},
                ],
            },
            "primaryType": "Permit",
            "domain": domain,
            "message": message,
        }

        return encode_structured_data(primitive=typed_data)

    async def _sign_message(self, message: SignableMessage) -> List[str]:
        data_hash = self.client.w3.eth.account.sign_message(
            message, self.client.private_key
        )
        r, v, s = (
            self.client.w3.to_hex(data_hash.r),
            data_hash.v,
            self.client.w3.to_hex(data_hash.s),
        )
        await sleep_pause(delay_range=AFTER_APPROVE_DELAY_RANGE, enable_message=False)
        return r, v, s

    @retry_on_fail(tries=RETRIES)
    async def _send_with_permit(
        self,
        src_chain: Chain,
        dst_chain: Chain,
        amount: int | float,
        token: Token = AGEUR_Token,
    ):
        nonce = await self._get_contract_nonce()

        if nonce is None:
            return False

        logger.info(f"[{self.name}] Approving {amount} {token.symbol} for bridging")

        deadline = self.client.get_deadline(seconds=60 * 3)
        message = self._generate_message(
            spender=self.chain_to_contract_addrs_mapping[self.client.chain.name],
            value=amount,
            nonce=nonce,
            src_chain=src_chain,
            deadline=deadline,
        )
        r, v, s = await self._sign_message(message=message)
        raw_data = self._get_bridge_calldata(dst_chain=dst_chain, amount=amount)
        try:
            data = self.contract.encodeABI(
                fn_name="sendWithPermit", args=(*raw_data, deadline, v, r, s)
            )
        except Exception as e:
            logger.debug(f"[{self.name}] RPC synchronization issues, retrying")
            return False
        send_fee = await self._estimate_send_fee(
            dst_chain=dst_chain,
            amount=amount,
            adapter_params=self._get_adapter_params(),
        )

        if not send_fee:
            return False

        logger.info(
            f"[{self.name}] Bridging {token.from_wei(value=amount)} {AGEUR_Token.symbol} from {src_chain.name} to {dst_chain.name}"
        )
        tx_hash = await self.client.send_transaction(
            to=self.chain_to_contract_addrs_mapping[self.client.chain.name],
            data=data,
            value=send_fee,
        )
        if not tx_hash:
            return False

        return await self.client.verify_tx(tx_hash=tx_hash)

    async def _send(
        self,
        src_chain: Chain,
        dst_chain: Chain,
        amount: int | float,
        token: Token = AGEUR_Token,
    ):
        raw_data = self._get_bridge_calldata(dst_chain=dst_chain, amount=amount)
        data = self.contract.encodeABI(fn_name="send", args=raw_data)

        send_fee = await self._estimate_send_fee(
            dst_chain=dst_chain,
            amount=amount,
            adapter_params=self._get_adapter_params(),
        )

        if not send_fee:
            return False

        if await self.client.approve(
            spender=self.chain_to_contract_addrs_mapping[self.client.chain.name],
            token=AGEUR_Token,
            value=amount,
        ):
            logger.info(
                f"[{self.name}] Bridging {token.from_wei(value=amount)} {AGEUR_Token.symbol} from {src_chain.name} to {dst_chain.name}"
            )
            tx_hash = await self.client.send_transaction(
                to=self.chain_to_contract_addrs_mapping[self.client.chain.name],
                data=data,
                value=send_fee,
            )

            if not tx_hash:
                return False

            return await self.client.verify_tx(tx_hash=tx_hash)
        return False

    @wait(delay_range=TX_DELAY_RANGE)
    @gas_delay(gas_threshold=GAS_THRESHOLD, delay_range=GAS_DELAY_RANGE)
    @retry_on_fail(tries=RETRIES)
    async def bridge(self, src_chain: Chain, dst_chain: Chain, token: Token = AGEUR_Token):
        if self.client.chain != src_chain:
            self.client.change_chain(chain=src_chain)

        self.contract = self.client.w3.eth.contract(
            address=self.chain_to_contract_addrs_mapping[self.client.chain.name],
            abi=ANGLE_CONTRACT_ABI,
        )

        amount = await self.client.get_token_balance(token=token)
        if amount is None:
            return False
        amount = int(amount * (1 - MAX_LEFT_TOKEN_PERCENTAGE))

        # Get token balance on the dst_chain
        self.client.change_chain(chain=dst_chain)
        initial_balance = await self.client.get_token_balance(token=token)
        if initial_balance is None:
            logger.info("Inital balance")
            return False
        # Change the chain back to src_chain
        self.client.change_chain(chain=src_chain)

        limits_matched = await self._wait_for_suitable_limits(
            amount=amount,
            src_chain=src_chain,
            dst_chain=dst_chain,
            sleep_time=REQUEST_SLEEP_TIME_RANGE,
        )
        if not limits_matched:
            return False

        if amount == 0:
            logger.error(
                f"[{self.name}] {AGEUR_Token.symbol} balance on {src_chain.name} is {amount}"
            )
            return False
        if src_chain == Celo or src_chain == Gnosis:
            # if src_chain is GNOSIS make sure the gas is appropriate
            if src_chain == Gnosis:
                await self.client.wait_for_gas(
                    desired_gas=MAX_GNOSIS_GAS,
                    delay_range=GNOSIS_GAS_CHECKUP_SLEEPTIME_RANGE,
                )

            was_bridged = await self._send_with_permit(
                src_chain=src_chain, dst_chain=dst_chain, amount=amount
            )
        else:
            was_bridged = await self._send(
                src_chain=src_chain, dst_chain=dst_chain, amount=amount
            )

        if not was_bridged:
            return False

        return await self.client.wait_for_tokens_recieved_on_wallet(
            initial_balance=initial_balance,
            chain=dst_chain,
            token=token,
            checkup_sleep_time_range=WAIT_FOR_BRIDGED_FUNDS_SLEEP_TIME,
        )
