from asyncio import sleep

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message
from pyromod.helpers import ikb

from WebStreamer.logger import LOGGER
from WebStreamer.utils.database import Database
from WebStreamer.vars import Var


def ban_kb(user_id: int):
    kb = ikb([[("Ban User", f"ban_{user_id}")]]) if user_id != Var.OWNER_ID else None
    return kb


# -- Constants --  #
NO_JOIN_START_TEXT = """
You must be a member of the Channel to use the bot, \
this step ensure that you know about bot status \
and latest updates.
This step is also taken to prevent misuse of bot as \
all users will be logged.
"""
# -- Constants --  #

DEV_LEVEL = [int(Var.OWNER_ID)]
db = Database(Var.DATABASE_URL, "filestreambot")


async def user_check_filter(_, c: Client, m: Message):
    user_id = m.from_user.id
    # To check if user is new
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id)
        await c.send_message(
            Var.LOG_CHANNEL,
            f"#NEW_USER: \n\nNew User [{m.from_user.first_name}](tg://user?id={user_id}) started bot!!",
            reply_markup=ban_kb(user_id),
        )

    # if user is dev or owner, return true
    if user_id in DEV_LEVEL:
        LOGGER.info("Dev User detected, skipping check")
        return True

    try:
        invite_link = await c.create_chat_invite_link(int(Var.AUTH_CHANNEL))
    except FloodWait as e:
        await sleep(e.x)
        return

    try:
        user_member = await c.get_chat_member(int(Var.AUTH_CHANNEL), user_id)
        # If user is banned in Channel
        if user_member.status == "kicked":
            await m.reply_text(
                (
                    "Sorry, You are Banned!\n"
                    f"Contact my [Support Group](https://t.me/DivideProjectsDiscussion) to know more."
                ),
            )
            return
        if user_member:
            LOGGER.info(f"User {user_id} already a member of chat, passing check!")
            return True

    except UserNotParticipant:
        await m.reply_text(
            NO_JOIN_START_TEXT,
            disable_web_page_preview=True,
            parse_mode="markdown",
            reply_markup=ikb([[("Join Channel", invite_link.invite_link, "url")]]),
        )
        return False
    except Exception as ef:
        LOGGER.error(f"Error: {ef}")
        await m.reply_text(
            f"Something went Wrong. Contact my [Support Group](https://t.me/DivideProjectsDiscussion).",
            disable_web_page_preview=True,
        )
        return


user_check = filters.create(user_check_filter)
