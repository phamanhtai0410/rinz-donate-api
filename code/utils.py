
# -*- coding: utf-8 -*-
"""
    Utils has nothing to do with models and views.
"""

import os
import random
import string
import json

import requests
from datetime import datetime

from bson import ObjectId
from flask import make_response, request
import traceback

from .extensions import redis_cluster
from .config import DefaultConfig
from sentry_sdk import capture_exception


def get_current_time():
    return datetime.utcnow()


def get_current_epoch_time():
    import time
    return int(time.time())


def pretty_date(dt, default=None):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    Ref: https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
    """

    if default is None:
        default = 'just now'

    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, 'year', 'years'),
        (diff.days / 30, 'month', 'months'),
        (diff.days / 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
        (diff.seconds / 3600, 'hour', 'hours'),
        (diff.seconds / 60, 'minute', 'minutes'),
        (diff.seconds, 'second', 'seconds'),
    )

    for period, singular, plural in periods:

        if not period:
            continue

        if period == 1:
            return u'%d %s ago' % (period, singular)
        else:
            return u'%d %s ago' % (period, plural)

    return default


def id_generator(size=10, chars=string.ascii_letters + string.digits):
    # return base64.urlsafe_b64encode(os.urandom(size))
    return ''.join(random.choice(chars) for x in range(size))


def make_dir(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
    except Exception as e:
        raise e


def base64_decode(code):
    import base64
    if len(code) % 4 != 0:  # check if multiple of 4
        while len(code) % 4 != 0:
            code = code + "="
        req_str = base64.b64decode(code)
    else:
        req_str = base64.b64decode(code)
    return req_str


def is_too_many_double_word(text, limit_time=3):
    # util to check double word, if its appearance exceed limit_time then return true
    # example: "con chua an comm" is ok, "mm chua mm chaoo" is not ok
    if len(text) < 2:
        return False
    count = 0
    for i in range(0, len(text) - 1):
        if text[i] == text[i + 1]:
            count += 1
            if count > limit_time:
                return True
    return False


def replace_multiple(s, list=["`", "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", "=", "{", "}", "[", "]",
                              ";", ":", "'", "\\", "/", ",", "|", "<", ".", ">", "?"], r='-'):
    # replace multiple character to one
    for l in list:
        s = s.replace(l, r)
    return s


def replace_special_character(text):
    # prevent unexpected character in filetype
    replace_list = "`~!@#$%^&*()-_+={}[];:'\"\\|,<>.?/"
    s = replace_multiple(text, replace_list, ' ')
    s = " ".join(s.split())  # remove all unneccesary space, split line
    return s


def json_encode_response(obj):
    if isinstance(obj, datetime):
        obj = obj.timestamp()
    if isinstance(obj, ObjectId):
        obj = str(obj)

    return obj


def make_response_dict(data):
    dict_string = json.dumps(data, default=json_encode_response)
    return json.loads(dict_string)


def make_cross_domain_response(data, response_code=200, extra_data=[]):
    data = make_response_dict(data)
    response = make_response(data, response_code)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'AUTHORIZATION, If-none-match'
    response.headers['Access-Control-Max-Age'] = '1728000'
    response.headers['Access-Control-Expose-Headers'] = 'ETag, X-TOKEN'
    if extra_data:
        for d in extra_data:
            if 'name' in d and 'value' in d:
                response.headers[d['name']] = d['value']
    return response


def send_telegram_message(token_id, chat_id, message):
    try:
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        return requests.post('https://api.telegram.org/bot{token}/sendMessage'.format(token=token_id), data=payload,
                             verify=False).content
    except Exception as e:
        capture_exception(e)


def json_decode_hook(obj):
    if isinstance(obj, str) and '\\' in obj:
        obj = obj.replace('\\', '')
        if ('{' in obj and '}' in obj) or ('[' in obj and ']' in obj):
            obj = json.loads(obj)
    if '__datetime__' in obj:
        return datetime.strptime(obj['as_str'], "%Y%m%dT%H:%M:%S.%f")
    if b'__datetime__' in obj:
        return datetime.strptime(obj[b'as_str'], "%Y%m%dT%H:%M:%S.%f")
    return obj


def json_encode_hook(obj):
    if isinstance(obj, datetime):
        obj = {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    if isinstance(obj, ObjectId):
        obj = str(obj)
    return obj


def make_up_objectid(obj):
    '''
    Make up single obj. Use id instead of _id, and convert value to string.
    :param obj:
    :return:
    '''

    if not obj:
        return None
    # obj = obj.to_son().to_dict()
    if isinstance(obj, dict):
        obj['id'] = str(obj['_id'])
        del obj['_id']
    else:
        obj.id = str(obj._id)
        del obj._id
    return obj


def jsonify_dict(dct):
    for k, v in dct.items():
        if isinstance(v, datetime):
            dct[k] = v.isoformat()
        elif isinstance(v, ObjectId):
            dct[k] = str(v)

    return json.dumps(dct)


def log_any(x, *args,**kwargs):
    '''
    Log any message to json format.
    '''

    msg = {
        'msg': x,
    }

    try:
        if args:
            msg['args'] = json.dumps(args)
        if kwargs:
            #kwargs.setdefault('default',lambda x:getattr(x,'__dict__',dict((k,getattr(x,k) if not callable(getattr(x,k)) else repr(getattr(x,k))) for k in dir(x) if not (k.startswith('__') or isinstance(getattr(x,k),x.__class__)))))
            msg['kwargs'] = json.dumps(kwargs)
        print(msg)
    except:
        log_any('Can not log that kind of message')
        traceback.print_exc()
        return ""

    return json.dumps(msg)


def convert_to_int(string):
    '''
    Convert string to number
    '''
    if string:
        try:
            num = int(string)
        except:
            return False
        return num
    return False


# def save_token_redis(token):
#     redis_cluster.setex('token:{}'.format(token), 259200, 1)
#     return True

#======= Dump/Load json scripts =========

def msgpack_decode_hook(obj):
    if b'__datetime__' in obj:
        obj = datetime.strptime(obj[b'as_str'].decode(), "%Y-%m-%dT%H:%M:%S.%f")
    return obj


def msgpack_encode_hook(obj):
    if isinstance(obj, datetime):
        obj = obj.strftime("%Y-%m-%dT%H:%M:%S.%f").encode()

    if isinstance(obj, ObjectId):
        obj = str(obj).decode('utf-8')

    return obj


def dump_data(item, dumper=json.dumps):
    if dumper == json.dumps:
        # json, use separators to stringify
        return dumper(item, separators=(',', ':'), default=msgpack_encode_hook)
    else:
        # msgpack
        return dumper(item, default=msgpack_encode_hook)


def load_data(item, loader=json.loads):
    return loader(item, object_hook=msgpack_encode_hook)


def get_redis_cache(key):
    """
    Get value redis by single key.
    :param key:
    :return:
    """
    output = redis_cluster.get(key)
    if output:
        return load_data(output, json.loads)

    return None

#
# def set_redis_cache(key, value):
#     """
#     Set obj to redis.
#     :param key:
#     :param value:
#     :return:
#     """
#     output = dump_data(value)
#     redis_cache.set(key, output)
#
#     return None


