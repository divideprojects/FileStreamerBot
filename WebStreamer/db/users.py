from datetime import date
from typing import List, Union

from WebStreamer.db.mongo import MongoDB
from WebStreamer.logger import LOGGER


def new_user(uid: int):
    """
    Creates a new user in the database
    """
    return {
        "id": uid,
        "join_date": date.today().isoformat(),
        "downloads": [],
    }


class Users(MongoDB):
    """
    Users collections to be made in the database
    """

    db_name = "filestreamerbot_users"

    def __init__(self):
        super().__init__(self.db_name)

    async def total_users_count(self) -> int:
        """
        Returns the total number of users in the database
        """
        return await self.count({})

    async def get_all_users(self) -> List[int]:
        """
        Returns a list of all users in the database
        """
        users = await self.find_all({})
        return [user["id"] for user in users]

    async def user_exists(self, user_id: int) -> bool:
        """
        Checks if a user exists in the database
        """
        user = await self.find_one({"id": user_id})
        if not user:
            user_data = {
                "id": user_id,
                "join_date": date.today().isoformat(),
            }
            LOGGER.info(f"New User: {user_id}")
            await self.insert_one(user_data)
            return False
        return True

    async def delete_user(self, user_id: int) -> Union[bool, int]:
        """
        Deletes a user from the database
        """
        return await self.delete_one({"id": user_id})
