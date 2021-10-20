from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from WebStreamer.utils.ikb import ikb

from WebStreamer.bot import StreamBot
from WebStreamer.utils.custom_filters import user_check

PMTEXT = """
Hi, {} !
I'm File streamer Bot!

<i>Click on the below buttons to learn more!</i>

<b><u><i>WARNING:</i></u></b> <i>NSFW Content will lead to ban!</i>
"""

HELPTEXT = """
<b>Commands:</b>
/start: <i>Start the bot.</i>
/help: <i>Show this message again.</i>

Just Send or Forward me any file or media, I'll give you a direct download link for it!
"""

ABOUT = """
Hi there, I'm an Advanced and Fast File Streamer Bot! Made with love from @DivideProjectsDiscussion using pyrogram :)

<b><u>Here are the few questions that are answered:</u></b>

<b>1) The direct link given by me is valid for how much time ?</b>
<u>Ans</u>) <i>The direct link to telegram files are valid for upto 24 hours!</i>

<b>2) How to use me ?</b>
<u>Ans</u>) <i>Read /help and if you get some issues join @DivideProjectsDiscussion and tell what issues are you facing to use me :)</i>

<b>3) Is NSFW allowed ?</b>
<u>Ans</u>) <i>NOOOOOOO !!</i>

<b>4) You want to contact support for something ?</b>
<u>Ans</u>) <i>You can Contact My devs or if you need any help or found any bugs report it at @DivideProjectsDiscussion asap !</i>

<i><u>Atlast, Thanks for using me!!</u></i>
"""


@StreamBot.on_message(
    filters.command("start") & filters.private & ~filters.edited & user_check,
)
async def start(_, m: Message):
    return await m.reply_text(
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
    return await m.reply_text(
        HELPTEXT,
        parse_mode="HTML",
    )


@StreamBot.on_callback_query()
async def button(_, cmd: CallbackQuery):
    cb_data = cmd.data
    if "aboutbot" in cb_data:
        await cmd.message.edit(
            text=ABOUT,
            parse_mode="HTML",
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
