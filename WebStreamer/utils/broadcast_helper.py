from asyncio import sleep
from traceback import format_exc

from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import Message


async def send_msg(user_id: int, m: Message) -> tuple[int, Message | None | str]:
    """send_msg function to send message to user

    Args:
        user_id (int): user_id to send message
        m (Message): Message to forward

    Returns:
        Tuple[int, Union[Message, None, str]]: status code, status message
    """
    try:
        await m.forward(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await sleep(e.value)
        return send_msg(user_id, m)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as ef:
        return 500, f"{user_id} : {format_exc()}|{ef}\n"
