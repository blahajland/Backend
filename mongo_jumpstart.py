from pymongo import MongoClient
from config import mongo_host, mongo_port, mongo_user, mongo_password, mongo_db_name

client = MongoClient(f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/")
db = client[mongo_db_name]

def create_collections():
    db.create_collection('users')
    print("Collections created successfully.")

if __name__ == "__main__":
    create_collections()