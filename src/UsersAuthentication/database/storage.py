from pymongo import MongoClient
from bson import ObjectId

class MongoDB:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client['mydatabase']
        self.users_collection = self.db['users']
        self.rooms_collection = self.db['rooms']

    def get_by_name(self, name):
        return self._convert_objectid(self.users_collection.find_one({'name': name}))

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
    
    def get_by_phone(self, phone):
        return self._convert_objectid(self.users_collection.find_one({'phone': phone}))

    def _convert_objectid(self, user):
        if user and '_id' in user:
            user['_id'] = str(user['_id'])
        return user
    
    def delete_user(self, phone):
        result = self.users_collection.delete_one({'phone': phone})
        return result.deleted_count
    
    def create_room(self, name, users):
        room = {'name': name, 'users': users}
        result = self.rooms_collection.insert_one(room)
        return str(result.inserted_id)

    def get_rooms_by_user(self, user_phone):
        rooms = self.rooms_collection.find({"users": user_phone})
        return [self._convert_objectid(room) for room in rooms]

    def get_room_by_name(self, name):
        return self._convert_objectid(self.rooms_collection.find_one({'name': name}))

    def get_all_rooms(self):
        rooms = list(self.rooms_collection.find())
        return [self._convert_objectid(room) for room in rooms]

    def delete_room(self, name):
        result = self.rooms_collection.delete_one({'name': name})
        return result.deleted_count
    
    def _convert_objectid(self, obj):
        if obj and '_id' in obj:
            obj['_id'] = str(obj['_id'])
        return obj
