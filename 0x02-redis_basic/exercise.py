#!/usr/bin/env python3
"""
RedisCache Module

This module declares a RedisCache class and related methods to provide a caching mechanism using Redis.
"""

import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps

class RedisCache:
    """
    RedisCache class for storing and retrieving data with additional features.
    """

    def __init__(self):
        """
        Initialize the RedisCache instance and flush the Redis database.
        """
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @staticmethod
    def _decode_value(value: bytes, default: Union[str, int] = "") -> Union[str, int]:
        """
        Decode bytes to string or integer, with a default value if decoding fails.

        Args:
            value (bytes): The value to decode.
            default (Union[str, int]): The default value if decoding fails.

        Returns:
            Union[str, int]: The decoded value.
        """
        try:
            return value.decode("utf-8")
        except Exception:
            return default

    @staticmethod
    def _get_function_key(func: Callable) -> str:
        """
        Generate a unique key for a function.

        Args:
            func (Callable): The function for which to generate the key.

        Returns:
            str: The generated function key.
        """
        return func.__qualname__

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis and return a unique key.

        Args:
            data (Union[str, bytes, int, float]): The data to store.

        Returns:
            str: The unique key associated with the stored data.
        """
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, decode_function: Optional[Callable] = None) -> Union[str, int]:
        """
        Retrieve data from Redis and optionally apply a decoding function.

        Args:
            key (str): The key associated with the data.
            decode_function (Optional[Callable]): The decoding function to apply.

        Returns:
            Union[str, int]: The retrieved and potentially decoded value.
        """
        value = self._redis.get(key)
        return self._decode_value(value) if not decode_function else decode_function(value)

    def get_str(self, key: str) -> str:
        """
        Retrieve and decode a string from Redis.

        Args:
            key (str): The key associated with the string data.

        Returns:
            str: The decoded string value.
        """
        return self.get(key, decode_function=self._decode_value)

    def get_int(self, key: str) -> int:
        """
        Retrieve and decode an integer from Redis, defaulting to 0 if decoding fails.

        Args:
            key (str): The key associated with the integer data.

        Returns:
            int: The decoded integer value.
        """
        return self.get(key, decode_function=lambda value: int(value.decode("utf-8", "ignore")))

    @classmethod
    def replay(cls, func: Callable):
        """
        Display the history of calls of a particular function.

        Args:
            func (Callable): The function for which to display the call history.
        """
        redis_instance = redis.Redis()
        func_name = cls._get_function_key(func)
        call_count = int(redis_instance.get(func_name).decode("utf-8")) if redis_instance.get(func_name) else 0
        print(f"{func_name} was called {call_count} times:")

        inputs = redis_instance.lrange(f"{func_name}:inputs", 0, -1)
        outputs = redis_instance.lrange(f"{func_name}:outputs", 0, -1)

        for inp, outp in zip(inputs, outputs):
            print(f"{func_name}(*{inp.decode('utf-8')}) -> {outp.decode('utf-8')}")
