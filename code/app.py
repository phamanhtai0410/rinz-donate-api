# -*- coding: utf-8 -*-

import os
import traceback

import sentry_sdk
from sentry_sdk import capture_exception, capture_message
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask, request, jsonify
from flask_babel import Babel
from .common import rest_service
from .config import DefaultConfig
from .constants import AppConstants
from .extensions import redis_cache
from pymodm import connect

# For import *
__all__ = ['create_app']


DEFAULT_BLUEPRINTS = (
    rest_service,
)


def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = DefaultConfig.PROJECT
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name, instance_relative_config=True)
    configure_app(app, config)
    configure_hook(app)
    configure_blueprints(app, blueprints)
    configure_extensions(app)
    configure_template_filters(app)
    configure_error_handlers(app)
    configure_logging_level()

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
    redis_cache.init_app(app)
    print('Init Redis cache successfully')

    # Flask Babel
    babel = Babel(app)

    # Sentry
    if DefaultConfig.SENTRY_DSN:
        sentry_sdk.init(
            dsn=DefaultConfig.SENTRY_DSN,
            integrations=[FlaskIntegration()],
        )

        capture_message('{} starts'.format(DefaultConfig.PROJECT))

    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES')
        return request.accept_languages.best_match(accept_languages)


def configure_blueprints(app, blueprints):
    """Configure blueprints in views."""

    for blueprint in blueprints:
        app.register_blueprint(blueprint)


def configure_template_filters(app):
    @app.template_filter()
    def pretty_date(value):
        return pretty_date(value)

    @app.template_filter()
    def format_date(value, format='%Y-%m-%d'):
        return value.strftime(format)


def configure_logging_level():
    import logging
    logging.getLogger('suds').setLevel(logging.ERROR)


def configure_hook(app):
    @app.before_request
    def before_request():
        pass


def configure_error_handlers(app):

    @app.errorhandler(401)
    def server_error_page(error):
        return jsonify({'status': AppConstants.STATUS_NOT_OK, 'msg': 'Need login', 'data': {},
                                                                                   'error_code': AppConstants.AUTH_ERROR}), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return jsonify(msg="forbidden"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify(msg="notfound"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return jsonify(msg="server error"), 500
