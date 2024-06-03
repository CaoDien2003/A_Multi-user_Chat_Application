from pymongo import MongoClient
from bson import ObjectId

class MongoDB:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client['mydatabase']
        self.users_collection = self.db['users']

    def get_by_phone(self, phone):
        return self._convert_objectid(self.users_collection.find_one({'phone': phone}))

    def get_by_token(self, token):
        return self._convert_objectid(self.users_collection.find_one({'token': token}))

    def add_user(self, name, phone, password):
        user = {'name': name, 'phone': phone, 'password': password}
        result = self.users_collection.insert_one(user)
        return str(result.inserted_id)

    def get_by_id(self, id):
        return self._convert_objectid(self.users_collection.find_one({'_id': ObjectId(id)}))

    def add_token(self, phone, token):
        self.users_collection.update_one({'phone': phone}, {'$set': {'token': token}})

    def get_all_users(self):
        users = list(self.users_collection.find())
        return [self._convert_objectid(user) for user in users]

    def _convert_objectid(self, user):
        if user and '_id' in user:
            user['_id'] = str(user['_id'])
        return user
