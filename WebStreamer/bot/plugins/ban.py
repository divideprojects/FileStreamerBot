from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from WebStreamer.bot import StreamBot
from WebStreamer.vars import Vars


@StreamBot.on_callback_query(filters.regex("^ban_"))
async def ban_user(c: StreamBot, q: CallbackQuery):
    """
    Ban a user from using the bot
    :param c: pyrogram.Client
    :param q: pyrogram.types.CallbackQuery
    """
    user_id = int(q.data.split("_", 1)[1])
    await c.ban_chat_member(Vars.AUTH_CHANNEL, user_id)
    await q.answer("User Banned from Updates Channel!", show_alert=True)


@StreamBot.on_message(
    filters.command("ban") & filters.private & filters.user(Vars.OWNER_ID),
)
async def ban_user_cmd(c: StreamBot, m: Message):
    """
    Ban a user from using the bot
    :param c: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    user_id = m.text.split(" ", 1)[1]
    # check if user_id has space in between
    if len(user_id.split(" ")) == 1:
        await c.ban_chat_member(Vars.AUTH_CHANNEL, user_id)
        await m.reply_text(f"User '{user_id}' Banned from Updates Channel!")
        return
    # error if user_id has space in between
    await m.reply_text(
        "Multiple User IDs given!\nOnly one user can be banned at a time!",
    )
