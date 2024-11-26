from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import certifi
load_dotenv()

class DBConnection:
    
    def __init__(self, db, collection):
        self.__client = MongoClient(os.environ["MONGODB_URI"], server_api=ServerApi('1'), tlsCAFile=certifi.where())
        self.__db = self.__client[db]
        self.__collection = self.__db[collection]
        
    def get_name_data(self, name: str):
        return list(self.__collection.find({"name": name}))
