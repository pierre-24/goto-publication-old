import requests
import re
import json
from bs4 import BeautifulSoup

from goto_publication.settings import API_KEY


class ProviderError(Exception):
    pass


class IncorrectJournalName(ProviderError):
    def __init__(self, *args):
        super().__init__('incorrect journal name', *args)


class ArticleNotFound(ProviderError):
    def __init__(self, *args):
        super().__init__('article not found', *args)


API_KEY_FIELD = 'apiKey'


class Provider:
    CODE = ''
    NAME = ''
    WEBSITE_URL = ''  # /!\ please add trailing slash
    ICON_URL = ''
    JOURNALS = []

    API_KEY_KWARG = False

    def __init__(self):
        if self.ICON_URL == '':
            self.ICON_URL = self.WEBSITE_URL + 'favicon.ico'

    def get_info(self) -> dict:
        """Info that every request sends"""

        return {
            'providerName': self.NAME,
            'providerIcon': self.ICON_URL,
            'providerWebsite': self.WEBSITE_URL,
        }

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Get an url that go close to the actual article (a search page with the form filled, or in the
        best cases, the actual article).

        Normally, this is fast, because most of the time the link is forged without any request.
        On the other hand, there is no check, so it is not guaranteed to link to an actual article.
        """

        raise NotImplementedError()

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Get the DOI of the article.

        Slower than `get_url()`, because some requests are made. But the DOI is guaranteed to be exact.
        """

        raise NotImplementedError()


class AIP(Provider):
    """American Institute of Physics"""

    NAME = 'American Institute of Physics (AIP)'
    CODE = 'aip'
    WEBSITE_URL = 'https://aip.scitation.org/'

    JOURNALS = [
        'Journal of Applied Physics',
        'The Journal of Chemical Physics',
        'Journal of Mathematical Physics'
    ]

    base_url = WEBSITE_URL + 'action/quickLink'
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
            result = self.session.get(search_url, allow_redirects=False)
        if 'doi' not in result.headers['Location']:
            raise ArticleNotFound()

        return self.doi_regex.search(result.headers['Location']).group(1)


class ACS(AIP):
    """American chemical society. Their API is very close to the AIP one (except there is journal codes).
    """

    NAME = 'American Chemical Society'
    CODE = 'acs'
    WEBSITE_URL = 'https://pubs.acs.org/'

    journal_codes = {
        'Journal of the American Chemical Society': 'jacsat'
    }

    JOURNALS = list(journal_codes.keys())
    base_url = WEBSITE_URL + 'action/quickLink'

    def __init__(self):
        super().__init__()
        self.session = requests.session()

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        if journal not in self.journal_codes:
            raise IncorrectJournalName()

        return super().get_url(self.journal_codes[journal], volume, page)


