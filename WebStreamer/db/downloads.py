from datetime import datetime, timedelta

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
        await self.insert_one(
            {
                "link": random_url,
                "user_id": user_id,
                "message_id": message_id,
                # NOTE: Only 'never' is allowed for owners
                "valid_upto": (datetime.now() + timedelta(seconds=valid_upto))
                if valid_upto != -1
                else -1,
            },
        )
        return random_url

    # TODO: Remove this function after 1 month (2021-08-01) because it's not used anywhere now
    async def get_actual_link(self, link: str) -> str | None:
        """
        Get the actual link from the database
        :param link: The link to be searched
        :return: The actual link
        """
        document = await self.find_one({"random_link": link})
        if not document:
            return None
        return document["link"]

    async def get_msg_id(self, link: str) -> tuple[int, bool, datetime]:
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
            document
            for document in all_data
            # using -1 as a flag for never expiring links
            if (document["valid_upto"] == -1 or document["valid_upto"] > datetime.now())
        ]
        return (
            valid_count,
            len(all_data),
            len(all_data) - len(valid_count),
            len(valid_count),
        )

    async def delete_download(self, link: str, user_id: int) -> int | None:
        """
        Instead of deleting the document, we just set the valid_upto to current time which will make it invalid
        :param link: The link to be deleted
        :param user_id: The user id of the user
        :return: int or None
        """
        return await self.update(
            {"link": link, "user_id": user_id},
            {"$set": {"valid_upto": datetime.now()}},
        )

    async def get_user_active_links(
        self,
        user_id: int,
        with_date: bool = False,
    ) -> dict[str, datetime | str]:
        """Gets the links of a user

        Args:
            user_id (int): User ID to get links for

        Returns:
            List[str]: List of links
        """
        all_links = await self.find_all({"user_id": user_id})
        if with_date:
            return {
                document["link"]: document["valid_upto"]
                for document in all_links
                # using -1 as a flag for never expiring links, and only show valid links to user
                if (
                    document["valid_upto"] == -1
                    or document["valid_upto"] > datetime.now()
                )
            }
        return {
            document["link"]: ""
            for document in all_links
            if (document["valid_upto"] == -1 or document["valid_upto"] > datetime.now())
        }
