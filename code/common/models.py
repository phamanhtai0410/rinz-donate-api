# -*- coding: utf-8 -*-

from datetime import datetime
from bson import ObjectId
from pymodm import fields
from ..base.model import BaseMG


class LiveStreamAccount(BaseMG):
    class Meta:
        collection_name = 'live_stream_account'
        final = True
        ignore_unknown_fields = True

    _id = fields.ObjectIdField(primary_key=True)
    user_id = fields.IntegerField(default=0)

    username = fields.CharField(default='', blank=True)
    password = fields.CharField(default='',  blank=True)


class LiveStreamInfo(BaseMG):
    class Meta:
        collection_name = 'live_stream_info'
        final = True
        ignore_unknown_fields = True

    _id = fields.ObjectIdField(primary_key=True)
    user_id = fields.IntegerField(default=0)
    live_event_id = fields.CharField(default='', blank=True)
    service = fields.CharField(default='', blank=True)
    event_start_time = fields.DateTimeField()
    rtmp_url =  fields.CharField(default='', blank=True)
    full_rtmp_url = fields.CharField(default='', blank=True)
    live_event_url = fields.ListField(default='', blank=True)
    key_url = fields.CharField(default='', blank=True)
    stream_key = fields.CharField(default='', blank=True)
    stream_user = fields.CharField(default='', blank=True)
    stream_password = fields.CharField(default='', blank=True)
