from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings

client = None
db = None


def connect_to_mongo():
    global client, db
    try:
        client = MongoClient(settings.mongodb_url)
        db = client[settings.database_name]
        client.admin.command("ping")
        print("Connected to MongoDB successfully")
    except ConnectionFailure:
        print("Failed to connect to MongoDB")
        raise


def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


def get_database():
    return db
