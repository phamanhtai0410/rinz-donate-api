# -*- coding: utf-8 -*-

import requests
import os
import traceback
import sys
from sentry_sdk import capture_message, capture_exception
from ..tasks import celery
from ..config import DefaultConfig
from ..utils import call_payment_gw_api, get_redis_cache


@celery.task(name='donate_direct_task', rate_limit='60/s')
def donate_direct_task(payload):

    user_detail = get_redis_cache("users:id:".format(payload["user_id"]))
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
    result = call_payment_gw_api('/v1/payment/loyalty/donate', data)
    return result
