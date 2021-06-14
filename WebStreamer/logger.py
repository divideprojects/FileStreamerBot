from logging import INFO, WARNING, basicConfig, getLogger

basicConfig(level=INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
getLogger("pyrogram").setLevel(WARNING)
getLogger("apscheduler").setLevel(WARNING)

LOGGER = getLogger(__name__)
