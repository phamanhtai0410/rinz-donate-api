# -*- coding: utf-8 -*-

import random
from flask import Blueprint, request, abort

from ..utils import make_cross_domain_response, log_any, convert_to_int
from ..constants import AppConstants
from ..config import DefaultConfig
from ..decorators.auth import get_user, auth_user
from .tasks import donate_direct_task


rest_service = Blueprint('rest_service', __name__, url_prefix='/v1/donate')


@rest_service.route('/common/health_check', methods=['GET'])
def health_check():
    # capture_message('Health check route voter service')
    # health_check_task.delay()
    return make_cross_domain_response({'status': AppConstants.STATUS_OK, 'msg': 'Live stream api Health Check service'},
                                      200)


@rest_service.route('/direct', methods=['POST'])
@auth_user()
def donate_direct(user_info):
    """
    Donate directly.
    """
    log_any('Call donate_direct')

    if not user_info:
        return abort(401)

    receiver = request.json.get('receiver')
    from_user_id = user_info["id"]
    stream_id = request.json.get('object_id')
    stream_title = request.json.get('object_title', '')
    amount = convert_to_int(request.json.get('amount'))
    message = request.json.get('message', '')
    service = request.json.get('service', '') # service name: rinzmusic, thecuatui

    if not receiver or not from_user_id or not amount or not stream_id:
        return make_cross_domain_response(
            {'status': AppConstants.STATUS_NOT_OK, 'msg': 'Missing data', 'data': {},
             'error_code': AppConstants.E_MISSING_DATA}, 200)

    # Call celery to make donate
    payload = {
        'receiver': receiver,
        'user_id': from_user_id,
        'stream_id': stream_id,
        'stream_title': stream_title,
        'amount': amount,
        'note': message,
        'service': service,
    }
    response = donate_direct_task(payload)
    if response:
        return make_cross_domain_response(response, 200)

    return make_cross_domain_response(
         {'status': AppConstants.STATUS_NOT_OK, 'msg': 'Something error with us. We are fixing!', 'data': {},
          'error_code': AppConstants.E_SERVER_ERROR}, 200)
