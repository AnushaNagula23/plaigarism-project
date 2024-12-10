from django.conf import settings

def get_mongo_collection(collection_name):
    return settings.MONGO_DB[collection_name] # Return the specific collection
