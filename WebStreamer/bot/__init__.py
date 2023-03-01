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

# MISSALITABOT_TOKEN
MissAliTaBot = Client(
    "Miss AliTa Bot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.MISSALITABOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)

# DIVKIXBOT_TOKEN
DivkixBot = Client(
    "Divkix Bot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.DIVKIXBOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)

# PREMIUMACCOUNTSROBOT_TOKEN
PremiumAccountsRobot = Client(
    "Premium Accounts Robot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.PREMIUMACCOUNTSROBOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)

# GOFILTERBOT_TOKEN
GoFilterBot = Client(
    "Go Filter Bot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.GOFILTERBOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)

# ALITABETABOT_TOKEN
AlitaBetaBot = Client(
    "Alita Beta Bot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.ALITABETABOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)

# DP_WATERMARKBOT_BOT
DPWatermarkBot = Client(
    "DP Watermark Bot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.DP_WATERMARKBOTBOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)

# VIDMERGEBOT_TOKEN
VidMergeBot = Client(
    "Vid Merge Bot",
    api_id=Vars.API_ID,
    api_hash=Vars.API_HASH,
    bot_token=Vars.VIDMERGEBOT_TOKEN,
    sleep_threshold=Vars.SLEEP_THRESHOLD,
    workers=Vars.WORKERS,
)
