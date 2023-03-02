from pyrogram import Client

from WebStreamer.vars import Vars

# Initialize the main bot, for normal bot operations
StreamBot = Client(
    "Web Streamer",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.BOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    plugins={"root": "WebStreamer/bot/plugins"},
    workers=Vars.WORKERS,
)

# make a dict to store all the clients,
# we will also use this later to determine
# which cleint has least load and use that
# to stream files
multi_clients = {}
work_loads = {}
