from asyncio import sleep
from random import randint
from secrets import token_urlsafe
from time import time

from cachetools import TTLCache
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from pyshorteners import Shortener

from WebStreamer.bot import StreamBot
from WebStreamer.db import Downloads
from WebStreamer.logger import LOGGER
from WebStreamer.utils.custom_filters import user_check
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.ikb import ikb
from WebStreamer.vars import Var

msg_text = """
<b><i><u>Link Generated!!</u></i></b>

<b><u>📂 Name:</u></b> <i>{}</i>\n
<b><u>📦 Size:</u></b> <i>{}</i>\n
<b><u>📥 Download link:</u></b> <i>{}</i>

<b>🚸 Note: This link will expire after 24 hours!</b>

<i>@DivideProjects </i>
"""

ttl_dict = TTLCache(maxsize=512, ttl=(5 * 60))


@StreamBot.on_message(
    filters.private
    & (filters.document | filters.video | filters.audio | filters.photo)
    & ~filters.edited
    & user_check,
    group=4,
)
async def private_receive_handler(c: Client, m: Message):
    user_id = m.from_user.id

    # spam check
    if user_id in ttl_dict.keys():
        await m.reply_text(
            f"Flood control active, please wait {int(ttl_dict[user_id]-time())} seconds!",
        )
        return

    wait = await m.reply_text(
        """
Please wait while I process your file ...
<b>Do not send any other media file till i give you the link for the current given file !</b>
""",
        quote=True,
    )
    try:
        log_msg = await m.forward(chat_id=Var.LOG_CHANNEL)
        random_url = token_urlsafe(randint(32, 64))
        stream_link = (
            f"https://{Var.FQDN}/{random_url}"
            if Var.ON_HEROKU or Var.NO_PORT
            else f"https://{Var.FQDN}:{Var.PORT}/{random_url}"
        )

        await Downloads().add_download(log_msg.message_id, random_url, user_id)

        # Only get file size if it's a file
        doc = m.document or m.audio or m.video
        if doc:
            file_size = humanbytes(doc.file_size)
            file_name = doc.file_name
        else:
            file_size = humanbytes(m.photo[-1].file_size)
            file_name = m.photo[-1].file_name

        s = Shortener()
        short_link = s.dagd.short(stream_link)

        await log_msg.reply_text(
            text=(
                f"<b>Requested By:</b> [{m.from_user.first_name}](tg://user?id={user_id})\n"
                f"<b>User ID:</b> <code>{user_id}</code>\n"
                f"<b>Download Link:</b> {short_link}"
            ),
            disable_web_page_preview=True,
            quote=True,
            reply_markup=ikb([[("Ban User", f"ban_{user_id}")]]),
        )

        await wait.edit_text(
            text=msg_text.format(file_name, file_size, short_link),
            disable_web_page_preview=True,
            reply_markup=ikb([[("Download 📥", short_link, "url")]]),
        )

        # user should wait for 5 minutes before sending another file
        ttl_dict[user_id] = time() + int(5 * 60)

    except FloodWait as e:
        LOGGER.info(f"Sleeping for {str(e.x)}s")
        await sleep(e.x)
        await c.send_message(
            chat_id=Var.LOG_CHANNEL,
            text=f"FloodWait {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={user_id})\n\n<b>User ID:</b> "
            f"<code>{str(user_id)}</code>",
            disable_web_page_preview=True,
        )
