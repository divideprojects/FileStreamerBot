from math import ceil, floor
from mimetypes import guess_type
from time import time
from typing import Any

from aiohttp import web
from aiohttp_jinja2 import template
from pypers.formatters import Formatters

from WebStreamer import StartTime
from WebStreamer.bot import multi_clients, work_loads
from WebStreamer.db.downloads import Downloads
from WebStreamer.db.users import Users
from WebStreamer.logger import LOGGER
from WebStreamer.utils.custom_dl import ByteStreamer
from WebStreamer.utils.file_properties import get_name
from WebStreamer.utils.helpers import extract_user_id_from_random_link
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
            "connected_bots": len(multi_clients),
            "loads": {
                "bot" + str(c + 1): l
                for c, (_, l) in enumerate(
                    sorted(work_loads.items(), key=lambda x: x[1], reverse=True),
                )
            },
        },
    )


# custom download page
# TODO: Remove this function after 1 month (2021-08-01) because it's not used anywhere now
@routes.get("/download-file-{random_link}")
@template("download_page.html")
async def stream_handler(request) -> web.StreamResponse | dict[str, str]:
    """
    Stream Handler for WebStreamer, the '/download-file-*' route.
    :param request: Request object
    :return: StreamResponse object or a dict with appropriate data
    """
    try:
        random_link = request.match_info["random_link"]
        user_id = extract_user_id_from_random_link(random_link)

        # check if user is banned
        if await Users().is_banned(user_id):
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

        def json_response(
            custom_repsonse: dict[str | Any, str | Any],
            status_code: int = 200,
        ) -> dict[str | Any, str | Any]:
            """
            Return a json response with appropriate data
            :return: Dict with appropriate data
            """
            return web.json_response(
                {
                    "maintained_by": "@DivideProjects",
                    "telegram_bot": "@GetPublicLink_Robot",
                }.update(custom_repsonse),
                status=status_code,
            )

        # check if user is banned
        # user_id is the second part of the random_link separated by '-'
        # if user is banned, return 403
        try:
            if await Users().is_banned(real_link.split("-")[1]):
                return json_response({"status": "user_banned"}, 403)
        # NOTE: IndexError is raised when old link is used to validate
        except IndexError:
            pass

        message_id, valid, valid_upto = await Downloads().get_msg_id(real_link)
        if not valid:
            if int(message_id) == 0:
                return json_response({"status": "not found"}, 404)

            # response code 410 means that the resource is no longer available, expired
            return json_response(
                {
                    "status": "download_link_expired",
                    # NOTE: Only 'never' is allowed for owners
                    "expired_time": str(valid_upto) if valid_upto != -1 else "never",
                },
                410,
            )
        return await media_streamer(request, message_id)
    except ValueError as ef:
        LOGGER.error(ef)
        raise web.HTTPNotFound


class_cache = {}


async def media_streamer(request: web.Request, message_id: int):
    range_header = request.headers.get("Range", 0)

    index = min(work_loads, key=work_loads.get)
    faster_client = multi_clients[index]

    if Vars.MULTI_CLIENT:
        LOGGER.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        LOGGER.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        LOGGER.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    LOGGER.debug("before calling get_file_properties")
    file_id = await tg_connect.get_file_properties(message_id)
    LOGGER.debug("after calling get_file_properties")

    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = ceil(until_bytes / chunk_size) - floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id,
        index,
        offset,
        first_part_cut,
        last_part_cut,
        part_count,
        chunk_size,
    )
    mime_type = file_id.mime_type
    file_name = get_name(file_id)
    disposition = "attachment"

    if not mime_type:
        mime_type = guess_type(file_name)[0] or "application/octet-stream"

    if "video/" in mime_type or "audio/" in mime_type or "/html" in mime_type:
        disposition = "inline"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
        },
    )
