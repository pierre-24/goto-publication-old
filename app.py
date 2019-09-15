from flask import Flask, render_template
from flask_restful import Api

from goto_publication import api_views, __version__, __program_name__

# APP
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html', **{
        'prog_name': __program_name__,
        'prog_version': __version__
    })


# API
api = Api(app)

api.add_resource(api_views.SuggestJournals, '/api/suggests')
api.add_resource(api_views.GetURL, '/api/url')
api.add_resource(api_views.GetDOI, '/api/doi')


if __name__ == '__main__':
    app.run()
