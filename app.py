from flask import Flask, render_template
from flask_restful import Api

from goto_publi import api_views

# APP
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


# API
api = Api(app)

api.add_resource(api_views.SuggestJournals, '/api/suggests')
api.add_resource(api_views.GetURL, '/api/url')


if __name__ == '__main__':
    app.run()
