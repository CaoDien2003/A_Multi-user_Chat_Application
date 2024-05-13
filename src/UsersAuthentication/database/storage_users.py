from pymongo import MongoClient
from bson import ObjectId

class MongoDB:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client['mydatabase']
        self.users_collection = self.db['users']

    def get_by_phone(self, phone):
        return self.users_collection.find_one({'phone': phone})

    def get_by_token(self, token):
        return self.users_collection.find_one({'token': token})

    def add_user(self, name, phone, password):
        user = {'name': name, 'phone': phone, 'password': password}
        result = self.users_collection.insert_one(user)
        return str(result.inserted_id)

    def get_by_id(self, id):
        return self.users_collection.find_one({'_id': ObjectId(id)})

    def add_token(self,phone,token):
        user = self.users_collection.find_one({'phone': phone})
        if user:
            self.users_collection.update_one({'_id': user['_id']}, {'$set': {'token': token}})
            return True
        else:
            return False
    def remove_token(self,phone):
        self.users_collection.update_one({'phone': phone}, {'$unset': {'token': ""}})
