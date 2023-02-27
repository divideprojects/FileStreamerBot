from datetime import datetime, timedelta
from secrets import token_urlsafe
from typing import Tuple, Union

from WebStreamer.db.mongo import MongoDB
from WebStreamer.logger import LOGGER


class Downloads(MongoDB):
    """
    Define downloads collection here
    """

    db_name = "downloads"

    def __init__(self):
        """
        Initialize the collection
        """
        super().__init__(self.db_name)

    async def add_download(
        self,
        message_id: int,
        random_url: str,
        user_id: int,
        valid_upto: float,
    ) -> str:
        """
        Add a download to the database
        :param message_id: Message id of the message
        :param random_url: Random url to be generated
        :param user_id: User id of the user
        :return: The random url
        """
        LOGGER.info(f"Added {random_url}: {message_id}")
        random_gen_link = token_urlsafe(16)
        await self.insert_one(
            {
                "random_link": random_url,
                "link": random_gen_link,
                "user_id": user_id,
                "message_id": message_id,
                # NOTE: Only 'never' is allowed for owners
                "valid_upto": (datetime.now() + timedelta(seconds=valid_upto))
                if valid_upto != -1
                else -1,
            },
        )
        return random_gen_link

    async def get_actual_link(self, link: str) -> Union[str, None]:
        """
        Get the actual link from the database
        :param link: The link to be searched
        :return: The actual link
        """
        document = await self.find_one({"random_link": link})
        if not document:
            return None
        return document["link"]

    async def get_msg_id(self, link: str) -> Tuple[int, bool, datetime]:
        """
        Get the message id from the database
        :param link: The link to be searched
        :return: The message_id
        """
        document = await self.find_one({"link": link})
        if not document:
            return 0, False, datetime.now()
        valid_upto = document["valid_upto"]
        valid = valid_upto > datetime.now() if valid_upto != -1 else True
        return document["message_id"], valid, valid_upto

    async def total_downloads(self) -> int:
        """
        Get the total number of downloads
        :return: The total number of downloads
        """
        return await self.count()

    async def valid_downloads_list(self):
        """
        Get the list of valid downloads
        :return: The list of valid downloads
        """
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

    async def delete_download(self, link: str, user_id: int) -> Union[int, None]:
        """
        Delete a download from the database
        :param link: The link to be deleted
        :param user_id: The user id of the user
        :return: int or None
        """
        return await self.delete_one({"link": link, "user_id": user_id})
