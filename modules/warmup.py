import random

from config import USE_MOBILE_PROXY, TOKEN_USE_PERCENTAGE, ROUND_TO, USE_OKX_WITHDRAW, OKX_API_KEY, OKX_API_SECRET, \
    OKX_API_PASSWORD
from modules.database import Database
from sdk import Client, logger, OKX
from sdk.dapps import Stargate, CoreBridge
from sdk.dapps.merkly import Merkly
from sdk.models.chain import Moonbeam, Moonriver, DFK, Harmony, Celo, Kava, Polygon, BSC, CoreDAO, NAMES_TO_CHAINS
from sdk.models.data_item import DataItem
from sdk.utils import change_ip


class Warmup:
    @staticmethod
    async def execute_mode():
        db = Database.read_from_json()

        while True:
            try:
                if USE_MOBILE_PROXY:
                    await change_ip()

                data_item, index = db.get_random_data_item()

                if not data_item:
                    break

                client = Client(private_key=data_item.private_key, proxy=data_item.proxy)

                logger.info("", send_to_tg=False)
                logger.debug(f"[Warmup] Wallet: {data_item.address}")
                logger.info(f"[Warmup] Transactions left for this wallet: {data_item.get_tx_count()}", send_to_tg=False)

                action, dapp = data_item.get_random_warmup_action()

                if not action:
                    if db.delete_item_if_finished(data_item=data_item):
                        logger.warning(f"[Warmup] No actions left for this wallet")
                        db.save_database()
                    continue

                if await Warmup.execute_warmup_action(
                        item=data_item,
                        action=action,
                        dapp=dapp,
                        client=client
                ):
                    db.delete_item_if_finished(data_item=data_item)
                    db.save_database()
            except Exception as ex:
                logger.exception(f"[Warmup] Error occurred: {ex}")
        logger.success(f"[Warmup] Warmup ended")

    @staticmethod
    async def execute_warmup_action(
        item: DataItem,
        action: str,
        dapp,
        client: Client
    ):
        chains = action.split('-')
        src_chain = NAMES_TO_CHAINS[chains[0]]
        dst_chain = NAMES_TO_CHAINS[chains[1]]

        onchain_balance = await client.get_native_balance(chain=src_chain)

        if USE_OKX_WITHDRAW[src_chain.name]["use"]:
            if USE_OKX_WITHDRAW[src_chain.name]["min-balance"] > onchain_balance:
                amount_to_withdraw = round(
                    random.uniform(*USE_OKX_WITHDRAW[src_chain.name]["amount"]),
                    ROUND_TO
                )

                okx = OKX(
                    api_key=OKX_API_KEY,
                    secret=OKX_API_SECRET,
                    password=OKX_API_PASSWORD,
                    client=client
                )

                await okx.withdraw(
                    amount_to_withdraw=amount_to_withdraw,
                    token=src_chain.coin_symbol,
                    chain=src_chain
                )

                onchain_balance = await client.get_native_balance(chain=src_chain)

        amount = round(
            onchain_balance / 10 ** 18 * TOKEN_USE_PERCENTAGE,
            ROUND_TO
        )

        if dapp == Merkly:
            dapp = Merkly(client=client, chain=src_chain)
            result = await dapp.bridge(src_chain=src_chain, dst_chain=dst_chain, amount=amount)
        elif dapp == Stargate:
            dapp = Stargate(client=client)
            result = await dapp.swap_and_bridge(amount=amount)
        else:
            dapp = CoreBridge(client=client)
            result = await dapp.swap_and_bridge(amount=amount)

        if result:
            item.decrease_action_count(
                action=action, dapp=dapp.name
            )
            return True


