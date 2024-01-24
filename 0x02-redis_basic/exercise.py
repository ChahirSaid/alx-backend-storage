#!/usr/bin/env python3
"""Function declares a redis class and methods"""
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Counting how many times methods of the class Cache are called"""
    k = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapping the decorated func and returning the wrapper"""
        self._redis.incr(k)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Storing the history of inputs and outputs for a particular func"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapping the decorated function and returning the wrapper"""
        key = method.__qualname__
        inp = str(args)
        self._redis.rpush(key + ":inputs", inp)
        outp = str(method(self, *args, **kwargs))
        self._redis.rpush(key + ":outputs", outp)
        return outp
    return wrapper


def replay(fn: Callable):
    """Displaying the history of calls of a particular func"""
    red = redis.Redis()
    func_n = fn.__qualname__
    calls = red.get(func_n)
    try:
        calls = int(calls.decode("utf-8"))
    except Exception:
        calls = 0
    print("{} was called {} times:".format(func_n, calls))
    inputs = red.lrange("{}:inputs".format(func_n), 0, -1)
    outputs = red.lrange("{}:outputs".format(func_n), 0, -1)
    for inp, outp in zip(inputs, outputs):
        try:
            inp = inp.decode("utf-8")
        except Exception:
            inp = ""
        try:
            outp = outp.decode("utf-8")
        except Exception:
            outp = ""
        print("{}(*{}) -> {}".format(func_n, inp, outp))


class Cache:
    """Declaring a Cache class"""
    def __init__(self):
        """init to store an instance and flush"""
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """taking a data arg and returning a string"""
        redk = str(uuid4())
        self._redis.set(redk, data)
        return redk

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """Converting the data back to the desired format"""
        val = self._redis.get(key)
        if fn:
            val = fn(val)
        return val

    def get_str(self, key: str) -> str:
        """Parametrizing Cache get with the correct conversion func"""
        val = self._redis(key)
        return val.decode("utf-8")

    def get_int(self, key: str) -> int:
        """Parametrizing Cache get with the correct conversion func"""
        val = self._redis(key)
        try:
            val = int(val.decode("utf-8"))
        except Exception:
            val = 0
        return val
