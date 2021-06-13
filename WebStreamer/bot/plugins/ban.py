from pyrogram import filters
from pyrogram.types import CallbackQuery

from WebStreamer.bot import StreamBot
from WebStreamer.vars import Var


@StreamBot.on_callback_query(filters.regex("^ban_"))
async def ban_user(c: StreamBot, q: CallbackQuery):
    user_id = int(q.data.split("_", 1)[1])
    await c.kick_chat_member(Var.AUTH_CHANNEL, user_id)
    await q.answer("User Banned from Updates Channel!", show_alert=True)
