#!/usr/bin/env python3
"""Web Caching and tracker"""
import requests
import redis
from functools import wraps
from typing import Callable

store = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """Decorator counting times a url is accessed"""
    @wraps(method)
    def wrapper(url):
        store.incr(f"count:{url}")
        c_html = store.get(f"cached:{url}")
        if c_html:
            return c_html.decode('utf-8')

        html = method(url)
        store.setex(f"cached:{url}", 10, html)
        return html
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """Returning html content of a url"""
    result = requests.get(url)
    return result.text
