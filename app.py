import logging

from flask import Flask, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Api

import settings
import api_views

# APP
app = Flask(__name__)
app.config.from_mapping(**settings.APP_CONFIG)


@app.route('/')
def hello_world():
    return render_template('index.html', **settings.WEBPAGE_INFO)


# Limiter
limiter = Limiter(app, key_func=get_remote_address)


def dummy_decorator(f):
    return f


# API
api = Api(app)

# Lists
if app.config.get('API_RATE_LIMITER_LIST') is not None:
    api_rate_limiter_list = limiter.shared_limit(app.config.get('API_RATE_LIMITER_LIST'), scope='api')
else:
    api_rate_limiter_list = dummy_decorator

api_views.ListJournals.decorators = [api_rate_limiter_list]
api.add_resource(api_views.ListJournals, '/api/journals')

api_views.ListProviders.decorators = [api_rate_limiter_list]
api.add_resource(api_views.ListProviders, '/api/providers')

# suggestions
if app.config.get('API_RATE_LIMITER_SUGGESTS') is not None:
    api_rate_limiter_suggests = limiter.shared_limit(app.config.get('API_RATE_LIMITER_SUGGESTS'), scope='api')
else:
    api_rate_limiter_suggests = dummy_decorator

api_views.SuggestJournals.decorators = [api_rate_limiter_suggests]
api.add_resource(api_views.SuggestJournals, '/api/suggests')

# get URL/DOI
if app.config.get('API_RATE_LIMITER_GET') is not None:
    api_rate_limiter_get = limiter.shared_limit(app.config.get('API_RATE_LIMITER_GET'), scope='api')
else:
    api_rate_limiter_get = dummy_decorator

api_views.GetURL.decorators = [api_rate_limiter_get]
api.add_resource(api_views.GetURL, '/api/url')

api_views.GetDOI.decorators = [api_rate_limiter_get]
api.add_resource(api_views.GetDOI, '/api/doi')

# MAIN
if __name__ == '__main__':
    app.run()

if __name__ != '__main__':
    # same level of logging between gunicorn and Flask
    # (see https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
