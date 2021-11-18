from os import getcwd, environ

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

env_file = f"{getcwd()}/.env"
config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])


class Var:
    API_ID = int(config("API_ID"))
    API_HASH = str(config("API_HASH"))
    BOT_TOKEN = str(config("BOT_TOKEN"))
    SLEEP_THRESHOLD = int(config("SLEEP_THRESHOLD", default=60))
    WORKERS = int(config("WORKERS", default=8))
    LOG_CHANNEL = int(config("LOG_CHANNEL"))
    PORT = int(config("PORT", default=8080))
    BIND_ADDRESS = str(config("WEB_SERVER_BIND_ADDRESS", default="0.0.0.0"))
    OWNER_ID = int(config("OWNER_ID", default=1198820588))
    NO_PORT = bool(config("NO_PORT", default=False))
    APP_NAME = None
    if "DYNO" in environ:
        ON_HEROKU = True
        APP_NAME = str(config("APP_NAME"))
    else:
        ON_HEROKU = False
    FQDN = (
        str(config("FQDN", default=BIND_ADDRESS))
        if not ON_HEROKU or config("FQDN")
        else APP_NAME + ".herokuapp.com"
    )
    URL = f"https://{FQDN}/" if ON_HEROKU or NO_PORT else f"https://{FQDN}:{PORT}/"
    DATABASE_URL = str(config("DATABASE_URL"))
    AUTH_CHANNEL = str(config("AUTH_CHANNEL", default=None))
