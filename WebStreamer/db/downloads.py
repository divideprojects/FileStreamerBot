from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Tuple, Union

from WebStreamer.db.mongo import MongoDB
from WebStreamer.logger import LOGGER


class Downloads(MongoDB):
    """
    Define downloads collection here
    """

    db_name = "filestreamerbot_downloads"

    def __init__(self):
        """
        Initialize the collection
        """
        super().__init__(self.db_name)

    async def add_download(self, message_id: int, random_url: str, user_id: int) -> str:
        """
        Add a download to the database
        """
        LOGGER.info(f"Added {random_url}: {message_id}")
        real_link = token_urlsafe(16)
        await self.insert_one(
            {
                "random_link": random_url,
                "link": real_link,
                "user_id": user_id,
                "message_id": message_id,
                "valid_upto": (datetime.now() + timedelta(days=1)),
            },
        )
        return real_link

    async def get_actual_link(self, link: str) -> Union[str, None]:
        """
        Get the actual link from the database
        """
        document = await self.find_one({"random_link": link})
        if not document:
            return None
        return document["link"]

    async def get_msg_id(self, link: str) -> Tuple[int, bool, datetime]:
        """
        Get the message id from the database
        """
        document = await self.find_one({"link": link})
        if not document:
            return 0, False, datetime.now()
        valid_upto = document["valid_upto"]
        valid = valid_upto > datetime.now()
        return document["message_id"], valid, valid_upto

    async def total_downloads(self) -> int:
        """
        Get the total number of downloads
        """
        return await self.count()

    async def valid_downloads_list(self):
        all_data = await self.find_all()
        valid_count = [
            document for document in all_data if document["valid_upto"] > datetime.now()
        ]
        return (
            valid_count,
            len(all_data),
            len(all_data) - len(valid_count),
            len(valid_count),
        )

    async def delete_download(self, link: str, user_id: int):
        return await self.delete_one({"link": link, "user_id": user_id})
