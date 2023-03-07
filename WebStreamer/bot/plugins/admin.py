from asyncio import sleep
from datetime import timedelta
from os import remove
from random import choice
from string import ascii_letters
from time import time

from aiofiles import open as open_aiofiles
from pyrogram import filters
from pyrogram.types import Message

from WebStreamer.bot import StreamBot
from WebStreamer.db.downloads import Downloads
from WebStreamer.db.users import Users
from WebStreamer.utils.broadcast_helper import send_msg
from WebStreamer.vars import Vars

broadcast_ids = {}


@StreamBot.on_message(
    filters.command("stats") & filters.private & filters.user(Vars.OWNER_ID),
)
async def stats(_, m: Message):
    """
    Get stats of the bot, number of users, number of files, etc.
    :param _: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    total_users = await Users().total_users_count()
    (
        _,
        num_downloads,
        expired_downloads,
        valid_num_downloads,
    ) = await Downloads().valid_downloads_list()
    await m.reply_text(
        f"<b>Total Users:</b> <code>{total_users}</code>"
        f"\n<b>Total Downloads:</b> <code>{num_downloads}</code>"
        f"\n<b>Active Downloads:</b> <code>{valid_num_downloads}</code>"
        f"\n<b>Expired Downloads:</b> <code>{expired_downloads}</code>",
        quote=True,
    )
    return


@StreamBot.on_message(
    filters.command("downloadlist") & filters.private & filters.user(Vars.OWNER_ID),
)
async def downloadList(_, m: Message):
    """
    Get the list of all downloads
    :param _: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    dl = Downloads()
    filename = "downloadList.txt"
    (
        valid_downloads_list,
        num_downloads,
        expired_downloads,
        valid_num_downloads,
    ) = await dl.valid_downloads_list()
    async with open_aiofiles(filename, "w") as valid_dl_list:
        valid_downloads = ""
        for dl in valid_downloads_list:
            valid_downloads += (
                f"UserID: {dl['user_id']}\n"
                f"Link: {dl['link']}\n"
                f"Expire: {dl['valid_upto'].strftime('%m/%d/%Y, %H:%M:%S')}\n\n"
            )
        await valid_dl_list.write(valid_downloads)
    await m.reply_document(
        filename,
        caption=(
            f"<b>Total Downloads:</b> <code>{num_downloads}</code>\n"
            f"<b>Active Downloads:</b> <code>{valid_num_downloads}</code>\n"
            f"<b>Expired Downloads:</b> <code>{expired_downloads}</code>"
        ),
        quote=True,
    )
    return


@StreamBot.on_message(
    filters.command("userlist") & filters.private & filters.user(Vars.OWNER_ID),
)
async def userlist(_, m: Message):
    """
    Get the list of all users
    :param _: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    users_db = Users()
    total_users_num = await users_db.total_users_count()
    filename = "usersList.txt"
    async with open_aiofiles(filename, "w") as total_user_list:
        total_users = ""
        for user_id in await users_db.get_all_users():
            total_users += str(user_id) + "\n"
        await total_user_list.write(total_users)
    await m.reply_document(
        filename,
        caption=(f"<b>Total Users:</b> <code>{total_users_num}</code>\n"),
        quote=True,
    )
    return


@StreamBot.on_message(
    filters.command("broadcast") & filters.private & filters.user(Vars.OWNER_ID),
)
async def broadcast_(_, m: Message):
    """
    Broadcast a message to all users
    :param _: pyrogram.Client
    :param m: pyrogram.types.Message
    """
    all_users = await Users().get_all_users()
    broadcast_msg = m.reply_to_message
    # only replied msg can be broadcasted
    if not broadcast_msg:
        await m.reply_text("Reply to a message to broadcast.")
        return
    while 1:
        broadcast_id = "".join(choice(ascii_letters) for _ in range(3))
        if not broadcast_ids.get(broadcast_id):
            break
    out_msg = await m.reply_text(
        "Broadcast initiated! You will be notified with log file when all the users are notified.",
    )
    start_time = time()
    total_users = len(all_users)
    done, failed, success = 0, 0, 0
    broadcast_ids[broadcast_id] = dict(
        total=total_users,
        current=done,
        failed=failed,
        success=success,
    )
    async with open_aiofiles("broadcast.txt", "w") as broadcast_log_file:
        for user in all_users:
            sts, msg = await send_msg(user_id=int(user), m=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)

            match sts:
                case 200:
                    success += 1
                case 400:
                    await Users().delete_user(user)
                case _:
                    failed += 1
            done += 1

            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(
                    dict(current=done, failed=failed, success=success),
                )
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    completed_in = timedelta(seconds=int(time() - start_time))
    await sleep(3)
    await out_msg.delete()
    if failed == 0:
        await m.reply_text(
            text=(
                f"broadcast completed in <code>{completed_in}</code>\n\n"
                f"Total users {total_users}.\n"
                f"Total done {done}, {success} success and {failed} failed."
            ),
            quote=True,
        )
    else:
        await m.reply_document(
            document="broadcast.txt",
            caption=(
                f"broadcast completed in <code>{completed_in}</code>\n\n"
                f"Total users {total_users}.\n"
                f"Total done {done}, {success} success and {failed} failed."
            ),
            quote=True,
        )
    remove("broadcast.txt")