class Wiley(Provider):
    """Wiley.

    Perform the request on their search page API, since there is no other correct API available.
    Sorry about that, open to any suggestion.
    """

    NAME = 'Wiley'
    CODE = 'wiley'
    WEBSITE_URL = 'https://onlinelibrary.wiley.com/'

    journal_codes = {
        'Chemistry - A European Journal': 15213765
    }

    JOURNALS = list(journal_codes.keys())

    api_url = WEBSITE_URL + 'action/quickLink'

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Require a single request to get the url (which contains the DOI)
        """
        if journal not in self.journal_codes:
            raise IncorrectJournalName()

        url = self.api_url + '?quickLinkJournal={j}&quickLinkVolume={v}&quickLinkPage={p}&quickLink=true'.format(
            j=self.journal_codes[journal], v=volume, p=page)

        result = requests.get(url)
        if result.status_code != 200:
            raise ProviderError('error while requesting search')

        j = result.json()
        if 'link' not in j:
            raise ArticleNotFound()

        return self.WEBSITE_URL + j['link'][1:]

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        result_url = self.get_url(journal, volume, page)
        p = result_url.find('abs/')
        if p == -1:
            raise ProviderError('cannot find DOI')

        return result_url[p + 4:]


class ScienceDirect(Provider):
    """Science Direct (Elsevier).

    Getting the DOI requires a valid API key (Get one at https://dev.elsevier.com/index.html).
    """

    NAME = 'ScienceDirect'
    CODE = 'sd'
    API_KEY_KWARG = 'true'
    WEBSITE_URL = 'https://www.sciencedirect.com/'
    ICON_URL = 'https://sdfestaticassets-eu-west-1.sciencedirectassets.com/shared-assets/18/images/favSD.ico'

    journal_codes = {
        'Chemical Physics': 271366
    }

    JOURNALS = list(journal_codes.keys())

    api_url = 'https://api.elsevier.com/content/search/sciencedirect'
    base_url = WEBSITE_URL + 'search/advanced'

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        if journal not in self.journal_codes:
            raise IncorrectJournalName()

        return self.base_url + '?cid={}&volume={}&page={}'.format(self.journal_codes[journal], volume, page)

    def _api_call(self, journal: str, volume: str, page: str, **kwargs) -> dict:
        """
        Uses the Science Direct API provided by Elsevier
        (see https://dev.elsevier.com/documentation/ScienceDirectSearchAPI.wadl, but actually, the ``PUT`` API is
        described in https://dev.elsevier.com/tecdoc_sdsearch_migration.html, since the ``GET`` one is decommissioned).

        **Requires an API key**.

        .. warning::

            Note that for this kind of usage, the person who uses the Elsevier API
            needs to be a member of an organization that subscribed to an Elsevier product
            (see https://dev.elsevier.com/policy.html, section "Federated Search").
        """

        api_key = kwargs.get(API_KEY_FIELD, API_KEY.get(self.NAME, ''))
        if api_key == '':
            raise ProviderError('no API key provided')

        response = requests.put(self.api_url, data=json.dumps({
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

        if v['resultsFound'] == 0:
            raise ArticleNotFound()
        elif v['resultsFound'] > 1:
            # happen when a journal matches different titles (ex "Chemical Physics" matches "Chemical Physics Letters")
            for r in v['results']:
                if r['sourceTitle'] == journal:
                    return r
            raise ProviderError('no exact match for journal {}!?'.format(journal))
        else:
            return v['results'][0]

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        d = self._api_call(journal, volume, page, **kwargs)
        return d['doi']


class Springer(Provider):
    """Springer have a messed up notation for its article (mixing between pages and article number)
    and their API (https://dev.springernature.com/adding-constraints) does not provide a page or article number search
    (and does not give the article number anyway, except ``e-location`` in the jats output, which is sloooooow).

    Thus, it is impossible to get the exact URL or DOI without any further information.
    """

    NAME = 'Springer'
    CODE = 'sl'  # = SpringerLink
    WEBSITE_URL = 'https://link.springer.com/'
    ICON_URL = \
        'https://link.springer.com/static/17c1f2edc5a95a03d2f5f7b0019142685841f5ad/sites/link/images/favicon-32x32.png'

    journal_codes = {
        'Theoretical Chemistry Accounts': 214,
        'Theoretica chimica acta': 214,
    }

    JOURNALS = list(journal_codes.keys())

    base_url = WEBSITE_URL + 'journal/'

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """TOC of the volume, find your way into that ;)
        """
        if journal not in self.journal_codes:
            raise IncorrectJournalName()

        return self.base_url + '/{}/volume/{}/toc'.format(self.journal_codes[journal], volume)


class Nature(Provider):
    """Even though they have an OpenSearch API (https://www.nature.com/opensearch/), not
    everything seems to be indexed in it (not much of Nature for years < 2010, for example).

    Therefore, this one will rely on the search page.
    """

    NAME = 'Nature'
    CODE = 'nat'
    DOI_BASE = '10.1038'
    WEBSITE_URL = 'https://www.nature.com/'

    journal_codes = {
        'Nature': 'nature'
    }

    JOURNALS = list(journal_codes.keys())

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        if journal not in self.journal_codes:
            raise IncorrectJournalName()

        url = self.WEBSITE_URL + 'search?journal={}&volume={}&spage={}'.format(
            self.journal_codes[journal], volume, page)

        return url

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Requires a request"""

        url = self.get_url(journal, volume, page, **kwargs)

        soup = BeautifulSoup(requests.get(url).content, 'lxml')
        links = soup.find_all(attrs={'data-track-action': 'search result'})

        if len(links) == 0:
            raise ArticleNotFound()
        elif len(links) > 1:
            raise ProviderError('More than one result?!')  # TODO: that may happen, though

        return links[0].attrs['href'].replace('/articles', self.DOI_BASE)


class RSC(Provider):
    """Royal society of Chemistry

    No trace of an API, but a painful two-request process to get any result:
    the actual result page takes a long (mostly base64) payload as POST input, but this payload cannot be forged in
    advance (it seems to contain, at least, some information on the system which generates it).
    """

    NAME = 'Royal society of Chemistry'
    CODE = 'rsc'
    WEBSITE_URL = 'https://pubs.rsc.org/'

    journal_codes = {
        'Physical Chemistry Chemical Physics (PCCP)': 'phys. chem. chem. phys.'
    }

    JOURNALS = list(journal_codes.keys())
    search_url = WEBSITE_URL + 'en/results'
    search_result_url = WEBSITE_URL + 'en/search/journalresult'

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        if journal not in self.journal_codes:
            raise IncorrectJournalName()

        url = self.search_url + '?artrefjournalname={}&artrefvolumeyear={}&artrefstartpage={}&fcategory=journal'.format(
            self.journal_codes[journal], volume, page)

        return url

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        """Requires 2 (!) requests.

        Note: for some reasons, an user-agent is mandatory
        """

        url = self.get_url(journal, volume, page)

        response = requests.get(url, headers={'User-Agent': 'tmp'})
        s = BeautifulSoup(response.content, 'lxml').find('input', attrs={'name': 'SearchTerm'}).attrs['value']
        response = requests.post(self.search_result_url, data={
            'searchterm': s,
            'resultcount': 1,
            'category': 'journal',
            'pageno': 1
        }, headers={'User-Agent': 'goto-publi/0.1'})

        if len(response.content) < 50:
            raise ArticleNotFound()

        links = BeautifulSoup(response.content, 'lxml').select('.text--small a')

        if len(links) == 0:
            raise ProviderError('article not found, did you put the first page?')
        elif len(links) > 1:
            raise ProviderError('More than one result?!')

        return links[0].attrs['href'][16:]
