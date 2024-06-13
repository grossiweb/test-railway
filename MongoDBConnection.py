from pymongo import MongoClient
import os

class DBConnection:
    
    def __init__(self, db, collection):
        self.__client = MongoClient(os.environ["MONGODB_URI"])
        self.__db = self.__client[db]
        self.__collection = self.__db[collection]
        
    def get_name_data(self, name: str):
        return list(self.__collection.find({"name": name}))