def post_to_iapi(uri, payload):
    """
    POST to Internal api to do something.
    :param payload:
    :return:
    """
    url = DefaultConfig.IAPI_DOMAIN + uri
    if 'st' not in payload:
        payload['st'] = request.values.get('st', '')

    headers = {
        'content-Type': 'application/json',
    }

    try:
        log_any(payload)
        response = requests.post(url, data=json.dumps(payload), headers=headers,verify=False, timeout=3)
        if response.status_code != 200:
            log_any("Call iapi error", response.status_code, uri)

        return True
    except:
        traceback.print_exc()

    return False



def send_notify_to_user(user_id, title, description, msg_type, payload):
    try:
        data = {
            "user_id": user_id,
            "from_service": "card",
            "type": msg_type,
            "payload": payload,
            "message": {
                "type_content": "text",
                "title": title,
                "description": description,
                "image": "",
                "origin_user": "",
                "item_id": "",
                "preview_info": {
                    "preview_img": "",
                    "preview_description": description,
                    "preview_title": title
                }
            }
        }
        _data = json.dumps(data)
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request(method="POST", url=DefaultConfig.IAPI_DOMAIN + "/v1/pusher/user/push-notification",
                                    data=_data,
                                    headers=headers,
                                    timeout=10,
                                    verify=False)
        log_any('send_noty_to_user response', response.text)
    except Exception as e:
        capture_exception(e)
        traceback.print_exc()


def call_payment_gw_api(uri, payload, method='POST'):
    """

    @:param uri: sample '/api/clients'
    @:param payload: json
    @:param method: POST or GET
    """
    try:
        _data = json.dumps(payload)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            #'Authorization': 'Basic {}'.format(DefaultConfig.SERVER_STREAM_TOKEN),
        }

        log_any(uri, _data)

        if method in ['POST', 'PUT']:
            response = requests.request(method=method, url=DefaultConfig.PAYMENT_GW_DOMAIN + uri,
                                    data=_data,
                                    headers=headers,
                                    timeout=10,
                                    verify=False)
        else:
            response = requests.request(method="GET", url=DefaultConfig.SERVER_STREAM_DOMAIN + uri,
                                        headers=headers,
                                        timeout=10,
                                        verify=False)

        log_any(uri, response.text)

        return response.json()

    except Exception as e:
        capture_exception(e)
        traceback.print_exc()

    return False