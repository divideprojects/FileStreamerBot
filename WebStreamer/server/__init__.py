from aiohttp import web

from WebStreamer.server.stream_routes import routes


def web_server() -> web.Application:
    """Create the web server and return it

    Returns:
        web.Application: The web server
    """
    web_app = web.Application(client_max_size=30000000)
    # add the routes to the web app
    web_app.add_routes(routes)
    return web_app
