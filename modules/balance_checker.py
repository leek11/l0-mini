from rich.console import Console
from rich.table import Table

from config import USE_MOBILE_PROXY
from modules import Database
from sdk import Client, logger
from sdk.models.chain import BSC, Gnosis, Polygon, Celo, Arbitrum, Moonbeam, Moonriver, Conflux
from sdk.utils import change_ip


async def balance_checker():
    database = Database.read_from_json()
    data_index = 0

    table = Table(title="Balance checker")
    chains = [BSC, Gnosis, Polygon, Celo, Arbitrum, Moonbeam, Moonriver, Conflux]
    rows = []

    logger.info("Please wait")

    while data_index < len(database.data):
        try:
            if USE_MOBILE_PROXY:
                await change_ip()

            data_item = database.data[data_index]
            row = []

            for chain in chains:
                client = Client(private_key=data_item.private_key, proxy=data_item.proxy, chain=chain)
                balance = await client.get_native_balance(chain=chain) / 10 ** 18
                row.append(str(round(balance, 5)))

            data_index += 1
            rows.append(row)
        except Exception as ex:
            logger.exception(f"[Balance checker] Error occurred: {ex}")

    for chain in chains:
        table.add_column(chain.name)

    for row in rows:
        table.add_row(*row, style='bright_green')

    console = Console()
    console.print(table)
