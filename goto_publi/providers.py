import requests
import re
import json

from goto_publi.settings import API_KEY


class ProviderError(Exception):
    pass


API_KEY_FIELD = 'apiKey'


class Provider:
    PROVIDER_CODE = ''
    PROVIDER_NAME = ''
    JOURNALS = []

    API_KEY_KWARG = False

    def __init__(self):
        pass

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        raise NotImplementedError()

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        raise NotImplementedError()


class AIP(Provider):
    """American Institute of Physics"""

    PROVIDER_NAME = 'American Institute of Physics (AIP)'
    PROVIDER_CODE = 'aip'

    JOURNALS = [
        'Journal of Applied Physics',
        'The Journal of Chemical Physics',
        'Journal of Mathematical Physics'
    ]

    base_url = 'https://aip.scitation.org/action/quickLink'

    doi_regex = re.compile(r'abs/(.*/.*)\?')

    def __init__(self):
        super().__init__()
        self.session = requests.session()

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Requires no request
        """

        return self.base_url + '?quickLinkJournal={j}&quickLinkVolume={v}&quickLinkPage={p}&quickLink=true'.format(
            j=journal, v=volume, p=page)

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Requires a request, and eventually a second to set up the cookies.
        """

        search_url = self.get_url(journal, volume, page)
        result = self.session.get(search_url, allow_redirects=False)
        if result.status_code != 302:
            raise ProviderError('article not found')
        if 'cookieSet' in result.headers['Location']:
            print('in again !')
            result = self.session.get(search_url, allow_redirects=False)
        if 'doi' not in result.headers['Location']:
            raise ProviderError('article not found')

        return self.doi_regex.search(result.headers['Location']).group(1)


class ACS(AIP):
    """American chemical society. Their API is very close to the AIP one (except there is journal codes).
    """

    PROVIDER_NAME = 'American Chemical Society'
    PROVIDER_CODE = 'acs'

    journal_codes = {
        'Journal of the American Chemical Society': 'jacsat'
    }

    JOURNALS = list(journal_codes.keys())
    base_url = 'https://pubs.acs.org/action/quickLink'

    def __init__(self):
        super().__init__()
        self.session = requests.session()

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        if journal not in self.journal_codes:
            raise ProviderError('not a valid name: {}'.format(journal))

        return super().get_url(self.journal_codes[journal], volume, page)


class Wiley(Provider):
    """Wiley.

    Perform the request on their search page API, since there is no other correct API available.
    Sorry 'bout that, open to any suggestion.
    """

    PROVIDER_NAME = 'Wiley'
    PROVIDER_CODE = 'wiley'

    journal_codes = {
        'Chemistry - A European Journal': 15213765
    }

    JOURNALS = list(journal_codes.keys())

    api_url = 'https://onlinelibrary.wiley.com/action/quickLink'
    base_url = 'https://onlinelibrary.wiley.com'

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Require a single request to get the url (which contains the DOI)
        """
        if journal not in self.journal_codes:
            raise ProviderError('not a valid name: {}'.format(journal))

        url = self.api_url + '?quickLinkJournal={j}&quickLinkVolume={v}&quickLinkPage={p}&quickLink=true'.format(
            j=self.journal_codes[journal], v=volume, p=page)

        result = requests.get(url)
        if result.status_code != 200:
            raise ProviderError('error while requesting wiley API')

        j = result.json()
        if 'link' not in j:
            raise ProviderError('unknown article, check your inputs')

        return self.base_url + j['link']

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        result_url = self.get_url(journal, volume, page)
        p = result_url.find('abs/')
        if p == -1:
            raise ProviderError('cannot find DOI')

        return result_url[p + 4:]


class ScienceDirect(Provider):
    """Uses the Science Direct API provided by Elsevier
    (see https://dev.elsevier.com/documentation/ScienceDirectSearchAPI.wadl, but actually, the ``PUT`` API is
    described in https://dev.elsevier.com/tecdoc_sdsearch_migration.html, since the ``GET`` one is decommissioned).

    **Requires an API key**.

    .. warning::

        Note that for this kind of usage, the person who uses the Elsevier API
        needs to be a member of an organization that subscribed to an Elsevier product
        (see https://dev.elsevier.com/policy.html, section "Federated Search").
    """

    PROVIDER_NAME = 'ScienceDirect'
    PROVIDER_CODE = 'sd'
    API_KEY_KWARG = 'true'

    JOURNALS = [
        'Chemical Physics'
    ]

    base_url = 'https://api.elsevier.com/content/search/sciencedirect'

    def _api_call(self, journal: str, volume: str, page: str, **kwargs) -> dict:
        api_key = kwargs.get(API_KEY_FIELD, API_KEY.get(self.PROVIDER_NAME, ''))
        if api_key == '':
            raise ProviderError('no API key provided')

        response = requests.put(self.base_url, data=json.dumps({
            'qs': '*',
            'pub': journal,
            'volume': volume,
            'page': page
        }), headers={
            'Accept': 'application/json',
            'X-ELS-APIKey': api_key,
            'Content-Type': 'application/json'
        })

        v = response.json()
        if 'resultsFound' not in v:
            if 'service-error' in v:
                raise ProviderError('{} (API error)'.format(v['service-error']['status']['statusText']))
            if 'message' in v:
                raise ProviderError('{} (API usage error)'.format(v['message']))
            raise ProviderError('error while calling the API')

        if v['resultsFound'] > 1:
            # happen when a journal matches different titles (ex "Chemical Physics" matches "Chemical Physics Letters")
            for r in v['results']:
                if r['sourceTitle'] == journal:
                    return r
            raise ProviderError('no exact match for journal {}!?'.format(journal))
        else:
            return v['results'][0]

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        d = self._api_call(journal, volume, page, **kwargs)
        return d['uri']

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        d = self._api_call(journal, volume, page, **kwargs)
        return d['doi']
