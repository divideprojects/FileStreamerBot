from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyromod.helpers import ikb

from WebStreamer.bot import StreamBot
from WebStreamer.utils.custom_filters import user_check

PMTEXT = """
Hi, {} !!\n\n
<i>I'm File streamer Bot</i>\n
<b>Click on the below buttons to learn more</b>\n
<b>WARNING:</b> <b><u>NSFW Content will lead to ban.</u></b>
"""

HELPTEXT = "Just Send or Forward me any file or media, I'll give you a direct download link for it!"

ABOUT = """
Hi there I'm an Advanced and Fast File Streamer Bot!

I can give you a direct link to telegram files for upto 24 hours!

You can Contact My devs or if you need any help or find any bugs at @DivideProjectsDiscussion
Thanks for using me!!
"""


@StreamBot.on_message(
    filters.command("start") & filters.private & ~filters.edited & user_check,
)
async def start(_, m: Message):
    await m.reply_text(
        text=PMTEXT.format(m.chat.first_name),
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=ikb([[("Support Group", "https://t.me/DivideProjectsDiscussion", "url"),
                           ("Channel", "https://t.me/DivideProjects", "url")],
                          [("About Me", "aboutbot"), ("Help", "helptext")]]),
    )


@StreamBot.on_message(
    filters.command("help") & filters.private & ~filters.edited & user_check,
)
async def help_handler(_, m: Message):
    await m.reply_text(
        "<i>Send or Forward me any file or media, I'll give you a direct download link for it!</i>",
        parse_mode="HTML",
    )


@StreamBot.on_callback_query()
async def button(_, cmd: CallbackQuery):
    cb_data = cmd.data
    if "aboutbot" in cb_data:
        await cmd.message.edit(
            text=ABOUT,
            parse_mode="MARKDOWN",
            disable_web_page_preview=True,
            reply_markup=ikb(
                [
                    [
                        ("Go to Home", "gotohome"),
                        ("Help", "helptext"),
                    ]
                ]
            ),
        )
    elif "helptext" in cb_data:
        await cmd.message.edit(
            text=HELPTEXT,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=ikb(
                [
                    [
                        ("About Me", "aboutbot"),
                        ("Back", "gotohome"),
                    ]
                ]
            ),
        )
    elif "gotohome" in cb_data:
        await cmd.message.edit(
            text=PMTEXT.format(cmd.message.chat.first_name),
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=ikb(
                [
                    [
                        (
                            "Support Group",
                            "https://t.me/DivideProjectsDiscussion", "url"
                        ),
                        (
                            "Channel",
                            "https://t.me/DivideProjects", "url"
                        )
                    ],
                    [
                        ("About Me", "aboutbot"),
                        ("Help", "helptext")
                    ]
                ]
            ),
        )
    await cmd.answer()
