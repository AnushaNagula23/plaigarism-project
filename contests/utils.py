# utils.py (or another file)

from pymongo import MongoClient
from django.conf import settings

def get_mongo_collection(collection_name):
    client = MongoClient(settings.MONGO_DB_URI)  # Get the MongoDB client using URI from settings
    db = client[settings.MONGO_DB_NAME]  # Get the database using the name from settings
    return db[collection_name] # Return the specific collection
