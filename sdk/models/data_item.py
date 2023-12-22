from __future__ import annotations

import random
from dataclasses import dataclass

from sdk.dapps import Stargate, CoreBridge
from sdk.dapps.merkly import Merkly
from sdk.models.chain import Chain


@dataclass
class DataItem:
    private_key: str
    address: str
    proxy: str
    deposit_address: str
    merkly_tx_count: dict[str, dict[str, int]]
    stargate_tx_count: int
    core_bridge_tx_count: int
    chain_with_funds: Chain | None = None,
    warmup_started: bool = False
    warmup_finished: bool = False
    okx_withdrawn: bool = False
    polygon_from_usdc_swapped: bool = False
    from_polygon_ageur_bridged: bool = False
    to_polygon_ageur_bridged: bool = False
    polygon_to_usdc_swapped: bool = False
    sent_to_okx: bool = False

    def get_random_warmup_action(self):
        dapps_and_actions = []

        if self.stargate_tx_count > 0:
            dapps_and_actions.append((
                "Polygon-Kava", Stargate
            ))

        if self.core_bridge_tx_count > 0:
            dapps_and_actions.append((
                "BSC-Core", CoreBridge
            ))

        for key, value in self.merkly_tx_count.items():
            for chain, count in value.items():
                if count > 0:
                    dapps_and_actions.append((f"{key}-{chain}", Merkly))

        if not dapps_and_actions:
            return None, None

        return random.choice(dapps_and_actions)

    def get_item_state(self):
        state = {
            "okx_withdrawn": self.okx_withdrawn,
            "polygon_from_usdc_swapped": self.polygon_from_usdc_swapped,
            "from_polygon_ageur_bridged": self.from_polygon_ageur_bridged,
            "to_polygon_ageur_bridged": self.to_polygon_ageur_bridged,
            "polygon_to_usdc_swapped": self.polygon_to_usdc_swapped,
            "sent_to_okx": self.sent_to_okx,
        }
        return state

    def get_tx_count(self):
        total_transactions = 0

        total_transactions += self.stargate_tx_count + self.core_bridge_tx_count

        for key, chains in self.merkly_tx_count.items():
            for chain, value in chains.items():
                total_transactions += value

        return total_transactions

    def decrease_action_count(self, action: str, dapp: str, amount: int = 1) -> bool:
        if action == "Polygon-Kava" and dapp == "Stargate":
            attribute_name = f"stargate_tx_count"
        elif action == "BSC-Core" and dapp == "CoreBridge":
            attribute_name = f"core_bridge_tx_count"
        else:
            chains = action.split('-')
            if self.merkly_tx_count[chains[0]][chains[1]] >= amount:
                self.merkly_tx_count[chains[0]][chains[1]] -= 1
                return True
            else:
                return False

        if hasattr(self, attribute_name):
            current_count = getattr(self, attribute_name)

            if current_count >= amount:
                setattr(self, attribute_name, current_count - amount)
                return True
            else:
                return False
        else:
            return False
