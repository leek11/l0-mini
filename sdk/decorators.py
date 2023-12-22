import asyncio
import random
from functools import wraps

from tqdm import tqdm
from web3 import AsyncWeb3

from sdk import logger
from sdk.utils import sleep_pause, get_eth_gas_fee


def gas_delay(gas_threshold: int, delay_range: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            while True:
                current_eth_gas_price = await get_eth_gas_fee()
                threshold = AsyncWeb3.to_wei(gas_threshold, "gwei")
                if current_eth_gas_price > threshold:
                    random_delay = random.randint(*delay_range)

                    logger.warning(
                        f"Current gas fee {round(AsyncWeb3.from_wei(current_eth_gas_price, 'gwei'), 2)} GWEI > Gas threshold {AsyncWeb3.from_wei(threshold, 'gwei')} GWEI. Waiting for {random_delay} seconds..."
                    )

                    with tqdm(
                        total=random_delay,
                        desc="Waiting",
                        unit="s",
                        dynamic_ncols=True,
                        colour="blue",
                    ) as pbar:
                        for _ in range(random_delay):
                            await asyncio.sleep(1)
                            pbar.update(1)
                else:
                    break

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def check_balance(threshold):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if self.account is not None:
                balance = await self.account.get_native_balance()
                if balance < AsyncWeb3.to_wei(threshold, "ether"):
                    logger.error(
                        f"Balance is below the threshold at {self.account.address}"
                    )
                    return False
            else:
                logger.error("Client attribute is not set. Function not executed.")
                return False

            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


def wait(delay_range: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            await sleep_pause(delay_range=delay_range, enable_message=False)
            return result

        return wrapper

    return decorator