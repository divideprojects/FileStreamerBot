from pyrogram import filters
from pyrogram.types import CallbackQuery

from WebStreamer.bot import StreamBot
from WebStreamer.vars import Vars


@StreamBot.on_callback_query(filters.regex("^ban_"))
async def ban_user(c: StreamBot, q: CallbackQuery):
    """
    Ban a user from using the bot
    """
    user_id = int(q.data.split("_", 1)[1])
    await c.ban_chat_member(Vars.AUTH_CHANNEL, user_id)
    await q.answer("User Banned from Updates Channel!", show_alert=True)
