import asyncio
import functools
import json
import random
from typing import List

import aiohttp
from tqdm import tqdm
from web3 import AsyncWeb3

from config import PROXY_CHANGE_IP_URL
from sdk.logger import logger
from sdk.models.chain import EthMainnet

async def change_ip() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=PROXY_CHANGE_IP_URL) as response:
            if response.status == 200:
                logger.debug(f"[PROXY] Successfully changed ip address")
                return True
            else:
                logger.warning(f"[PROXY] Couldn't change ip address")
                return False

def read_from_txt(file_path):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file]
    except FileNotFoundError as e:
        logger.error(f"File '{file_path}' not found.")
    except Exception as e:
        logger.error(f"Encountered an error while reading a .txt file '{file_path}': {str(e)}.")


def read_from_json(file_path):
    try:
        with open(file_path) as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        logger.error(f"File '{file_path}' not found.")
        exit()
    except Exception as e:
        logger.exception(f"Encountered an error while reading a JSON file '{file_path}': {e}.")
        exit()


async def sleep_pause(delay_range: List[int], enable_message: bool = True, enable_pr_bar: bool = True):
    delay = random.randint(*delay_range)

    if enable_message:
        logger.info(f"Sleeping for {delay} seconds...")

    if enable_pr_bar:
        with tqdm(total=delay, desc="Waiting", unit="s", dynamic_ncols=True, colour="blue") as pbar:
            for _ in range(delay):
                await asyncio.sleep(delay=1)
                pbar.update(1)
    else:
        await asyncio.sleep(delay=delay)


def retry_on_fail(tries: int, retry_delay: List[int] = [5, 10]):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for _ in range(tries):
                result = await func(*args, **kwargs)
                if result is None or result is False:
                    await sleep_pause(delay_range=retry_delay, enable_message=False)
                else:
                    return result
            return False

        return wrapper

    return decorator


async def get_eth_gas_fee(chain=EthMainnet):
    w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(chain.rpc))
    return await w3.eth.gas_price


def greeting() -> None:
    logger.success(
        r"""

                                  ^Y                  
                                 ~&@7                
                      75~:.     !@&~&:       , .      
                      .&&PYY7^.7@@# J#   .^7JPB^      
                       ^@&Y:^?Y&@@P  GBB&@@GP&~       
                        7@@&?  :&@J  G@@&Y.~#^        
                     .:~?&#&@&? !@! B@G~  !&:         
                :75PPY?!^. .:?GG~P!5P~^!YG@@GJ~.      
                .~YG#&&##B#BGPJ?J??J?J5GBBBB##&#B5!.  
                    .^?P&@BJ!^^5G~G^5GJ^. .:!?Y5P57:\  
                       .#?  ^P@#.:@J !&@@#&J~^.       
                      :#7.J&@@#. !@@~  !&@@5          
                     ^&GP@@&BG#. J@@@5?~:?&@7         
                    :BGJ7^..  GG P@@J.:!JY5&@:        
                    .         .&7B@?      .~YJ        
                              ^&@7                   
                                ?!                  

               __    _ __                        __                  
   _______  __/ /_  (_) /  _   __   ____  ____ _/ /______  ____  ___ 
  / ___/ / / / __ \/ / /  | | / /  /_  / / __ `/ //_/ __ \/ __ \/ _ \
 (__  ) /_/ / /_/ / / /   | |/ /    / /_/ /_/ / ,< / /_/ / / / /  __/   
/____/\__, /_.___/_/_/    |___/    /___/\__,_/_/|_|\____/_/ /_/\___/ 
     /____/      
                                              """
    , send_to_tg=False)


def menu_message():
    print(
        r"""
1. Create database
2. Warmup (Merkly / Stargate / CoreBridge)
""")
