# -*- coding: utf-8 -*-

import traceback
from datetime import datetime, timedelta
from .models import LiveStreamAccount, LiveStreamInfo
from sentry_sdk import capture_exception, capture_message
from ..utils import log_any, call_server_streaming_api
import random
import string


def save_livestream_info(user_id, live_event_id, service, event_start_time, rtmp_url, full_rtmp_url, live_event_url,
                         key_url, stream_key, stream_user, stream_password):

    try:
        event_start_time = datetime.strptime(event_start_time, '%d/%m/%Y %H:%M:%S')
    except Exception as e:
        traceback.print_exc()
        capture_exception(e)
        log_any("Default start in 24h")
        event_start_time = datetime.now() + timedelta(hours=24)

    if event_start_time < datetime.now():
        capture_message("Event start time less than now()")

    payload = {
        'user_id': user_id,
        'live_event_id': live_event_id,
        'service': service,
        'event_start_time': event_start_time,
        'rtmp_url': rtmp_url,
        'full_rtmp_url': full_rtmp_url,
        'live_event_url': live_event_url,
        'key_url': key_url,
        'stream_key': stream_key,
        'stream_user': stream_user,
        'stream_password': stream_password
    }
    return LiveStreamInfo.add(payload)


def get_livestream_account(user_id):
    account = LiveStreamAccount.find_one({'user_id': user_id})
    if not account:
        # Generate new account
        username, password = generate_username_password(user_id)
        # Register on steraming server
        payload = {
            "password": password,
            "name": username,
            "serverName": "_defaultServer_",
            "description": "api generate for publish stream",
            "version": "3"
        }

        call_server_streaming_api('/v2/servers/_defaultServer_/publishers', payload)

        account = {
            'user_id': user_id,
            'username': username,
            'password': password,
        }
        LiveStreamAccount.add(account)

    return account


def generate_username_password(user_id, min_size_username=6,size_pass=10,chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    username = ''.join(random.choice(chars) for _ in range(min_size_username - 1))
    username = '{}u{}'.format(username, user_id)
    password = ''.join(random.choice(chars) for _ in range(size_pass))

    return username, password