import requests
import re


class ProviderError(Exception):
    pass


class Provider:
    PROVIDER_CODE = ''
    PROVIDER_NAME = ''
    JOURNALS = []

    def __init__(self):
        pass

    def get_url(self, journal: str, volume: str, page: str) -> str:
        raise NotImplementedError()

    def get_doi(self, journal: str, volume: str, page: str) -> str:
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

    def get_url(self, journal: str, volume: str, page: str) -> str:
        """Requires no request
        """

        return self.base_url + '?quickLinkJournal={j}&quickLinkVolume={v}&quickLinkPage={p}&quickLink=true'.format(
            j=journal, v=volume, p=page)

    def get_doi(self, journal: str, volume: str, page: str) -> str:
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

    def get_url(self, journal: str, volume: str, page: str) -> str:
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

    def get_url(self, journal: str, volume: str, page: str) -> str:
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

    def get_doi(self, journal: str, volume: str, page: str) -> str:
        result_url = self.get_url(journal, volume, page)
        p = result_url.find('abs/')
        if p == -1:
            raise ProviderError('cannot find DOI')

        return result_url[p + 4:]