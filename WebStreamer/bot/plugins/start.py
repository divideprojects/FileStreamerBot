from pyrogram import filters
from pyrogram.types import Message

from WebStreamer.bot import StreamBot
from WebStreamer.utils.custom_filters import user_check


@StreamBot.on_message(
    filters.command("start") & filters.private & ~filters.edited & user_check,
)
async def start(_, m: Message):
    await m.reply_text(
        (
            "<i>Hi, I'm File Streamer Bot</i>\n"
            "<i>Click on /help to learn more</i>\n"
            "<b>WARNING:</b> <b>NSFW Content will lead to ban.</b>"
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@StreamBot.on_message(
    filters.command("help") & filters.private & ~filters.edited & user_check,
)
async def help_handler(_, m: Message):
    await m.reply_text(
        "<i>Send or Forward me any file or media, I'll give you a direct download link for it!</i>",
    )
