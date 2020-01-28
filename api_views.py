from typing import Tuple, Union, Callable, List, Any
from flask_restful import Resource, reqparse

from goto_publication import registry
from goto_publication.providers import API_KEY_FIELD

import settings

REGISTRY = registry.Registry(settings.REGISTRY_PATH, settings.PROVIDERS)


def make_error(msg: str, arg: str) -> dict:
    return {'message': {arg: msg}}


class ListAPIView(Resource):
    list_field_name = 'list'

    def _get_list(self, start: int, count: int) -> List[Any]:
        raise NotImplementedError()

    def _get_total(self) -> int:
        raise NotImplementedError()

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('start', type=int, default=0)
        self.parser.add_argument('count', type=int, default=settings.API_CONFIG['DEFAULT_COUNT'])

    def get(self) -> Union[dict, Tuple[dict, int]]:
        args = self.parser.parse_args()

        if args.count > settings.API_CONFIG['MAX_COUNT'] or args.count < 0:
            return make_error('count must be between 0 and {}'.format(settings.API_CONFIG['MAX_COUNT']), 'count'), 400

        li = self._get_list(args.start, args.count)

        return {
            'start': args.start,
            'count': len(li),
            'total': self._get_total(),
            self.list_field_name: li
        }


class ListProviders(ListAPIView):
    list_field_name = 'providers'

    def _get_list(self, start: int, count: int) -> List[Any]:
        return list(p.get_info() for p in REGISTRY.providers.values())[start:start + count]

    def _get_total(self) -> int:
        return len(REGISTRY.providers)


class ListJournals(ListAPIView):
    def _get_list(self, start: int, count: int) -> List[Any]:
        journals = []

        for j in list(REGISTRY.journals.values())[start:start + count]:
            info = {
                'journal': j.name,
                'abbreviation': j.abbr
            }

            info.update(**j.provider.get_info())
            journals.append(info)

        return journals

    def _get_total(self) -> int:
        return len(REGISTRY.journals)


class SuggestJournals(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('q', type=str, required=True)
        self.parser.add_argument('source', default='name', choices=['name', 'abbr'])
        self.parser.add_argument('cutoff', type=float, default=settings.API_CONFIG['DEFAULT_CUTOFF'])
        self.parser.add_argument('count', type=int, default=settings.API_CONFIG['DEFAULT_NUM_SUGGESTIONS'])

    def get(self) -> Union[dict, Tuple[dict, int]]:
        args = self.parser.parse_args()

        if args.count > settings.API_CONFIG['MAX_COUNT'] or args.count < 0:
            return make_error('count must be between 0 and {}'.format(settings.API_CONFIG['MAX_COUNT']), 'count'), 400

        if args.cutoff < .0 or args.cutoff > 1:
            return make_error('cutoff must be between 0 and 1', 'cutoff'), 400

        try:
            return {
                'request': args.get('q'),
                'source': args.get('source'),
                'count': args.get('count'),
                'cutoff': args.get('cutoff'),
                'suggestions': REGISTRY.suggest_journals(
                    args.get('q'), args.get('source'), args.get('count'), args.get('cutoff')
                )
            }
        except registry.RegistryError as e:
            return make_error(e.what, e.var), 400


class GetInfo(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('journal', type=str, required=True)
        self.parser.add_argument('volume', type=str, required=True)
        self.parser.add_argument('page', type=str, required=True)
        self.parser.add_argument(API_KEY_FIELD, type=str)

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
