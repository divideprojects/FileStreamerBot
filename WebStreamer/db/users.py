from datetime import date

from WebStreamer.db.mongo import MongoDB
from WebStreamer.logger import LOGGER


def new_user(uid: int) -> dict[str, str | int | date]:
    """
    Creates a new user in the database
    :param uid: User ID
    """
    return {
        "_id": uid,
        "join_date": date.today().isoformat(),
        "expire_time": "86400",  # 24 hours in seconds
        "ban": False,  # no use is banned by default
    }


class Users(MongoDB):
    """
    Users collections to be made in the database
    """

    db_name = "users"

    def __init__(self):
        super().__init__(self.db_name)

    async def total_users_count(self) -> int:
        """
        Returns the total number of users in the database
        """
        return await self.count({})

    async def get_all_users(self) -> list[int]:
        """
        Returns a list of all users in the database
        :return: List of user ids
        """
        users = await self.find_all({})
        return [user["_id"] for user in users]

    async def user_exists(self, user_id: int) -> bool:
        """
        Checks if a user exists in the database
        :param user_id: User id to check
        :return: True if user exists, False otherwise
        """
        user = await self.find_one({"_id": user_id})
        if not user:
            # if user is not in the database, add them
            user_data = new_user(user_id)
            LOGGER.info(f"New User: {user_id}")
            await self.insert_one(user_data)
        return True

    async def delete_user(self, user_id: int) -> bool | int:
        """
        Deletes a user from the database
        :param user_id: User id to delete
        :return: True if user was deleted, False otherwise
        """
        return await self.delete_one({"_id": user_id})

    async def get_expire_time(self, user_id: int) -> int:
        """
        Returns the expire time for a user (in seconds)

        Args:
            user_id (int): User ID to get expire time for

        Returns:
            int: The expire time for the user (in seconds)
        """
        try:
            user = await self.find_one({"_id": user_id})
            return int(user["expire_time"])
        except:
            return 86400

    async def set_expire_time(
        self,
        user_id: int,
        expire_time: int | bool,
    ) -> bool:
        """
        Sets the expire time for a user (in seconds)

        Args:
            user_id (int): User ID to set expire time for
            expire_time (int): The expire time for the user (in seconds)

        Returns:
            bool: True if the expire time was set, False otherwise
        """
        return await self.update({"_id": user_id}, {"expire_time": expire_time})

    async def is_banned(self, user_id: int) -> bool:
        """Gets the ban status of a user

        Args:
            user_id (int): User ID to get ban status for

        Returns:
            bool: True if the user is banned, False otherwise
        """
        try:
            user = await self.find_one({"_id": user_id})
            return int(user["ban"])
        except:
            return False

    async def set_user_ban_status(self, user_id: int, ban_status: bool) -> bool:
        """Sets the ban status of a user

        Args:
            user_id (int): User ID to set ban status for
            ban_status (bool): The ban status for the user

        Returns:
            bool: True if the ban status was set, False otherwise
        """
        return await self.update({"_id": user_id}, {"ban": ban_status})
