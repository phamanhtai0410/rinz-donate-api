# -*- coding: utf-8 -*-

import traceback
from enum import Enum, auto


class AppConstants(object):

    # Response status
    STATUS_OK = 1
    STATUS_NOT_OK = 0

    # API APP KEY
    API_APP_KEY = ""

    # Error src
    NOT_E = ''
    E_SERVER_ERROR = 'E_SERVER_ERROR'
    E_FILE_NOT_FOUND = 'E_FILE_NOT_FOUND'
    E_MISSING_DATA = 'E_MISSING_DATA'
    AUTH_ERROR = 'AUTH_ERROR'
