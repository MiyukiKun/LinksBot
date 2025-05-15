from config import client, database_name, collection_name

class BaseDB:
    def __init__(self, collection_suffix):
        self.client = client
        self.db = self.client[collection_name]
        if collection_suffix == None:
            self.collection = self.db[f"{database_name}"]
        else:
            self.collection = self.db[f"{database_name}_{collection_suffix}"]

    async def find(self, data):
        return await self.collection.find_one(data)

    async def full(self):
        cursor = self.collection.find()
        return await cursor.to_list(length=None)

    async def add(self, data):
        try:
            await self.collection.insert_one(data)
        except Exception as e:
            pass

    async def remove(self, data):
        await self.collection.delete_one(data)

    async def modify(self, search_dict, new_dict):
        try:
            await self.collection.find_one_and_update(search_dict, {'$set': new_dict})
        except Exception as e:
            pass

    async def range(self, offset, limit):
        cursor = self.collection.find().skip(offset).limit(limit)
        return await cursor.to_list(length=None)

    async def rando(self, sample_size):
        pipeline = [{"$sample": {"size": sample_size}}]
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def count(self, data={}):
        return await self.collection.count_documents(data)
    
class LinksDB(BaseDB):
    def __init__(self):
        super().__init__(collection_suffix="Links")

class UsersDB(BaseDB):
    def __init__(self):
        super().__init__(collection_suffix="Users")

class SettingsDB(BaseDB):
    def __init__(self):
        super().__init__(collection_suffix="Settings")