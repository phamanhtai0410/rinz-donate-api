# -*- coding: utf-8 -*-
import os
import traceback

import sentry_sdk
from celery import Celery
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk import capture_message, capture_exception

from .config import DefaultConfig
from pymodm import connect
#from .extensions import redis_cache


def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT

    app = Flask(app_name, instance_relative_config=True)
    configure_app(app, config)
    configure_extensions(app)

    return app


def configure_app(app, config=None):
    """Different ways of configurations."""

    # http://flask.pocoo.org/docs/api/#configuration
    app.config.from_object(DefaultConfig)

    # http://flask.pocoo.org/docs/config/#instance-folders
    app.config.from_pyfile('production.cfg', silent=True)

    if config:
        app.config.from_object(config)


def configure_extensions(app):
    # MongoDB
    connect(DefaultConfig.MONGODB_URI, connect=False)
    print('Connect with MongoDB successfully')

    # Redis
    #redis_cache.init_app(app)
    #print('Init Redis cache successfully')

    # Sentry
    if DefaultConfig.SENTRY_DSN:
        sentry_sdk.init(
            dsn=DefaultConfig.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            debug=True,
        )

        capture_message('{} celery starts'.format(DefaultConfig.PROJECT))


def create_celery_app(app=None):
    app = app or create_app()
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    print('Init Celery tasks app')

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = create_celery_app()
