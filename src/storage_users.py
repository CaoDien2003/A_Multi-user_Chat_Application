from pymongo import MongoClient
from bson import ObjectId

class MongoDB:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client['mydatabase']
        self.users_collection = self.db['users']

    def get_by_phone(self, phone):
        return self.users_collection.find_one({'phone': phone})

    def add_user(self, name, phone, password):
        user = {'name': name, 'phone': phone, 'password': password}
        result = self.users_collection.insert_one(user)
        return str(result.inserted_id)

    def get_by_id(self, id):
        return self.users_collection.find_one({'_id': ObjectId(id)})
