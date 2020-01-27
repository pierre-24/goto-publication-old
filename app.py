import logging

from flask import Flask, render_template
from flask_restful import Api

import settings
import api_views

# APP
app = Flask(__name__)
app.config.from_mapping(**settings.APP_CONFIG)


@app.route('/')
def hello_world():
    return render_template('index.html', **settings.WEBPAGE_INFO)


# API
api = Api(app)

api.add_resource(api_views.ListJournals, '/api/journals')
api.add_resource(api_views.ListProviders, '/api/providers')
api.add_resource(api_views.SuggestJournals, '/api/suggests')
api.add_resource(api_views.GetURL, '/api/url')
api.add_resource(api_views.GetDOI, '/api/doi')


if __name__ == '__main__':
    app.run()


if __name__ != '__main__':
    # same level of logging between gunicorn and Flask
    # (see https://medium.com/@trstringer/logging-flask-and-gunicorn-the-manageable-way-2e6f0b8beb2f)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
