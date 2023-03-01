from pyrogram import Client

from WebStreamer.vars import Vars

# Initialize bot, for normal bot operations
StreamBot = Client(
    "Web Streamer",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.BOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)

# @MisS_AliTaBot client for downloading files
MissAliTaBot = Client(
    "Miss AliTa Bot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.MISSALITABOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)
