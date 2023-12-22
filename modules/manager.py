from modules import Database
from modules.volume import Volume
from modules.warmup import Warmup
from sdk import logger
from sdk.utils import greeting, menu_message


class Manager:
    async def run_module(self):
        try:
            greeting()
            menu_message()
            module = input("Start module: ")

            if module == "1":
                db = Database.create_database()
                db.save_database()
            elif module == "2":
                await Warmup.execute_mode()
            # elif module == "3":
            #     await Volume.execute_mode()
            else:
                logger.error(f"Invalid module number: {module}", send_to_tg=False)
        except KeyboardInterrupt:
            logger.error("Finishing script", send_to_tg=False)
        except Exception as e:
            logger.exception(str(e))

