from pypers.formatters import Formatters
from pyrogram import filters
from pyrogram.types import Message

from WebStreamer.bot import StreamBot
from WebStreamer.db.downloads import Downloads
from WebStreamer.db.users import Users
from WebStreamer.vars import Vars


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
            current_expire_time = await users_db.get_expire_time(user_id)
            reply_text = (
                f"Your stream links expire after {Formatters.time_formatter(current_expire_time)}."
                if current_expire_time != -1
                else "Your stream links will never expire."
            )
        case 2:
            time = args[1].lower()
            # NOTE: Only 'never' is allowed for owners
            if args[1] == "never" and user_id == Vars.OWNER_ID:
                await users_db.set_expire_time(user_id, -1)
                reply_text = "Your stream links will never expire."
            else:
                seconds_time = Formatters.get_time_in_seconds(time)
                if seconds_time == -1:
                    reply_text = "Invalid time format. Send a time in m/h/d/w format to set the expire time for your stream links."
                else:
                    reply_text = f"Your stream links will expire after {time}."
                    await users_db.set_expire_time(user_id, seconds_time)
        case _:
            reply_text = "Invalid command usage. Send /expire to get your current expire time or send /expire <time> to set your expire time."
    await m.reply_text(reply_text)


@StreamBot.on_message(
    filters.command("mylinks") & filters.private,
)
async def my_links(_, m: Message):
    """
    Mylinks command handler
    :param c: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    user_id = m.from_user.id
    downloads_db = Downloads()
    valid_links = await downloads_db.get_user_active_links(user_id)
    if not valid_links:
        await m.reply_text("You have no active links.")
        return
    reply_text = "Your active links:"
    for link in valid_links:
        reply_text += "\n - " + link + f" | /delete_link_{link}"
    await m.reply_text(reply_text)
    return


@StreamBot.on_message(
    filters.regex(r"^/delete_link_(.*)") & filters.private,
)
async def delete_link(_, m: Message):
    """
    Delete link command handler to delete a link
    :param c: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    user_id = m.from_user.id
    downloads_db = Downloads()
    delete_success = await downloads_db.delete_download(m.matches[0].group(1), user_id)
    if not delete_success:
        return await m.reply_text("Unable to delete the link.")
    return await m.reply_text("Link deleted successfully.")
