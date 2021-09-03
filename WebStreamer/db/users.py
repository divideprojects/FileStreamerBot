from datetime import date

from WebStreamer.db.mongo import MongoDB
from WebStreamer.logger import LOGGER


def new_user(uid):
    return {"id": uid, "join_date": date.today().isoformat(), "downloads": []}


class Users(MongoDB):
    db_name = "filestreamerbot_users"

    def __init__(self):
        super().__init__(self.db_name)

    async def total_users_count(self):
        return await self.count({})

    async def get_all_users(self):
        return await self.find_all({})

    async def user_exists(self, user_id: int):
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

    async def delete_user(self, user_id: int):
        return await self.delete_one({"id": user_id})
