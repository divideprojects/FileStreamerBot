from asyncio import sleep
from secrets import token_urlsafe
from time import time

from cachetools import TTLCache
from pypers.formatters import Formatters
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, Message

from WebStreamer.bot import StreamBot
from WebStreamer.db import Downloads
from WebStreamer.db.users import Users
from WebStreamer.logger import LOGGER
from WebStreamer.utils.human_readable import humanbytes
from WebStreamer.utils.ikb import ikb
from WebStreamer.utils.joinCheck import joinCheck
from WebStreamer.vars import Vars

msg_text = """
<b>Link Generated!</b>

<b>📂 Name:</b> <i>{}</i>
<b>📦 Size:</b> <i>{}</i>
<b>📥 Download link:</b> {}

<b>🚸 Note: This link will expire after {}!</b>

<i>@DivideProjects </i>
"""

log_channel_msg = """
<b>Requested By:</b> {}
<b>User ID:</b> <code>{}</code>
<b>Download Link:</b> {}
<b>Direct Link:</b> {}
<b>Expires in:</b> {}
"""

# Cache for storing how many times a user has used the bot, takes number of mimuted from Vars
ttl_dict = TTLCache(maxsize=512, ttl=(Vars.FLOODCONTROL_TIME_MINUTES * 60))


@StreamBot.on_message(
    filters.private
    & (filters.document | filters.video | filters.audio | filters.photo),
    group=4,
)
@joinCheck()  # Check if user has joined the channel
async def private_receive_handler(c: Client, m: Message):
    """
    Handler for receiving files in private
    :param c: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    user = m.from_user
    user_id = user.id
    users_db = Users()
    user_expire_time = await users_db.get_expire_time(user_id)

    if (user_id != Vars.OWNER_ID) or (Vars.FLOODCONTROL_TIME_MINUTES != 0):
        # spam check
        if user_id in ttl_dict.keys():
            await m.reply_text(
                f"Flood control active, please wait {int(ttl_dict[user_id] - time())} seconds!",
            )
            return

    wait_text = await m.reply_text(
        """
Please wait while I process your file ...
<b>Do not send any other media file till I generate the link for the current file!</b>
""",
        quote=True,
    )
    try:
        log_msg = await m.forward(chat_id=Vars.LOG_CHANNEL)
        random_url = token_urlsafe(20) + "-" + str(user_id)
        # prepend 'download-file-' at to identify download page
        stream_link = (
            f"https://{Vars.FQDN}/download-file-{random_url}"
            if Vars.ON_HEROKU or Vars.NO_PORT
            else f"https://{Vars.FQDN}:{Vars.PORT}/download-file-{random_url}"
        )

        __direct_link = await Downloads().add_download(
            log_msg.id,
            random_url,
            user_id,
            user_expire_time,
        )
        direct_link = (
            f"https://{Vars.FQDN}/{__direct_link}"
            if Vars.ON_HEROKU or Vars.NO_PORT
            else f"https://{Vars.FQDN}:{Vars.PORT}/{__direct_link}"
        )

        # Only get file size if it's a file, different for photos
        doc = m.document or m.audio or m.video
        if doc:
            file_size = humanbytes(doc.file_size)
            file_name = doc.file_name
        else:
            file_size = "nil"
            file_name = "photo"

        await log_msg.reply_text(
            text=log_channel_msg.format(
                user.mention,
                user_id,
                stream_link,
                direct_link,
                # NOTE: Only 'never' is allowed for owners
                Formatters.time_formatter(user_expire_time)
                if user_expire_time != -1
                else "Never",
            ),
            disable_web_page_preview=True,
            quote=True,
            reply_markup=ikb([[("Ban User", f"ban_{user_id}")]]),
        )

        await wait_text.edit_text(
            text=msg_text.format(
                file_name,
                file_size,
                stream_link,
                Formatters.time_formatter(user_expire_time)
                if user_expire_time != -1
                else "Never",
            ),
            disable_web_page_preview=True,
            reply_markup=ikb(
                [
                    [("Download 📥", stream_link, "url")],
                    [("Delete ❌", f"delete_url.{random_url}")],
                ],
            ),
        )

        # user should wait for 5 minutes before sending another file
        ttl_dict[user_id] = time() + int(5 * 60)

    except FloodWait as e:
        LOGGER.info(f"Sleeping for {str(e.value)}s")
        await sleep(e.value)
        await c.send_message(
            chat_id=Vars.LOG_CHANNEL,
            text=(
                f"FloodWait {e.value}s from {user.mention}\n\n"
                f"<b>User ID:</b> <code>{user_id}</code>"
            ),
            disable_web_page_preview=True,
        )


@StreamBot.on_callback_query(filters.regex("^delete_url."))
async def delete_download(_, q: CallbackQuery):
    """
    Delete the download link from the database using a callback query
    :param _: pyrogram.Client
    :param q: pyrogram.types.CallbackQuery
    """
    user_id = q.from_user.id
    msg = q.message
    url = str(q.data.split(".")[-1])
    deleted = await Downloads().delete_download(url, user_id)

    _text = (
        "<b>Deleted the file permanently from my server!</b>"
        if deleted
        else "<b>Error:</b>\nCould not delete download, please contact my developers!"
    )
    await msg.edit_text(_text)
    await q.answer("Operation Complete!")
