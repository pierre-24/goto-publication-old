import requests
import re
import json
from bs4 import BeautifulSoup

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


class Springer(Provider):
    """Springer have a messed up notation for its article (mixing between pages and article number)
    and their API (https://dev.springernature.com/adding-constraints) does not provide a page or article number search
    (and does not give the article number anyway, except ``e-location`` in the jats output, which is sloooooow).

    Thus, it is impossible to get the exact URL or DOI without any further information.
    """

    PROVIDER_NAME = 'Springer'
    PROVIDER_CODE = 'sl'  # = SpringerLink

    journal_codes = {
        'Theoretical Chemistry Accounts': 214,
        'Theoretica chimica acta': 214,
    }

    JOURNALS = list(journal_codes.keys())

    base_url = 'https://link.springer.com/journal/'

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """TOC of the volume, find your way into that ;)
        """
        if journal not in self.journal_codes:
            raise ProviderError('not a valid name: {}'.format(journal))

        return self.base_url + '/{}/volume/{}/toc'.format(self.journal_codes[journal], volume)


class Nature(Provider):
    """Even though they have an OpenSearch API (https://www.nature.com/opensearch/), not
    everything seems to be indexed in it (not much of Nature for years < 2010, for example).

    Therefore, this one will rely on the search page.
    """

    PROVIDER_NAME = 'Nature'
    PROVIDER_CODE = 'nat'
    DOI_BASE = '10.1038'

    journal_codes = {
        'Nature': 'nature'
    }

    JOURNALS = list(journal_codes.keys())
    base_url = 'https://www.nature.com'

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Requires a request"""

        if journal not in self.journal_codes:
            raise ProviderError('not a valid name: {}'.format(journal))

        url = self.base_url + '/search?journal={}&volume={}&spage={}'.format(
            self.journal_codes[journal], volume, page)

        soup = BeautifulSoup(requests.get(url).content, 'lxml')
        links = soup.find_all(attrs={'data-track-action': 'search result'})

        if len(links) == 0:
            raise ProviderError('article not found, did you put the first page?')
        elif len(links) > 1:
            raise ProviderError('More than one result?!')  # TODO: that may happen, though

        return self.base_url + links[0].attrs['href']

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        url = self.get_url(journal, volume, page, **kwargs)
        return url.replace(self.base_url + '/articles', self.DOI_BASE)


class RSC(Provider):
    """Royal society of Chemistry

    No trace of an API, but a painful two-request process to get any result:
    the actual result page takes a long (mostly base64) payload as POST input, but this payload cannot be forged in
    advance (it seems to contain, at least, some information on the system which generates it).
    """

    PROVIDER_NAME = 'Royal society of Chemistry'
    PROVIDER_CODE = 'rsc'

    journal_codes = {
        'Physical Chemistry Chemical Physics (PCCP)': 'phys. chem. chem. phys.'
    }

    JOURNALS = list(journal_codes.keys())

    base_url = 'https://pubs.rsc.org'
    search_url = base_url + '/en/results'
    search_result_url = base_url + '/en/search/journalresult'

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Requires 2 (!) requests. For efficiency, the result will be the DOI link.

        Note: for some reasons, an user-agent is mandatory
        """

        if journal not in self.journal_codes:
            raise ProviderError('not a valid name: {}'.format(journal))

        url = self.search_url + '?artrefjournalname={}&artrefvolumeyear={}&artrefstartpage={}&fcategory=journal'.format(
            self.journal_codes[journal], volume, page)

        response = requests.get(url, headers={'User-Agent': 'tmp'})
        s = BeautifulSoup(response.content, 'lxml').find('input', attrs={'name': 'SearchTerm'}).attrs['value']
        response = requests.post(self.search_result_url, data={
            'searchterm': s,
            'resultcount': 1,
            'category': 'journal',
            'pageno': 1
        }, headers={'User-Agent': 'goto-publi/0.1'})

        if len(response.content) < 50:
            raise ProviderError('article not found')

        links = BeautifulSoup(response.content, 'lxml').select('.text--small a')

        if len(links) == 0:
            raise ProviderError('article not found, did you put the first page?')
        elif len(links) > 1:
            raise ProviderError('More than one result?!')

        return links[0].attrs['href']

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        return self.get_url(journal, volume, page)[16:]
