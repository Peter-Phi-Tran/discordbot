# clear_db.py
import os
import sys
from dotenv import load_dotenv

# Add your project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.db import get_jobs_collection

def clear_jobs_collection():
    """Clear all jobs from the MongoDB collection"""
    collection = get_jobs_collection()
    
    # Count documents before deletion
    count_before = collection.count_documents({})
    print(f"Jobs in collection before deletion: {count_before}")
    
    # Delete all documents
    result = collection.delete_many({})
    print(f"Deleted {result.deleted_count} documents")
    
    # Verify deletion
    count_after = collection.count_documents({})
    print(f"Jobs in collection after deletion: {count_after}")
    
    if count_after == 0:
        print("✅ Collection successfully cleared!")
    else:
        print("❌ Some documents may still remain")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv(dotenv_path="config/.env")
    
    # Confirm deletion
    response = input("Are you sure you want to delete ALL jobs from the database? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        clear_jobs_collection()
    else:
        print("Operation cancelled")