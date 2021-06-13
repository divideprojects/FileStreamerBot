from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from WebStreamer.bot import StreamBot
from WebStreamer.logger import LOGGER
from WebStreamer.utils.custom_filters import user_check
from WebStreamer.utils.database import Database
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.vars import Var
from pyromod.helpers import ikb

db = Database(Var.DATABASE_URL, "filestreambot")

msg_text = """
<b><i><u>Link Generated!!</u></i></b>
<b>📂 Name:</b> <i>{}</i>
<b>📦 Size:</b> <i>{}</i>
<b>📥 Download:</b> <i>{}</i>

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
    try:
        log_msg = await m.forward(chat_id=Var.LOG_CHANNEL)
        user_id = m.from_user.id
        stream_link = (
            f"https://{Var.FQDN}/{log_msg.message_id}"
            if Var.ON_HEROKU or Var.NO_PORT
            else f"http://{Var.FQDN}:{Var.PORT}/{log_msg.message_id}"
        )
        await db.add_download(user_id, stream_link)

        doc = m.document or m.audio or m.video
        file_size, file_name = None, None
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
            text=f"FloodWait {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={user_id})\n\n<b>User ID:</b> <code>{str(user_id)}</code>",
            disable_web_page_preview=True,
        )
