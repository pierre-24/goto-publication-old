from typing import Tuple, Union
from flask_restful import Resource, reqparse

from goto_publi import REGISTRY, registry
from goto_publi.providers import API_KEY_FIELD


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


main_parser = reqparse.RequestParser()
main_parser.add_argument('journal', type=str, required=True)
main_parser.add_argument('volume', type=str, required=True)
main_parser.add_argument('page', type=str, required=True)
main_parser.add_argument(API_KEY_FIELD, type=str)


class GetInfo(Resource):
    def __init__(self):
        self.parser = main_parser

    def _get_func_args(self) -> dict:
        args = self.parser.parse_args()

        func_args = {
            'journal': args.get('journal'),
            'volume': args.get('volume'),
            'page': args.get('page')
        }

        if args.get(API_KEY_FIELD):
            func_args[API_KEY_FIELD] = args.get(API_KEY_FIELD)

        return func_args


class GetURL(GetInfo):

    def get(self) -> Union[dict, Tuple[dict, int]]:
        try:
            url = REGISTRY.get_url(**self._get_func_args())
        except registry.RegistryError as e:
            return make_error(e.what, e.var)
        except NotImplementedError:
            return make_error('Not implemented yet for this journal', 'journal')

        return {
            'url': url
        }


class GetDOI(GetInfo):

    def get(self) -> Union[dict, Tuple[dict, int]]:
        try:
            doi = REGISTRY.get_doi(**self._get_func_args())
        except registry.RegistryError as e:
            return make_error(e.what, e.var)
        except NotImplementedError:
            return make_error('Not implemented yet for this journal', 'journal')

        return {
            'doi': doi,
            'url': 'https://dx.doi.org/' + doi
        }
