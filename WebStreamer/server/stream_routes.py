from math import ceil
from mimetypes import guess_type
from secrets import token_hex
from time import time
from typing import Dict, Union

from aiohttp import web
from aiohttp_jinja2 import template
from pypers.formatters import Formatters

from WebStreamer import StartTime
from WebStreamer.bot import (
    AlitaBetaBot,
    DivkixBot,
    DPWatermarkBot,
    GoFilterBot,
    MissAliTaBot,
    PremiumAccountsRobot,
    StreamBot,
    VidMergeBot,
)
from WebStreamer.db import Downloads, Users
from WebStreamer.logger import LOGGER
from WebStreamer.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from WebStreamer.vars import Vars

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def index_handler(_) -> web.StreamResponse:
    """
    Index Handler for WebStreamer, the '/' route.
    """
    return web.json_response(
        {
            "status": "Active",
            "maintainer": "DivideProjects",
            "uptime": Formatters.time_formatter(time() - StartTime),
            "bot_username": "GetPublicLink_Robot",
            "bot_link": "https://t.me/GetPublicLink_Robot",
        },
    )


# custom download page
@routes.get("/download-file-{random_link}")
@template("download_page.html")
async def stream_handler(request) -> Union[web.StreamResponse, Dict[str, str]]:
    """
    Stream Handler for WebStreamer, the '/download-file-*' route.
    :param request: Request object
    :return: StreamResponse object or a dict with appropriate data
    """
    try:
        random_link = request.match_info["random_link"]

        # check if user is banned
        if await Users().is_banned(random_link.split("-")[1]):
            # user_id is the second part of the random_link separated by '-'
            # if user is banned, return 403
            return web.json_response(
                {
                    "status": "user_banned",
                    "maintained_by": "@DivideProjects",
                    "telegram_bot": "@GetPublicLink_Robot",
                },
                status=403,
            )

        # get the actual link
        real_link = await Downloads().get_actual_link(random_link)
        return {"download_link": Vars.URL + real_link}
    except ValueError as ef:
        LOGGER.error(ef)
        raise web.HTTPNotFound


# actual download link
@routes.get("/{real_link}")
async def stream_handler(request) -> web.StreamResponse:
    """
    Stream Handler for WebStreamer, the '/{real_link}' route.
    :param request: Request object
    :return: StreamResponse object
    """
    try:
        real_link = request.match_info["real_link"]
        message_id, valid, valid_upto = await Downloads().get_msg_id(real_link)
        if not valid:
            if int(message_id) == 0:
                return web.json_response(
                    {
                        "status": "not found",
                        "maintained_by": "@DivideProjects",
                        "telegram_bot": "@GetPublicLink_Robot",
                    },
                    status=404,
                )
            return web.json_response(
                {
                    "status": "download_link_expired",
                    # NOTE: Only 'never' is allowed for owners
                    "expired_time": str(valid_upto) if valid_upto != -1 else "never",
                    "maintained_by": "@DivideProjects",
                    "telegram_bot": "@GetPublicLink_Robot",
                },
                status=410,
            )
        return await media_streamer(request, message_id)
    except ValueError as ef:
        LOGGER.error(ef)
        raise web.HTTPNotFound


async def media_streamer(request, message_id: int) -> web.StreamResponse:
    """
    Media Streamer for WebStreamer, the '/{real_link}' route.
    :param request: Request object
    :param message_id: Message ID of the file to be streamed
    :return: StreamResponse object
    """
    range_header = request.headers.get("Range", 0)
    media_msg = await StreamBot.get_messages(Vars.LOG_CHANNEL, message_id)
    file_properties = await TGCustomYield(
        [
            MissAliTaBot,
            DivkixBot,
            PremiumAccountsRobot,
            GoFilterBot,
            AlitaBetaBot,
            DPWatermarkBot,
            VidMergeBot,
        ],
    ).generate_file_properties(
        media_msg,
    )
    file_size = file_properties.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = request.http_range.stop or file_size - 1

    req_length = until_bytes - from_bytes

    new_chunk_size = await chunk_size(req_length)
    offset = await offset_fix(from_bytes, new_chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = (until_bytes % new_chunk_size) + 1
    part_count = ceil(req_length / new_chunk_size)
    body = TGCustomYield().yield_file(
        media_msg,
        offset,
        first_part_cut,
        last_part_cut,
        part_count,
        new_chunk_size,
    )

    file_name = file_properties.file_name or f"{token_hex(2)}.jpeg"
    mime_type = file_properties.mime_type or f"{guess_type(file_name)}"

    return_resp = web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": mime_type,
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Disposition": f'attachment; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )

    if return_resp.status == 200:
        return_resp.headers.add("Content-Length", str(file_size))

    return return_resp
