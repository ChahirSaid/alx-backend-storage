#!/usr/bin/env python3
""" web cache and tracker """

import redis
import requests
from typing import Callable
from functools import wraps


def countURL(method: Callable) -> Callable:
    """ count function """
    @wraps(method)
    def wrapper(*args, **kwds):
        """ wrapped function """
        rds = redis.Redis()
        rds.incr('count:' + args[0])
        url = rds.get(args[0])
        if not url:
            url = method(*args, **kwds)
            rds.setex(args[0], 10, url)
        return url
    return wrapper


@countURL
def get_page(url: str) -> str:
    """ track how many times a particular URL was accessed """
    return requests.get(url).text
