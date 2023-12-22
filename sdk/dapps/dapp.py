import random
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Union

from sdk import Client
from sdk.models.token import Token


@dataclass
class Dapp:
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    @staticmethod
    def aggregate(dapps: List["Dapp"], token_in: "Token") -> List[Union["Token", "Dapp"]]:
        supported_dapps = []  # Supported dapps are the dapps that have token_in in their pairs
        supported_tokens_out = []  # Supported tokens_out as a list

        for dapp in dapps:
            if token_in in dapp.pairs:
                supported_tokens_out.extend(dapp.pairs[token_in])
                supported_dapps.append(dapp)

        if len(supported_dapps) == 1:
            # Remove duplicates if there's only one supported dapp
            supported_tokens_out = list(set(supported_tokens_out))
        elif len(supported_dapps) >= 2:
            # Create a dictionary to count the appearances of each token
            token_counts = defaultdict(int)
            for token in supported_tokens_out:
                token_counts[token] = token_counts.get(token, 0) + 1

            # Filter tokens based on counts
            supported_tokens_out = [token for token in supported_tokens_out if token_counts[token] > 1]

            # Remove duplicates from the filtered list
            seen_tokens = set()
            unique_tokens_out = []
            for token in supported_tokens_out:
                if token not in seen_tokens:
                    unique_tokens_out.append(token)
                    seen_tokens.add(token)
            supported_tokens_out = unique_tokens_out

        return Dapp._get_random_dapp_and_token(dapps=supported_dapps, tokens=supported_tokens_out)

    @staticmethod
    def init_dapps(dapps_list: List["Dapp"], client: Client) -> List["Dapp"]:
        initialized_dapps = [DappClass(client=client) for DappClass in dapps_list]
        random.shuffle(initialized_dapps)

        return initialized_dapps

    @staticmethod
    def _get_random_dapp_and_token(dapps: List["Dapp"], tokens: List["Token"]):
        random.shuffle(dapps)
        random.shuffle(tokens)

        for token in tokens:
            token = random.choice(tokens)
            supported_dapps = [dapp for dapp in dapps if token in dapp.pairs]

            if supported_dapps:
                return token, random.choice(supported_dapps)

            tokens.remove(token)

        return None, None