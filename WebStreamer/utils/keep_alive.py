from asyncio import sleep

from aiohttp import ClientSession, ClientTimeout

from WebStreamer.logger import LOGGER
from WebStreamer.vars import Vars


async def ping_server():
    sleep_time = Vars.PING_INTERVAL
    LOGGER.info(f"Started with {sleep_time}s interval between pings")
    while True:
        await sleep(sleep_time)
        try:
            async with ClientSession(timeout=ClientTimeout(total=10)) as session:
                async with session.get(Vars.URL) as resp:
                    LOGGER.info(f"Pinged server with response: {resp.status}")
        except TimeoutError:
            LOGGER.warning("Couldn't connect to the site URL..")
        except Exception:
            LOGGER.error("Unexpected error: ", exc_info=True)
