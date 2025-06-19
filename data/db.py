# data/db.py

from pymongo import MongoClient
import os

def get_jobs_collection():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client["engjobs"]
    collection = db["jobs"]
    collection.create_index("url", unique=True)
    return collection

def upsert_job(job):
    collection = get_jobs_collection()
    collection.update_one(
        {"url": job["url"]},
        {"$set": job},
        upsert=True
    )


