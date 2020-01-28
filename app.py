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

if app.config.get('API_RATE_LIMITER') is not None:
    api_limit = limiter.shared_limit(app.config.get('API_RATE_LIMITER'), scope='api')
else:
    def dummy(f):
        return f

    api_limit = dummy

# API
api = Api(app)

api_views.ListJournals.decorators = [api_limit]
api.add_resource(api_views.ListJournals, '/api/journals')

api_views.ListProviders.decorators = [api_limit]
api.add_resource(api_views.ListProviders, '/api/providers')

api_views.SuggestJournals.decorators = [api_limit]
api.add_resource(api_views.SuggestJournals, '/api/suggests')

api_views.GetURL.decorators = [api_limit]
api.add_resource(api_views.GetURL, '/api/url')

api_views.GetDOI.decorators = [api_limit]
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
