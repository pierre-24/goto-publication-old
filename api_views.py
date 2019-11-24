from typing import Tuple, Union, Callable
from flask_restful import Resource, reqparse

from goto_publication import registry
from goto_publication.providers import API_KEY_FIELD

import settings

REGISTRY = registry.Registry(settings.REGISTER_PATH, settings.PROVIDERS)


def make_error(msg: str, arg: str) -> dict:
    return {'message': {arg: msg}}


class SuggestJournals(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('q', type=str, required=True)
        self.parser.add_argument('source', default='name', choices=['name', 'abbr'])

    def get(self) -> Union[dict, Tuple[dict, int]]:
        args = self.parser.parse_args()

        try:
            return {
                'request': args.get('q'),
                'source': args.get('source'),
                'suggestions': REGISTRY.suggest_journals(args.get('q'), args.get('source'))
            }
        except registry.RegistryError as e:
            return make_error(e.what, e.var), 400


main_parser = reqparse.RequestParser()
main_parser.add_argument('journal', type=str, required=True)
main_parser.add_argument('volume', type=str, required=True)
main_parser.add_argument('page', type=str, required=True)
main_parser.add_argument(API_KEY_FIELD, type=str)


class GetInfo(Resource):
    def __init__(self):
        self.parser = main_parser
        self.journal = ''
        self.volume = ''
        self.page = ''
        self.apiKey = ''

    def _get_func_args(self) -> dict:
        args = self.parser.parse_args()

        self.journal = args.get('journal')
        self.volume = args.get('volume')
        self.page = args.get('page')

        func_args = {
            'journal': self.journal,
            'volume': self.volume,
            'page': self.page
        }

        if args.get(API_KEY_FIELD):
            self.apiKey = args.get(API_KEY_FIELD)
            func_args[API_KEY_FIELD] = self.apiKey

        return func_args

    def get(self) -> Union[dict, Tuple[dict, int]]:
        func_args = self._get_func_args()

        request = {
            'journal': self.journal,
            'volume': self.volume,
            'page': self.page
        }

        if self.apiKey:
            request.update({API_KEY_FIELD: self.apiKey})

        response = {'request': request}
        response_code = 200

        try:
            response.update({'result': self._get_response_func()(**func_args)})
        except registry.RegistryError as e:
            response.update(make_error(e.what, e.var))
            response_code = 400

        return response, response_code

    def _get_response_func(self) -> Callable[[str, str, str, dict], dict]:
        raise NotImplementedError()


class GetURL(GetInfo):
    def _get_response_func(self) -> Callable[[str, str, str, dict], dict]:
        return REGISTRY.get_url


class GetDOI(GetInfo):
    def _get_response_func(self) -> Callable[[str, str, str, dict], dict]:
        return REGISTRY.get_doi
