from requests import get

from WebStreamer.logger import LOGGER
from WebStreamer.vars import Vars


def ping_server():
    k = get(f"https://ping-pong-sn.herokuapp.com/pingback?link={Vars.URL}").json()
    if not k.get("error"):
        LOGGER.info(
            f"KeepAliveService: Pinged {Vars.FQDN} with response: {k['message']}",
        )
    else:
        LOGGER.error("Couldn't Ping the Server!")
