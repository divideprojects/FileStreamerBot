from pypers.formatters import Formatters
from pyrogram import filters
from pyrogram.types import Message

from WebStreamer.bot import StreamBot
from WebStreamer.db.users import Users


@StreamBot.on_message(
    filters.command("expire") & filters.private,
)
async def expire_settings(_, m: Message):
    """
    Expire settings command handler
    :param c: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    user_id = m.from_user.id
    args = m.text.split(" ", 1)
    users_db = Users()
    reply_text = ""
    match len(args):
        case 1:
            current_expire_time = await users_db.get_user_expire_time(user_id)
            reply_text = f"Your stream links expire after {Formatters.time_formatter(current_expire_time)}."
        case 2:
            time = args[1]
            seconds_time = Formatters.get_time_in_seconds(time)
            if seconds_time == -1:
                reply_text = "Invalid time format. Send a time in m/h/d/w format to set the expire time for your stream links."
            else:
                reply_text = f"Your stream links will expire after {time}."
                await users_db.set_user_expire_time(user_id, seconds_time)
        case _:
            reply_text = "Invalid command usage. Send /expire to get your current expire time or send /expire <time> to set your expire time."
    await m.reply_text(reply_text)
