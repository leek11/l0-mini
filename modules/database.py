import itertools
import json
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from config import USE_MOBILE_PROXY, STARGATE_TX_COUNT, CORE_TX_COUNT, MERKLY_TX_COUNT
from sdk import logger, Client
from sdk.constants import PRIVATE_KEYS_PATH, PROXIES_PATH, DEPOSIT_ADDRESSES_PATH, DATABASE_PATH
from sdk.models.data_item import DataItem
from sdk.utils import read_from_txt


@dataclass
class Database:
    data: List[DataItem]

    def _to_dict(self) -> List[Dict[str, Any]]:
        return [vars(data_item) for data_item in self.data]

    @staticmethod
    def create_database() -> "Database":
        data = []

        private_keys = read_from_txt(file_path=PRIVATE_KEYS_PATH)
        proxies = read_from_txt(file_path=PROXIES_PATH)
        deposit_addresses = read_from_txt(file_path=DEPOSIT_ADDRESSES_PATH)

        if USE_MOBILE_PROXY:
            proxies = proxies * len(private_keys)

        for private_key, proxy, deposit_address in itertools.zip_longest(
                private_keys, proxies, deposit_addresses, fillvalue=None
        ):
            try:
                temp_client = Client(private_key=private_key, proxy=proxy)

                item = DataItem(
                    private_key=private_key,
                    address=temp_client.address,
                    proxy=proxy,
                    deposit_address=deposit_address,
                    merkly_tx_count=Database.get_randomized_merkly_tx_counts(),
                    stargate_tx_count=random.randint(*STARGATE_TX_COUNT["Polygon-Kava"]['tx-range']),
                    core_bridge_tx_count=random.randint(*CORE_TX_COUNT["BSC-Core"]['tx-range'])
                )

                data.append(item)
            except Exception as e:
                logger.exception(f"[Database] {e}")

        logger.success(f"[Database] Created successfully", send_to_tg=False)
        return Database(data=data)

    def save_database(self, file_name: str = DATABASE_PATH):
        db_dict = self._to_dict()

        with open(file_name, "w") as json_file:
            json.dump(db_dict, json_file, indent=4)

    @classmethod
    def read_from_json(cls, file_name: str = DATABASE_PATH) -> "Database":
        try:
            with open(file_name, "r") as json_file:
                db_dict = json.load(json_file)
        except Exception as e:
            logger.error(f"[Database] {e}")

        data = []

        for item in db_dict:
            account_data = {
                "private_key": item.pop("private_key"),
                "proxy": item.pop("proxy"),
            }

            item.pop("address")

            account = Client(**account_data)
            data_item = DataItem(
                private_key=account.private_key,
                address=account.address,
                proxy=account_data["proxy"],
                **item
            )
            data.append(data_item)

        return cls(data=data)

    def get_random_item_by_criteria(self, **kwargs) -> Optional[tuple[DataItem, int]]:
        filtered_items = self.query_items_by_criteria(**kwargs)

        if filtered_items:
            random_item = random.choice(filtered_items)
            item_index = self.get_item_index_by_data(random_item)
            return random_item, item_index

        return None

    def delete_item_if_finished(self, data_item: DataItem) -> bool:
        if data_item.get_tx_count() == 0:
            self.data.remove(data_item)
            return True
        return False

    def get_item_index_by_data(self, search_item: DataItem) -> Optional[int]:
        for index, item in enumerate(self.data):
            if item == search_item:
                return index
        return None

    def query_items_by_criteria(self, **kwargs) -> List[DataItem]:
        filtered_items = []

        for item in self.data:
            if all(getattr(item, key) == value for key, value in kwargs.items()):
                filtered_items.append(item)

        return filtered_items

    def get_random_data_item(self) -> Optional[tuple[DataItem, int]]:
        if self.data:
            random_index = random.randrange(len(self.data))
            return self.data[random_index], random_index
        return None, None

    def update_item(self, item_index: int, **kwargs):
        if 0 <= item_index < len(self.data):
            item = self.data[item_index]

            for key, value in kwargs.items():
                setattr(item, key, value)

            self.save_database()
        else:
            logger.error(f"[Database] Invalid item index: {item_index}")

    def reset_item(self, item_index: int):
        if 0 <= item_index < len(self.data):
            item = self.data[item_index]
            item.chain_with_funds = None
            item.warmup_started = False
            item.warmup_finished = True
            item.okx_withdrawn = False
            item.polygon_from_usdc_swapped = False
            item.from_polygon_ageur_bridged = False
            item.to_polygon_ageur_bridged = False
            item.polygon_to_usdc_swapped = False
            item.sent_to_okx = False
            self.save_database()
        else:
            logger.error(f"[Database] Invalid item index: {item_index}")

    @staticmethod
    def get_randomized_merkly_tx_counts():
        return {
            "BSC": {
                "Gnosis": random.randint(*MERKLY_TX_COUNT["BSC"]["Gnosis"]["tx-range"]),
                "Celo": random.randint(*MERKLY_TX_COUNT["BSC"]["Celo"]["tx-range"]),
                "Kava": random.randint(*MERKLY_TX_COUNT["BSC"]["Kava"]["tx-range"]),
                "Linea": random.randint(*MERKLY_TX_COUNT["BSC"]["Linea"]["tx-range"]),
                "Base": random.randint(*MERKLY_TX_COUNT["BSC"]["Base"]["tx-range"]),
                "Scroll": random.randint(*MERKLY_TX_COUNT["BSC"]["Scroll"]["tx-range"]),
                "DFK": random.randint(*MERKLY_TX_COUNT["BSC"]["DFK"]["tx-range"]),
                "Harmony": random.randint(*MERKLY_TX_COUNT["BSC"]["Harmony"]["tx-range"])
            },
            "Polygon": {
                "Gnosis": random.randint(*MERKLY_TX_COUNT["Polygon"]["Gnosis"]["tx-range"]),
                "Celo": random.randint(*MERKLY_TX_COUNT["Polygon"]["Celo"]["tx-range"]),
                "BSC": random.randint(*MERKLY_TX_COUNT["Polygon"]["BSC"]["tx-range"]),
                "Kava": random.randint(*MERKLY_TX_COUNT["Polygon"]["Kava"]["tx-range"]),
                "Linea": random.randint(*MERKLY_TX_COUNT["Polygon"]["Linea"]["tx-range"]),
                "Base": random.randint(*MERKLY_TX_COUNT["Polygon"]["Base"]["tx-range"]),
                "Zora": random.randint(*MERKLY_TX_COUNT["Polygon"]["Zora"]["tx-range"]),
                "Scroll": random.randint(*MERKLY_TX_COUNT["Polygon"]["Scroll"]["tx-range"]),
                "DFK": random.randint(*MERKLY_TX_COUNT["Polygon"]["DFK"]["tx-range"]),
                "Harmony": random.randint(*MERKLY_TX_COUNT["Polygon"]["Harmony"]["tx-range"]),
            },
            "Celo": {
                "Gnosis": random.randint(*MERKLY_TX_COUNT["Celo"]["Gnosis"]["tx-range"]),
                "Linea": random.randint(*MERKLY_TX_COUNT["Celo"]["Linea"]["tx-range"]),
                "BSC": random.randint(*MERKLY_TX_COUNT["Celo"]["BSC"]["tx-range"])
            },
            "Gnosis": {
                "Celo": random.randint(*MERKLY_TX_COUNT["Gnosis"]["Celo"]["tx-range"]),
                "BSC": random.randint(*MERKLY_TX_COUNT["Gnosis"]["BSC"]["tx-range"]),
                "Linea": random.randint(*MERKLY_TX_COUNT["Gnosis"]["Linea"]["tx-range"]),
                "Base": random.randint(*MERKLY_TX_COUNT["Gnosis"]["Base"]["tx-range"]),
                "Scroll": random.randint(*MERKLY_TX_COUNT["Gnosis"]["Scroll"]["tx-range"])
            },
            "Arbitrum": {
                "Gnosis": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["Gnosis"]["tx-range"]),
                "Celo": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["Celo"]["tx-range"]),
                "BSC": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["BSC"]["tx-range"]),
                "Kava": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["Kava"]["tx-range"]),
                "Linea": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["Linea"]["tx-range"]),
                "Base": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["Base"]["tx-range"]),
                "Zora": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["Zora"]["tx-range"]),
                "Scroll": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["Scroll"]["tx-range"]),
                "DFK": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["DFK"]["tx-range"]),
                "Harmony": random.randint(*MERKLY_TX_COUNT["Arbitrum"]["Harmony"]["tx-range"])
            },
            "Moonbeam": {
                "Gnosis": random.randint(*MERKLY_TX_COUNT["Moonbeam"]["Gnosis"]["tx-range"]),
                "Celo": random.randint(*MERKLY_TX_COUNT["Moonbeam"]["Celo"]["tx-range"]),
                "BSC": random.randint(*MERKLY_TX_COUNT["Moonbeam"]["BSC"]["tx-range"]),
                "Linea": random.randint(*MERKLY_TX_COUNT["Moonbeam"]["Linea"]["tx-range"]),
                "Base": random.randint(*MERKLY_TX_COUNT["Moonbeam"]["Base"]["tx-range"]),
                "Scroll": random.randint(*MERKLY_TX_COUNT["Moonbeam"]["Scroll"]["tx-range"]),
                "DFK": random.randint(*MERKLY_TX_COUNT["Moonbeam"]["DFK"]["tx-range"]),
                "Harmony": random.randint(*MERKLY_TX_COUNT["Moonbeam"]["Harmony"]["tx-range"])
            },
            "Moonriver": {
                "BSC": random.randint(*MERKLY_TX_COUNT["Moonriver"]["BSC"]["tx-range"]),
                "Kava": random.randint(*MERKLY_TX_COUNT["Moonriver"]["Kava"]["tx-range"]),
                "Linea": random.randint(*MERKLY_TX_COUNT["Moonriver"]["Linea"]["tx-range"]),
                "Base": random.randint(*MERKLY_TX_COUNT["Moonriver"]["Base"]["tx-range"]),
                "Scroll": random.randint(*MERKLY_TX_COUNT["Moonriver"]["Scroll"]["tx-range"])
            },
            "Conflux": {
                "Celo": random.randint(*MERKLY_TX_COUNT["Conflux"]["Celo"]["tx-range"])
            }
        }
