from asyncio import get_event_loop
from glob import glob

from aiohttp import web
from pyrogram import idle

from WebStreamer.bot import StreamBot
from WebStreamer.bot.client import initialize_clients
from WebStreamer.logger import LOGGER
from WebStreamer.server import web_server
from WebStreamer.vars import Vars

files = glob("WebStreamer/bot/plugins/*.py")

server = web.AppRunner(web_server())
loop = get_event_loop()


async def start_services():
    LOGGER.info("Initializing Telegram Bot")
    await StreamBot.start()
    bot_info = await StreamBot.get_me()
    LOGGER.debug(bot_info)
    StreamBot.username = bot_info.username
    LOGGER.info("Initialized Telegram Bot")
    LOGGER.info(f"bot =>> {bot_info.first_name}")
    if bot_info.dc_id:
        LOGGER.info(f"DC ID =>> {str(bot_info.dc_id)}")
    await initialize_clients()
    await server.setup()
    await web.TCPSite(server, Vars.BIND_ADDRESS, Vars.PORT).start()
    LOGGER.info("Service Started")
    LOGGER.info(f"URL =>> {Vars.URL}")
    await idle()


async def cleanup():
    await server.cleanup()
    await StreamBot.stop()


if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        pass
    except Exception as err:
        LOGGER.error(err.with_traceback(None))
    finally:
        loop.run_until_complete(cleanup())
        loop.stop()
        LOGGER.info("----------------------- Service Stopped -----------------------")
