from typing import Any, Tuple, Union

from motor.motor_asyncio import AsyncIOMotorClient

from WebStreamer.vars import Vars

db_client = AsyncIOMotorClient(Vars.DATABASE_URL)
main_db = db_client["filestreambot"]


class MongoDB:
    """
    Class for interacting with Bot database.
    """

    def __init__(self, collection) -> None:
        self.collection = main_db[collection]

    # Insert one entry into collection
    async def insert_one(self, document) -> str:
        result = await self.collection.insert_one(document)
        return repr(result.inserted_id)

    # Find one entry from collection
    async def find_one(self, query) -> Union[bool, None, Any]:
        result = await self.collection.find_one(query)
        if result:
            return result
        return False

    # Find entries from collection
    async def find_all(self, query=None) -> Union[bool, None, Any]:
        if query is None:
            query = {}
        return [document async for document in self.collection.find(query)]

    # Count entries from collection
    async def count(self, query=None) -> int:
        if query is None:
            query = {}
        return await self.collection.count_documents(query)

    # Delete entry/entries from collection
    async def delete_one(self, query) -> int:
        await self.collection.delete_many(query)
        after_delete = await self.collection.count_documents({})
        return after_delete

    # Replace one entry in collection
    async def replace(self, query, new_data) -> Tuple[int, int]:
        old = await self.collection.find_one(query)
        _id = old["_id"]
        await self.collection.replace_one({"_id": _id}, new_data)
        new = await self.collection.find_one({"_id": _id})
        return old, new

    # Update one entry from collection
    async def update(self, query, update) -> Tuple[int, int]:
        result = await self.collection.update_one(query, {"$set": update})
        new_document = await self.collection.find_one(query)
        return result.modified_count, new_document

    @staticmethod
    async def db_command(command: str) -> Any:
        return await main_db.command(command)
