from asyncio import get_event_loop
from glob import glob
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from sys import modules

from aiohttp import web
from pyrogram import idle

from WebStreamer.bot import StreamBot
from WebStreamer.logger import LOGGER
from WebStreamer.server import web_server
from WebStreamer.vars import Vars

ppath = "WebStreamer/bot/plugins/*.py"
files = glob(ppath)

loop = get_event_loop()


async def start_services():
    LOGGER.info("------------------- Initializing Telegram Bot -------------------")
    await StreamBot.start()
    LOGGER.info("----------------------------- DONE -----------------------------")
    LOGGER.info("--------------------------- Importing ---------------------------")
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"WebStreamer/bot/plugins/{plugin_name}.py")
            import_path = f".plugins.{plugin_name}"
            spec = spec_from_file_location(import_path, plugins_dir)
            load = module_from_spec(spec)
            spec.loader.exec_module(load)
            modules[f"WebStreamer.bot.plugins.{plugin_name}"] = load
            LOGGER.info(f"Imported => {plugin_name}")
    if Vars.ON_HEROKU:
        LOGGER.info("------------------ Starting Keep Alive Service ------------------")
    LOGGER.info("-------------------- Initializing Web Server --------------------")
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0" if Vars.ON_HEROKU else Vars.FQDN
    await web.TCPSite(app, bind_address, Vars.PORT).start()
    LOGGER.info("----------------------------- DONE -----------------------------")
    LOGGER.info("----------------------- Service Started -----------------------")
    LOGGER.info(f"bot =>> {(await StreamBot.get_me()).first_name}")
    LOGGER.info(f"server ip =>> {bind_address}:{Vars.PORT}")
    if Vars.ON_HEROKU:
        LOGGER.info(f"app running on =>> {Vars.FQDN}")
    LOGGER.info("---------------------------------------------------------------")
    await idle()


if __name__ == "__main__":
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        LOGGER.info("----------------------- Service Stopped -----------------------")
