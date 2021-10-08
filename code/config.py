# -*- coding: utf-8 -*-

import os
import json
from dotenv import load_dotenv

load_dotenv()


class BaseConfig(object):
    PROJECT = "donate-api"
    
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    DEBUG = False
    TESTING = False

    # http://flask.pocoo.org/docs/quickstart/#sessions
    SECRET_KEY = '\xd2\x0c\xa9\xb7\xd9E\xda-\x1e\xdb;\xb8\x0c\xfc\xbf\xf3\x16[\xa2x\xd5s\x83\xe3'    


class DefaultConfig(BaseConfig):
    DEBUG = True

    # Flask-babel: http://pythonhosted.org/Flask-Babel/
    ACCEPT_LANGUAGES = ['vi']
    BABEL_DEFAULT_LOCALE = 'en'

    SENTRY_DSN = os.getenv('SENTRY_DSN')
    MONGODB_URI = os.getenv('MONGODB_URI')
    REDIS_URL = os.getenv('REDIS_URL')
    REDIS_USERS_STARTUP_NODES = json.loads(os.getenv('REDIS_USERS_STARTUP_NODES'))
    CACHE_SUB = ''
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')

    IAPI_DOMAIN = os.getenv('IAPI_DOMAIN')
    PAYMENT_GW_DOMAIN = os.getenv('PAYMENT_GW_DOMAIN')

    SOCKET_API = os.getenv('SOCKET_API')
