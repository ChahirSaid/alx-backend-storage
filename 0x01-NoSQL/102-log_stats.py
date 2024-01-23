#!/usr/bin/env python3
"""
Script that provides some stats about Nginx logs stored in MongoDB
"""
from pymongo import MongoClient


def nginx_stats_check():
    """Providing stats about nginx logs stored in MongoDB"""
    cl = MongoClient()
    col = cl.logs.nginx
    num_of_documents = col.count_documents({})
    print("{} logs".format(num_of_documents))
    print("Methods:")

    methods_l = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    for met in methods_l:
        meth_count = col.count_documents({"method": met})
        print("\tmethod {}: {}".format(met, meth_count))
    st = col.count_documents({"method": "GET", "path": "/status"})
    print("{} status check".format(st))

    print("IPs:")
    t_IPs = col.aggregate([
        {"$group":
         {
             "_id": "$ip",
             "count": {"$sum": 1}
         }
         },
        {"$sort": {"count": -1}},
        {"$limit": 10},
        {"$project": {
            "_id": 0,
            "ip": "$_id",
            "count": 1
        }}
    ])
    for t_ip in t_IPs:
        c = t_ip.get("count")
        ip_add = t_ip.get("ip")
        print("\t{}: {}".format(ip_add, c))


if __name__ == "__main__":
    nginx_stats_check()
