from os import environ, getcwd

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment

env_file = f"{getcwd()}/.env"
config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])


class Vars:
    """
    Class to store all the variables
    """

    API_ID = int(config("API_ID", default=None))
    API_HASH = str(config("API_HASH", default=None))

    # Bot tokens
    BOT_TOKEN = str(config("BOT_TOKEN", default=None))
    MISSALITABOT_TOKEN = str(config("MISSALITABOT_TOKEN", default=None))
    DIVKIXBOT_TOKEN = str(config("DIVKIXBOT_TOKEN", default=None))
    PREMIUMACCOUNTSROBOT_TOKEN = str(config("PREMIUMACCOUNTSROBOT_TOKEN", default=None))
    GOFILTERBOT_TOKEN = str(config("GOFILTERBOT_TOKEN", default=None))
    ALITABETABOT_TOKEN = str(config("ALITABETABOT_TOKEN", default=None))
    DP_WATERMARKBOTBOT_TOKEN = str(config("DP_WATERMARKBOTBOT_TOKEN", default=None))
    VIDMERGEBOT_TOKEN = str(config("VIDMERGEBOT_TOKEN", default=None))

    SLEEP_THRESHOLD = int(config("SLEEP_THRESHOLD", default=60))
    WORKERS = int(config("WORKERS", default=8))
    LOG_CHANNEL = int(config("LOG_CHANNEL", default=-100))
    PORT = int(config("PORT", default=8080))
    BIND_ADDRESS = str(config("WEB_SERVER_BIND_ADDRESS", default="0.0.0.0"))
    OWNER_ID = int(config("OWNER_ID", default=1198820588))
    NO_PORT = bool(config("NO_PORT", default=False))
    APP_NAME = None
    if "DYNO" in environ:
        ON_HEROKU = True
        APP_NAME = str(config("APP_NAME", default=None))
    else:
        ON_HEROKU = False
    FQDN = (
        str(config("FQDN", default=BIND_ADDRESS))
        if not ON_HEROKU or config("FQDN", default=None)
        else APP_NAME + ".herokuapp.com"
    )
    URL = f"https://{FQDN}/" if ON_HEROKU or NO_PORT else f"https://{FQDN}:{PORT}/"
    DATABASE_URL = str(config("DATABASE_URL", default=None))
    DATABASE_NAME = str(config("DATABASE_NAME", default="filestreambot"))
    SUPPORT_GROUP = config("SUPPORT_GROUP", default="@DivideSupport")
    AUTH_CHANNEL = str(config("AUTH_CHANNEL", default="@DivideProjects"))
    JOIN_CHECK = config("JOIN_CHECK", default=None, cast=config.boolean)
    FLOODCONTROL_TIME_MINUTES = int(config("FLOODCONTROL_TIME_MINUTES", default=5))
