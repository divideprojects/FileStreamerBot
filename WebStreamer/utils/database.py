from datetime import date

from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    def __init__(self, uri, database_name):
        self._client = AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, uid):
        return {"id": uid, "join_date": date.today().isoformat(), "downloads": []}

    async def add_user(self, uid):
        user = self.new_user(uid)
        await self.col.insert_one(user)

    async def is_user_exist(self, uid):
        user = await self.col.find_one({"id": int(uid)})
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def add_download(self, uid, url):
        user = await self.col.find_one({"id": int(uid)})
        user["downloads"].append(url)
        await self.col.update_one(
            {"id": int(uid)},
            {"$set": {"downloads": user["downloads"]}},
        )

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})
