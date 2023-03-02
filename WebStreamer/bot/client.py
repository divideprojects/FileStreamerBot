from asyncio import gather, sleep
from os import environ

from pyrogram import Client

from WebStreamer.bot import StreamBot, multi_clients, work_loads
from WebStreamer.logger import LOGGER
from WebStreamer.vars import Vars


async def initialize_clients():
    multi_clients[0] = StreamBot
    work_loads[0] = 0
    all_tokens = {
        c + 1: t
        for c, (_, t) in enumerate(
            filter(lambda n: n[0].startswith("MULTI_TOKEN"), sorted(environ.items())),
        )
    }
    if not all_tokens:
        LOGGER.info("No additional clients found, using default client")
        return

    async def start_client(client_id, token):
        try:
            if client_id == len(all_tokens):
                await sleep(2)
                print("This will take some time, please wait...")
            client = await Client(
                name=str(client_id),
                api_id=Vars.API_ID,
                api_hash=Vars.API_HASH,
                bot_token=token,
                sleep_threshold=Vars.SLEEP_THRESHOLD,
            ).start()
            LOGGER.info(f"Started - Client {(await client.get_me()).first_name}")
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            LOGGER.error(f"Failed starting Client - {client_id} Error:", exc_info=True)

    clients = await gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    if len(multi_clients) != 1:
        Vars.MULTI_CLIENT = True
        LOGGER.info("Multi-client mode enabled")
    else:
        LOGGER.info("No additional clients were initialized, using default client")
