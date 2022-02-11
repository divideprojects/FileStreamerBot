from pyrogram import Client

from WebStreamer.vars import Vars

StreamBot = Client(
    "Web Streamer",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.BOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)
