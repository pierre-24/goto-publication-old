from typing import Tuple, Union
from flask_restful import Resource, reqparse

from goto_publi import REGISTRY, registry


def make_error(msg: str, arg: str, code: int = 400) -> Tuple[dict, int]:
    return {'message': {arg: msg}}, code


class SuggestJournals(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('q', type=str, required=True)

    def get(self) -> Union[dict, Tuple[dict, int]]:
        args = self.parser.parse_args()

        return {
            'suggestions': REGISTRY.suggest_journals(args.get('q'))
        }


class GetURL(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('journal', type=str, required=True)
        self.parser.add_argument('volume', type=str, required=True)
        self.parser.add_argument('page', type=str, required=True)

    def get(self) -> Union[dict, Tuple[dict, int]]:
        args = self.parser.parse_args()

        try:
            url = REGISTRY.get_url(args.get('journal'), args.get('volume'), args.get('page'))
        except registry.RegistryError as e:
            return make_error(e.what, e.var)

        return {
            'url': url
        }