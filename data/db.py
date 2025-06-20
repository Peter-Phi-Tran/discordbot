from pymongo import MongoClient
import os

def get_software_jobs_collection():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client["engjobs"]
    collection = db["software_jobs"]
    return collection

def get_engineering_jobs_collection():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client["engjobs"]
    collection = db["engineering_jobs"]
    return collection

def ensure_indexes():
    """Create indexes for both collections if they don't exist"""
    software = get_software_jobs_collection()
    engineering = get_engineering_jobs_collection()
    
    # Create URL index for software jobs
    if "url_1" not in software.index_information():
        software.create_index("url", unique=True)
    
    # Create URL index for engineering jobs
    if "url_1" not in engineering.index_information():
        engineering.create_index("url", unique=True)
