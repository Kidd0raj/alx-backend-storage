#!/usr/bin/env python3
"""
Web Cache and Tracker

This script provides a web cache and tracker using Redis for storage.
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis connection
redis_store = redis.Redis()

def count_url_access(method: Callable) -> Callable:
    """
    Decorator counting how many times a URL is accessed.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: The decorated method.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """
        Wrapper function for counting URL accesses.

        Args:
            url (str): The URL to access.

        Returns:
            str: HTML content of the URL.
        """
        cached_key = f"cached:{url}"
        cached_data = redis_store.get(cached_key)

        if cached_data:
            return cached_data.decode("utf-8")

        count_key = f"count:{url}"
        html_content = method(url)

        redis_store.incr(count_key)
        redis_store.set(cached_key, html_content)
        redis_store.expire(cached_key, 10)

        return html_content

    return wrapper

@count_url_access
def get_page(url: str) -> str:
    """
    Returns HTML content of a URL.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: HTML content of the URL.
    """
    response = requests.get(url)
    return response.text
