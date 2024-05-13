from pymongo import MongoClient
from bson import ObjectId
import logging

class MongoDB:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client['mydatabase']
        self.users_collection = self.db['users']

    def get_by_phone(self, phone):
        try:
            return self.users_collection.find_one({'phone': phone})
        except Exception as e:
            logging.error(f"Error retrieving user by phone: {e}")
            return None

    def add_user(self, name, phone, password):
        try:
            user = {'name': name, 'phone': phone, 'password': password}
            result = self.users_collection.insert_one(user)
            return str(result.inserted_id)
        except Exception as e:
            logging.error(f"Failed to insert user: {e}")
            return None

    def get_by_id(self, id):
        return self.users_collection.find_one({'_id': ObjectId(id)})
