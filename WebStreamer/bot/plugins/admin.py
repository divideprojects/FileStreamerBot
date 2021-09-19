from asyncio import sleep
from datetime import datetime, timedelta
from os import remove
from random import choice
from string import ascii_letters
from time import time

from aiofiles import open as open_aiofiles
from pyrogram import filters
from pyrogram.types import Message

from WebStreamer.bot import StreamBot
from WebStreamer.db import Downloads, Users
from WebStreamer.utils.broadcast_helper import send_msg
from WebStreamer.vars import Var

broadcast_ids = {}


@StreamBot.on_message(
    filters.command("status")
    & filters.private
    & filters.user(Var.OWNER_ID)
    & ~filters.edited,
)
async def status(_, m: Message):
    dl = Downloads()
    total_users = await Users().total_users_count()
    (
        valid_downloads_list,
        num_downloads,
        expired_downloads,
        valid_num_downloads,
    ) = await dl.valid_downloads_list()
    async with open_aiofiles("download_list.txt", "w") as valid_dl_list:
        valid_downloads = ""
        for dl in valid_downloads_list:
            valid_downloads += (
                f"UserID: {dl['user_id']}\n"
                f"Link: {dl['link']}\n"
                f"Expire: {dl['valid_upto'].strftime('%m/%d/%Y, %H:%M:%S')}\n\n"
            )
        await valid_dl_list.write(valid_downloads)
    await m.reply_document(
        "download_list.txt",
        caption=(
            f"<b>Total Users:</b> <code>{total_users}</code>\n"
            f"<b>Total Downloads:</b> <code>{num_downloads}</code>\n"
            f"<b>Active Downloads:</b> <code>{valid_num_downloads}</code>\n"
            f"<b>Expired Downloads:</b> <code>{expired_downloads}</code>"
        ),
        quote=True,
    )
    return


@StreamBot.on_message(
    filters.command("broadcast")
    & filters.private
    & filters.user(Var.OWNER_ID)
    & filters.reply
    & ~filters.edited,
)
async def broadcast_(_, m: Message):
    all_users = await Users().get_all_users()
    broadcast_msg = m.reply_to_message
    while True:
        broadcast_id = "".join(choice(ascii_letters) for _ in range(3))
        if not broadcast_ids.get(broadcast_id):
            break
    out = await m.reply_text(
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
        async for user in all_users:
            sts, msg = await send_msg(user_id=int(user["id"]), message=broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await Users().delete_user(user["id"])
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
    await out.delete()
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
