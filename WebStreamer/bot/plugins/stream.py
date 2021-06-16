from asyncio import sleep
from secrets import token_urlsafe

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from pyromod.helpers import ikb

from WebStreamer.bot import StreamBot
from WebStreamer.db import Downloads
from WebStreamer.logger import LOGGER
from WebStreamer.utils.custom_filters import user_check
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.vars import Var

msg_text = """
<b><i><u>Link Generated!!</u></i></b>

<b><u>📂 Name:</u></b> <i>{}</i>\n
<b><u>📦 Size:</u></b> <i>{}</i>\n
<b><u>📥 Download link:</u></b> <i>{}</i>

<b>🚸 Note: This link will expire in 24 hours!</b>

<i>@DivideProjects </i>
"""


@StreamBot.on_message(
    filters.private
    & (filters.document | filters.video | filters.audio)
    & ~filters.edited
    & user_check,
    group=4,
)
async def private_receive_handler(c: Client, m: Message):
    user_id = m.from_user.id
    
    wait = await m.reply_text("Please wait while i process the file...")
    try:
        log_msg = await m.forward(chat_id=Var.LOG_CHANNEL)
        random_url = token_urlsafe(log_msg.message_id)
        stream_link = (
            f"https://{Var.FQDN}/{random_url}"
            if Var.ON_HEROKU or Var.NO_PORT
            else f"https://{Var.FQDN}:{Var.PORT}/{random_url}"
        )

        await Downloads().add_download(log_msg.message_id, random_url, user_id)

        doc = m.document or m.audio or m.video
        file_size = f"{humanbytes(doc.file_size)}"
        file_name = doc.file_name

        await log_msg.reply_text(
            text=(
                f"<b>Requested By:</b> [{m.from_user.first_name}](tg://user?id={user_id})\n"
                f"<b>User ID:</b> <code>{user_id}<code>\n"
                f"<b>Download Link:</b> {stream_link}"
            ),
            disable_web_page_preview=True,
            quote=True,
        )
        await wait.delete()
        await m.reply_text(
            text=msg_text.format(file_name, file_size, stream_link),
            disable_web_page_preview=True,
            reply_markup=ikb([[("Download 📥", stream_link, "url")]]),
            quote=True,
        )
    except FloodWait as e:
        LOGGER.info(f"Sleeping for {str(e.x)}s")
        await sleep(e.x)
        await c.send_message(
            chat_id=Var.LOG_CHANNEL,
            text=f"FloodWait {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={user_id})\n\n<b>User ID:</b> "
            f"<code>{str(user_id)}</code>",
            disable_web_page_preview=True,
        )
