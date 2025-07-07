from pymongo import MongoClient
import os

def client():
    return MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))

def get_software_jobs_collection():
    db = client()["engjobs"]
    collection = db["software_jobs"]
    return collection

def get_engineering_jobs_collection():
    db = client()["engjobs"]
    collection = db["engineering_jobs"]
    return collection   

def get_newgrad_software_jobs_collection():
    db = client()["engjobs"]
    collection = db["newgrad_software_jobs"]
    return collection

def get_newgrad_engineering_jobs_collection():
    db = client()["engjobs"]
    collection = db["newgrad_engineering_jobs"]
    return collection

def ensure_indexes():
    """Create indexes for both collections if they don't exist"""
    cols = [
        get_software_jobs_collection(),
        get_engineering_jobs_collection(),
        get_newgrad_software_jobs_collection(),
        get_newgrad_engineering_jobs_collection()
    ]
    # Create URL index for software jobs
    for c in cols:
        if "url_1" not in c.index_information():
            c.create_index("url", unique=True)
