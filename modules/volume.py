import random

from config import OKX_API_KEY, OKX_API_SECRET, OKX_API_PASSWORD, OKX_WITHDRAWAL_AMOUNT_RANGE, TX_DELAY_RANGE, \
    MAX_SLIPPAGE, WALLET_DELAY_RANGE
from modules.database import Database
from sdk import Client, OKX, logger
from sdk.constants import POLYGON_CONFIRMATION_BLOCKS, BLOCK_CHECK_SLEEP_RANGE
from sdk.dapps import Inch, Angle
from sdk.models.chain import Polygon, Celo, Gnosis, ChainEnum
from sdk.models.data_item import DataItem
from sdk.models.token import USDC_Token, AGEUR_Token
from sdk.utils import sleep_pause


class Volume:
    @staticmethod
    async def execute_mode():
        db = Database.read_from_json()

        while True:
            unfinished_items = db.query_items_by_criteria(warmup_started=True)

            if unfinished_items:
                logger.warning(
                    f"[Volume Mode] Unfinished wallets found: {[wallet for wallet in unfinished_items]}"
                )

            for item in unfinished_items:
                item_index = db.get_item_index_by_data(search_item=item)
                await Volume.perform_cycle(
                    item=item,
                    item_index=item_index,
                    database=db,
                    **item.get_item_state(),
                )
                await sleep_pause(delay_range=WALLET_DELAY_RANGE)

            item_data = db.get_random_item_by_criteria(
                warmup_started=False, warmup_finished=False
            )
            if item_data is None:
                break
            else:
                item, item_index = item_data
                await Volume.perform_cycle(
                    item=item, item_index=item_index, database=db
                )
            await sleep_pause(delay_range=WALLET_DELAY_RANGE, enable_message=False)
        logger.success("[Volume Mode] No more items left")

    @staticmethod
    async def perform_cycle(
        item: DataItem,
        item_index: int,
        database: Database,
        okx_withdrawn: bool = False,
        polygon_from_usdc_swapped: bool = False,
        from_polygon_ageur_bridged: bool = False,
        to_polygon_ageur_bridged: bool = False,
        polygon_to_usdc_swapped: bool = False,
        sent_to_okx: bool = False,
    ):
        client = Client(private_key=item.private_key, proxy=item.proxy)
        okx = OKX(
            api_key=OKX_API_KEY,
            secret=OKX_API_SECRET,
            password=OKX_API_PASSWORD,
            client=client,
        )
        inch = Inch(client=client)
        angle = Angle(client=client)

        logger.debug(f"[Volume Mode] Wallet: {item.address}")

        # Withdrawal from OKX
        if okx_withdrawn == False:
            # Collect all the tokens from OKX sub-accounts
            await okx.transfer_from_sub_accounts()
            amount_to_withdraw = round(random.uniform(*OKX_WITHDRAWAL_AMOUNT_RANGE), 3)
            tokens_withdrawn = await okx.withdraw(amount_to_withdraw=amount_to_withdraw)
            if not tokens_withdrawn:
                return False
            database.update_item(
                item_index=item_index, warmup_started=True, okx_withdrawn=True
            )
            await sleep_pause(delay_range=TX_DELAY_RANGE, enable_message=False)

        # Swap from USDC -> AGEUR
        if polygon_from_usdc_swapped == False:
            usdc_tokens_swapped = await inch.swap(
                token_in=USDC_Token, token_out=AGEUR_Token, slippage=MAX_SLIPPAGE
            )
            if not usdc_tokens_swapped:
                return False
            database.update_item(item_index=item_index, polygon_from_usdc_swapped=True)
            await sleep_pause(delay_range=TX_DELAY_RANGE, enable_message=False)

        # Bridge from POLYGON -> CELO/GNOSIS
        if from_polygon_ageur_bridged == False:
            dst_chain = random.choice([Celo, Gnosis])
            tokens_bridged_from_polygon = await angle.bridge(
                src_chain=Polygon, dst_chain=dst_chain
            )
            if not tokens_bridged_from_polygon:
                return False
            database.update_item(
                item_index=item_index,
                from_polygon_ageur_bridged=True,
                chain_with_funds=dst_chain.name,
            )
            await sleep_pause(delay_range=TX_DELAY_RANGE, enable_message=False)

        # Cycle bridges (GNOSIS/CELO)
        while item.angle_tx_count > 0:
            if item.chain_with_funds == Celo:
                src_chain = Celo
                dst_chain = Gnosis
            elif item.chain_with_funds == Gnosis:
                src_chain = Gnosis
                dst_chain = Celo
            await angle.bridge(src_chain=src_chain, dst_chain=dst_chain)
            database.update_item(
                item_index=item_index,
                angle_tx_count=item.angle_tx_count - 1,
                chain_with_funds=dst_chain.name,
            )
            await sleep_pause(delay_range=TX_DELAY_RANGE, enable_message=False)

        # After cycle, bridge AGEUR back -> POLYGON
        if to_polygon_ageur_bridged == False:
            src_chain = ChainEnum[item.chain_with_funds].value
            tokens_bridged_to_polygon = await angle.bridge(
                src_chain=src_chain, dst_chain=Polygon
            )
            if not tokens_bridged_to_polygon:
                return False
            database.update_item(item_index=item_index, to_polygon_ageur_bridged=True)
            await sleep_pause(delay_range=TX_DELAY_RANGE, enable_message=False)

        # Swap AGEUR back to USDC
        if polygon_to_usdc_swapped == False:
            tokens_swapped_back = await inch.swap(
                token_in=AGEUR_Token, token_out=USDC_Token, slippage=MAX_SLIPPAGE
            )
            if not tokens_swapped_back:
                return False
            database.update_item(item_index=item_index, polygon_to_usdc_swapped=True)
            await sleep_pause(delay_range=TX_DELAY_RANGE, enable_message=False)

        # Send USDC back to OKX
        if sent_to_okx == False:
            tokens_sent_to_okx = await client.send_erc20(
                token=USDC_Token, recipient=item.deposit_address
            )
            if not tokens_sent_to_okx:
                return False
            database.update_item(item_index=item_index, sent_to_okx=True)

            # Wait for deposit to be confirmed in the blockchain
            await client.wait_for_block_confirmations(
                sent_block=await client.w3.eth.get_block_number(),
                confirmation_blocks=POLYGON_CONFIRMATION_BLOCKS,
                sleep_time=BLOCK_CHECK_SLEEP_RANGE,
                extra_blocks=10,
            )

        database.reset_item(item_index=item_index)