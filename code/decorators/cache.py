# -*- coding: utf-8 -*-
import json
from functools import wraps

import sentry_sdk

from ..config import DefaultConfig
from ..utils import json_encode_hook, json_decode_hook, jsonify_dict, log_any, make_cross_domain_response
from ..extensions import redis_cache, redis_cluster
from flask import request, abort, jsonify
from sentry_sdk import capture_exception
import jwt
import traceback

CACHE_TIMEOUT_FACTOR = 1


def get_data_by_key(_key):
    try:
        return None
        # return redis_cluster.get(_key)
    except:
        sentry_sdk.capture_exception()
        traceback.print_exc()
        return None


def set_data_by_key(_key, _payload):
    try:
        return redis_cluster.setex(_key, 86400, json.dumps(_payload, default=json_encode_hook))
    except:
        sentry_sdk.capture_exception()
        traceback.print_exc()
        return None


# timeout=1 week
def cache_id(timeout=604800, key_prefix='common', keep_timeout=False):
    """
    Decorator for caching functions by id, using its arguments as part of the key.
    Returns the cached value, or the function if the cache is disabled
    """
    if timeout is None:
        timeout = 300

    if not keep_timeout:
        timeout *= CACHE_TIMEOUT_FACTOR

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = "%s%s:id:%s" % (DefaultConfig.CACHE_SUB, key_prefix, args[0])
            output = get_data_by_key(key)
            if output:
                return json.loads(output, object_hook=json_decode_hook)

            output = f(*args, **kwargs)
            # Set data to redis
            set_data_by_key(key, output)
            return output

        return wrapper

    return decorator


# timeout = 1 day
def cache_filter(timeout=86400, key_prefix='common', key_fields=[], options=[], keep_timeout=False):
    """
    Decorator for caching functions by filter
    Returns the cached value, or the function if the cache is disabled
    """
    if timeout is None:
        timeout = 86400

    if not keep_timeout:
        timeout *= CACHE_TIMEOUT_FACTOR

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            _filter = dict()
            for key_field in key_fields:
                _filter[key_field] = kwargs.get(key_field)
            _options = kwargs.get('options', {})
            for option in options:
                _filter[option] = _options.get(option)

            key = "%s%s:%s" % (DefaultConfig.CACHE_SUB, key_prefix, jsonify_dict(_filter))
            output = get_data_by_key(key)
            if output:
                return json.loads(output, object_hook=json_decode_hook)
            output = f(*args, **kwargs)
            # Set data to redis
            set_data_by_key(key, output)
            return output

        return wrapper

    return decorator
