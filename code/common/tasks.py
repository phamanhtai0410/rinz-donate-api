# -*- coding: utf-8 -*-

import requests
import os
import traceback
import sys
from sentry_sdk import capture_message, capture_exception
from ..tasks import celery
from ..config import DefaultConfig
from ..utils import call_payment_gw_api, get_redis_cache, call_socket_api


@celery.task(name='donate_direct_task', rate_limit='60/s')
def donate_direct_task(payload):
    user_detail = get_redis_cache("users:id:{}".format(payload["user_id"]))
    if not user_detail:
        return None

    # TODO check user verified or not.

    user_phone = user_detail["user_phone"]

    data = {
        "stream_title": payload["stream_title"],
        "stream_id": payload["stream_id"],
        "amount": payload["amount"],
        "user_phone": user_phone,
        "user_id": payload["user_id"],
        "receiver": payload["receiver"],
        "note": payload["note"]
    }

    print(data)
    result = call_payment_gw_api('/v1/payment/loyalty/donate', data)

    if result and result['status'] == 1 and not result['error_code']:

        socket_payload = {
            "type": "public",
            "room": payload["stream_id"],
            "author_id": payload["receiver"],
            "event": "donate",
            "payload": {
                "content": "<span style='color: #FAAD14;'>{}</span> đã donate <span style='color: #FAAD14;'>{} RZP</span><br/>{}".format(user_detail["user_full_name"], payload["amount"], payload["note"]),
                "amount": payload["amount"],
                "user": {
                    "user_name": user_detail["user_full_name"] or '',
                    "user_avatar": user_detail["user_avatar"] or '',
                },
                "message": payload["note"],
            },
            "users": []
        }

        # Send message donating
        call_socket_api('/v1/socket/send_to_room', socket_payload)

    return result
