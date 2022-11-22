from WebStreamer.db.downloads import Downloads
from WebStreamer.db.mongo import MongoDB
from WebStreamer.db.users import Users
from WebStreamer.logger import LOGGER


def __connect_first():
    """
    Connect to the database before importing the models
    """
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!")


# Start the database connection
__connect_first()
