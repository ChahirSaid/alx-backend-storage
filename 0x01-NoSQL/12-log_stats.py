#!/usr/bin/env python3
"""
Script that provides some stats about Nginx logs stored in MongoDB
"""
from pymongo import MongoClient

def print_stats(collection):
    total_logs = collection.count_documents({})
    print(f"{total_logs} logs")

    methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    print("Methods:")
    for method in methods:
        count = collection.count_documents({"method": method})
        print(f"\tmethod {method}: {count}")

    status_check_count = collection.count_documents({"method": "GET", "path": "/status"})
    print(f"{status_check_count} status check")

if __name__ == "__main__":

    client = MongoClient('mongodb://localhost:27017/')
    db = client.logs
    nginx_collection = db.nginx

    print_stats(nginx_collection)

    client.close()
