from datetime import datetime, timedelta

from WebStreamer.db.mongo import MongoDB
from WebStreamer.logger import LOGGER


class Downloads(MongoDB):
    db_name = "downloads"

    def __init__(self):
        super().__init__(self.db_name)

    async def add_download(self, message_id: int, random_url: str, user_id: int):
        LOGGER.info(f"Added {random_url}: {message_id}")
        await self.insert_one(
            {
                "link": random_url,
                "user_id": user_id,
                "message_id": message_id,
                "valid_upto": (datetime.now() + timedelta(days=1)),
            },
        )
        return

    async def get_msg_id(self, message_id: int):
        full_url = await self.find_one({"message_id": message_id})
        return full_url["message_id"]

    async def total_downloads(self):
        return await self.count()

    async def valid_downloads_list(self):
        all_data = await self.find_all()
        valid_count = [
            document for document in all_data if document["valid_upto"] > datetime.now()
        ]
        return valid_count, len(valid_count)
