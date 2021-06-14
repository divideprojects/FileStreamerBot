from os import environ, getenv


class Var:
    API_ID = int(getenv("API_ID"))
    API_HASH = str(getenv("API_HASH"))
    BOT_TOKEN = str(getenv("BOT_TOKEN"))
    SLEEP_THRESHOLD = int(getenv("SLEEP_THRESHOLD", "60"))
    WORKERS = int(getenv("WORKERS", "8"))
    LOG_CHANNEL = int(getenv("LOG_CHANNEL"))
    PORT = int(getenv("PORT", 8080))
    BIND_ADRESS = str(getenv("WEB_SERVER_BIND_ADDRESS", "0.0.0.0"))
    OWNER_ID = int(getenv("OWNER_ID", 1198820588))
    NO_PORT = bool(getenv("NO_PORT", False))
    APP_NAME = None
    if "DYNO" in environ:
        ON_HEROKU = True
        APP_NAME = str(getenv("APP_NAME"))
    else:
        ON_HEROKU = False
    FQDN = (
        str(getenv("FQDN", BIND_ADRESS))
        if not ON_HEROKU or getenv("FQDN")
        else APP_NAME + ".herokuapp.com"
    )
    URL = f"https://{FQDN}/" if ON_HEROKU or NO_PORT else f"https://{FQDN}:{PORT}/"
    DATABASE_URL = str(getenv("DATABASE_URL"))
    AUTH_CHANNEL = str(getenv("AUTH_CHANNEL", None))
