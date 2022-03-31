from aiohttp import web
from aiohttp_jinja2 import setup as setup_jinja2
from jinja2 import FileSystemLoader
from WebStreamer.server.stream_routes import routes


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    setup_jinja2(
        web_app,
        enable_async=True,
        loader=FileSystemLoader("/app/WebStreamer/html/templates"),
    )
    web_app.add_routes(routes)
    return web_app
