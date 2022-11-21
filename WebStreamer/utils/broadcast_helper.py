from asyncio import sleep
from traceback import format_exc
from typing import Tuple, Union

from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    PeerIdInvalid,
    UserIsBlocked,
)
from pyrogram.types import Message


async def send_msg(user_id: int, m: Message) -> Tuple[int, Union[Message, None, str]]:
    """
    Send message to user using their user_id
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
