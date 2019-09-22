import requests
import re
import json
from bs4 import BeautifulSoup
from typing import Dict

from goto_publication.int_map import IntMap, N0, S
from goto_publication.settings import API_KEY


class ProviderError(Exception):
    pass


class IncorrectJournalName(ProviderError):
    def __init__(self, *args):
        super().__init__('incorrect journal name', *args)


class IncorrectVolume(ProviderError):
    def __init__(self, *args):
        super().__init__('incorrect volume', *args)


class ArticleNotFound(ProviderError):
    def __init__(self, *args):
        super().__init__('article not found', *args)


class NoJournalList(ProviderError):
    pass


API_KEY_FIELD = 'apiKey'


class Provider:
    CODE = ''
    NAME = ''
    WEBSITE_URL = ''  # !! please add trailing slash
    ICON_URL = ''
    JOURNALS = {}

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

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        """Get an url that go close to the actual article (a search page with the form filled, or in the
        best cases, the actual article).

        Normally, this is fast, because most of the time the link is forged without any request.
        On the other hand, there is no check, so it is not guaranteed to link to an actual article.
        """

        raise NotImplementedError()

    def get_doi(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        """Get the DOI of the article.

        Slower than `get_url()`, because some requests are made. But the DOI is guaranteed to be exact.
        """

        raise NotImplementedError()

    def get_journals(self) -> Dict[str, IntMap]:
        """Retrieve, at **any** cost, a list of the journals of this provider.
        """

        raise NotImplementedError()


# !! Please keep the list alphabetic


class ACS(Provider):
    """American chemical society. Their API is very close to the AIP one (except there is journal codes).
    """

    NAME = 'American Chemical Society'
    CODE = 'acs'
    WEBSITE_URL = 'https://pubs.acs.org/'

    JOURNALS = {
        'Accounts of Chemical Research': IntMap([('achre4', N0)]),
        'ACS Applied Bio Materials': IntMap([('aabmcb', N0)]),
        'ACS Applied Electronic Materials': IntMap([('aaembp', N0)]),
        'ACS Applied Energy Materials': IntMap([('aaemcq', N0)]),
        'ACS Applied Materials & Interfaces': IntMap([('aamick', N0)]),
        'ACS Applied Nano Materials': IntMap([('aanmf6', N0)]),
        'ACS Biomaterials Science & Engineering': IntMap([('abseba', N0)]),
        'ACS Catalysis': IntMap([('accacs', N0)]),
        'ACS Central Science': IntMap([('acscii', N0)]),
        'ACS Chemical Biology': IntMap([('acbcct', N0)]),
        'ACS Chemical Neuroscience': IntMap([('acncdm', N0)]),
        'ACS Combinatorial Science': IntMap([('acsccc', N0)]),
        'ACS Earth and Space Chemistry': IntMap([('aesccq', N0)]),
        'ACS Energy Letters': IntMap([('aelccp', N0)]),
        'ACS Infectious Diseases': IntMap([('aidcbc', N0)]),
        'ACS Macro Letters': IntMap([('amlccd', N0)]),
        'ACS Medicinal Chemistry Letters': IntMap([('amclct', N0)]),
        'ACS Nano': IntMap([('ancac3', N0)]),
        'ACS Omega': IntMap([('acsodf', N0)]),
        'ACS Pharmacology & Translational Science': IntMap([('aptsfn', N0)]),
        'ACS Photonics': IntMap([('apchd5', N0)]),
        'ACS Sensors': IntMap([('ascefj', N0)]),
        'ACS Sustainable Chemistry & Engineering': IntMap([('ascecg', N0)]),
        'ACS Synthetic Biology': IntMap([('asbcd6', N0)]),
        'Analytical Chemistry': IntMap([('ancham', N0)]),
        'Biochemistry': IntMap([('bichaw', N0)]),
        'Bioconjugate Chemistry': IntMap([('bcches', N0)]),
        'Biomacromolecules': IntMap([('bomaf6', N0)]),
        'Biotechnology Progress': IntMap([('bipret', N0)]),
        'C&EN Global Enterprise': IntMap([('cgeabj', N0)]),
        'Chemical & Engineering News Archive': IntMap([('cenear', N0)]),
        'Chemical Research in Toxicology': IntMap([('crtoec', N0)]),
        'Chemical Reviews': IntMap([('chreay', N0)]),
        'Chemistry of Materials': IntMap([('cmatex', N0)]),
        'Crystal Growth & Design': IntMap([('cgdefu', N0)]),
        'Energy & Fuels': IntMap([('enfuem', N0)]),
        'Environmental Science & Technology': IntMap([('esthag', N0)]),
        'Environmental Science & Technology Letters': IntMap([('estlcu', N0)]),
        'I&EC Product Research and Development': IntMap([('iepra6.2', N0)]),
        'Industrial & Engineering Chemistry': IntMap([('iechad', N0)]),
        'Industrial & Engineering Chemistry Analytical Edition': IntMap([('iecac0', N0)]),
        'Industrial & Engineering Chemistry Chemical & Engineering Data Series': IntMap([('iecjc0', N0)]),
        'Industrial & Engineering Chemistry Fundamentals': IntMap([('iecfa7', N0)]),
        'Industrial & Engineering Chemistry Process Design and Development': IntMap([('iepdaw', N0)]),
        'Industrial & Engineering Chemistry Product Research and Development': IntMap([('iepra6', N0)]),
        'Industrial & Engineering Chemistry Research': IntMap([('iecred', N0)]),
        'Industrial and Engineering Chemistry, News Edition': IntMap([('iecnav', N0)]),
        'Inorganic Chemistry': IntMap([('inocaj', N0)]),
        'Journal of Agricultural and Food Chemistry': IntMap([('jafcau', N0)]),
        'Journal of Chemical & Engineering Data': IntMap([('jceaax', N0)]),
        'Journal of Chemical Documentation': IntMap([('jci001', N0)]),
        'Journal of Chemical Education': IntMap([('jceda8', N0)]),
        'Journal of Chemical Information and Computer Sciences': IntMap([('jcics1', N0)]),
        'Journal of Chemical Information and Modeling': IntMap([('jcisd8', N0)]),
        'Journal of the American Chemical Society': IntMap([('jacsat', N0)]),
        'Journal of Chemical Theory and Computation': IntMap([('jctcce', N0)]),
        'Journal of Combinatorial Chemistry': IntMap([('jcchff', N0)]),
        'Journal of Industrial & Engineering Chemistry': IntMap([('iechad.1', N0)]),
        'Journal of Medicinal and Pharmaceutical Chemistry': IntMap([('jmcmar.1', N0)]),
        'Journal of Medicinal Chemistry': IntMap([('jmcmar', N0)]),
        'Journal of Natural Products': IntMap([('jnprdf', N0)]),
        'The Journal of Organic Chemistry': IntMap([('joceah', N0)]),
        'The Journal of Physical Chemistry': IntMap([('jpchax.2', N0)]),
        'The Journal of Physical Chemistry A': IntMap([('jpcafh', N0)]),
        'The Journal of Physical Chemistry B': IntMap([('jpcbfk', N0)]),
        'The Journal of Physical Chemistry C': IntMap([('jpccck', N0)]),
        'The Journal of Physical Chemistry Letters': IntMap([('jpclcd', N0)]),
        'Journal of Proteome Research': IntMap([('jprobs', N0)]),
        'Langmuir': IntMap([('langd5', N0)]),
        'Macromolecules': IntMap([('mamobx', N0)]),
        'Molecular Pharmaceutics': IntMap([('mpohbp', N0)]),
        'Nano Letters': IntMap([('nalefd', N0)]),
        'News Edition, American Chemical Society': IntMap([('neaca9', N0)]),
        'Organic Letters': IntMap([('orlef7', N0)]),
        'Organic Process Research & Development': IntMap([('oprdfk', N0)]),
        'Organometallics': IntMap([('orgnd7', N0)]), 'PNAS': IntMap([('pnas', N0)]),
        'Product R&D': IntMap([('iepra6.1', N0)]),
        'The Journal of Physical and Colloid Chemistry': IntMap([('jpchax.1', N0)])
    }

    base_url = WEBSITE_URL + 'action/quickLink'
    doi_regex = re.compile(r'abs/(.*/.*)\?')

    def __init__(self):
        super().__init__()
        self.session = requests.session()

    def __del__(self):
        if self.session is not None:
            self.session.close()

    def _get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        """Requires no request
        """

        return self.base_url + '?quickLinkJournal={j}&quickLinkVolume={v}&quickLinkPage={p}&quickLink=true'.format(
            j=journal, v=volume, p=page)

    def get_doi(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        """Requires a request, and eventually a second to set up the cookies.
        """

        search_url = self.get_url(journal, volume, page)
        result = self.session.get(search_url, allow_redirects=False)

        if result.status_code != 302:
            raise ArticleNotFound()
        if 'cookieSet' in result.headers['Location'] or 'quickLink=true' in result.headers['Location']:
            result = self.session.get(search_url, allow_redirects=False)  # request twice after setting cookies

        if 'doi' not in result.headers['Location']:
            raise ArticleNotFound()

        return self.doi_regex.search(result.headers['Location']).group(1)

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        if journal not in self.JOURNALS:
            raise IncorrectJournalName()

        try:
            j = self.JOURNALS[journal][int(volume)]
        except KeyError:
            raise IncorrectVolume()
        except ValueError:
            raise ProviderError('volume is not an integer')

        return self._get_url(j, volume, page, **kwargs)

    def get_journals(self) -> Dict[str, IntMap]:
        result = self.session.get(self.WEBSITE_URL)
        if result.status_code != 200:
            raise NoJournalList()

        soup = BeautifulSoup(result.content, 'lxml')
        opts = soup.find('select', attrs={'class': 'quick-search_journals-select'}).find_all('option')

        journals = {}
        for o in opts:
            if o.attrs['value'] != '':
                journals[o.text] = IntMap((o.attrs['value'], N0))

        return journals


class APS(Provider):
    """American Physical Society"""

    NAME = 'American Physical Society'
    CODE = 'aps'
    WEBSITE_URL = 'https://journals.aps.org/'
    ICON_URL = 'https://cdn.journals.aps.org/development/journals/images/favicon.ico'

    JOURNALS = {
        'Physical Review Letters': IntMap([(('prl', 'PhysRevLett'), N0)]),
        'Physical Review X': IntMap([(('prx', 'PhysRevX'), N0)]),
        'Reviews of Modern Physics': IntMap([(('rmp', 'RevModPhys'), N0)]),
        'Physical Review A': IntMap([(('pra', 'PhysRevA'), N0)]),
        'Physical Review B': IntMap([(('prb', 'PhysRevB'), N0)]),
        'Physical Review C': IntMap([(('prc', 'PhysRevC'), N0)]),
        'Physical Review D': IntMap([(('prd', 'PhysRevD'), N0)]),
        'Physical Review E': IntMap([(('pre', 'PhysRevE'), N0)]),
        'Physical Review Research': IntMap([(('prresearch', 'PhysRevResearch'), N0)]),
        'Physical Review Accelerators and Beams': IntMap([(('prab', 'PhysRevAccelBeams'), N0)]),
        'Physical Review Applied': IntMap([(('prapplied', 'PhysRevApplied'), N0)]),
        'Physical Review Fluids': IntMap([(('prfluids', 'PhysRevFluids'), N0)]),
        'Physical Review Materials': IntMap([(('prmaterials', 'PhysRevMaterials'), N0)]),
        'Physical Review Physics Education Research': IntMap([(('prper', 'PhysRevPhysEducRes'), N0)]),
        'Physical Review': IntMap([(('pr', 'PhysRev'), S(1, 188))]),
        'Physical Review (Series I)': IntMap([(('pri', 'PhysRevSeriesI'), S(1, 35))])
    }

    DOI = '10.1103/{j2}.{v}.{p}'

    base_url = WEBSITE_URL + '{j1}/abstract/' + DOI

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        """Infers the article URL base on the way it is written (which is surprisingly easy).
        """

        if journal not in self.JOURNALS:
            raise IncorrectJournalName()

        try:
            j1, j2 = self.JOURNALS[journal][int(volume)]
        except KeyError:
            raise IncorrectVolume()
        except ValueError:
            raise ProviderError('volume is not an integer')

        return self.base_url.format(j1=j1, j2=j2, v=volume, p=page)

    def get_doi(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        """Only checks that the url gives a 200 response. If so, the DOI is valid.
        """
        url = self.get_url(journal, volume, page, **kwargs)
        response = requests.get(url)
        if response.status_code != 200:
            raise ArticleNotFound()

        return self.DOI.format(j2=self.JOURNALS[journal][volume][1], v=volume, p=page)

    def get_journals(self) -> Dict[str, IntMap]:

        response = requests.get(self.WEBSITE_URL + 'about')
        soup = BeautifulSoup(response.content, 'lxml')

        divs = soup.find_all('div', attrs={'class': 'article'})
        journals = {}

        for l in divs[:-1]:  # Remove "Physics", which is published by another provider
            a = l.find('a', attrs={'class': 'button'})
            title = l.find('h5').text
            journals[title] = IntMap(
                ((a.attrs['href'][1:-1], a.text[5:].replace('.', '').replace(' ', '')), N0))

        # add "Physical Review", which is not on the "about" page
        journals['Physical Review'] = IntMap((('pr', 'PhysRev'), S(1, 188)))
        journals['Physical Review (Series I)'] = IntMap((('pri', 'PhysRevSeriesI'), S(1, 35)))

        return journals


class AIP(ACS):
    """American Institute of Physics"""

    NAME = 'American Institute of Physics (AIP)'
    CODE = 'aip'
    WEBSITE_URL = 'https://aip.scitation.org/'

    JOURNALS = {
        'AIP Advances': IntMap([('', N0)]),
        'AIP Conference Proceedings': IntMap([('', N0)]),
        'APL Bioengineering': IntMap([('', N0)]),
        'APL Materials': IntMap([('', N0)]),
        'APL Photonics': IntMap([('', N0)]),
        'Applied Physics Letters': IntMap([('', N0)]),
        'Applied Physics Reviews': IntMap([('', N0)]),
        'Biomicrofluidics': IntMap([('', N0)]),
        'Chaos: An Interdisciplinary Journal of Nonlinear Science': IntMap([('', N0)]),
        'Computers in Physics': IntMap([('', N0)]),
        'Computing in Science & Engineering': IntMap([('', N0)]),
        'Journal of Physical & Chemical Reference Data': IntMap([('', N0)]),
        'Journal of Renewable & Sustainable Energy': IntMap([('', N0)]),
        'Journal of Applied Physics': IntMap([('', N0)]),
        'Journal of Mathematical Physics': IntMap([('', N0)]),
        'Low Temperature Physics': IntMap([('', N0)]),
        'Magnetism & Magnetic Materials': IntMap([('', N0)]),
        'Matter and Radiation at Extremes': IntMap([('', N0)]),
        'Physics of Fluids': IntMap([('', N0)]),
        'Physics of Plasmas': IntMap([('', N0)]),
        'Physics Today': IntMap([('', N0)]),
        'Review of Scientific Instruments': IntMap([('', N0)]),
        'Scilight': IntMap([('', N0)]),
        'Structural Dynamics': IntMap([('', N0)]),
        'The Journal of Chemical Physics': IntMap([('', N0)])
    }

    base_url = WEBSITE_URL + 'action/quickLink'

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        return self._get_url(journal, volume, page, **kwargs)

    def get_journals(self) -> Dict[str, IntMap]:
        result = self.session.get(self.WEBSITE_URL)
        if result.status_code != 200:
            raise NoJournalList()

        soup = BeautifulSoup(result.content, 'lxml')
        opts = soup.find('div', attrs={'class': 'scitation-journals-covers'})\
            .find_all('span', attrs={'class': 'journal-title'})

        journals = {}
        for o in opts:
            text = o.find('a').text.strip().replace(' (co-published with ACA)', '')
            journals[text] = IntMap(('', N0))

        return journals


class IOP(Provider):
    """Institute of Physics (IOP)"""

    NAME = 'Institute of Physics (IOP)'
    CODE = 'IOP'
    WEBSITE_URL = 'https://iopscience.iop.org/'

    JOURNALS = {
        'Journal of Physics A': IntMap(('1751-8121', N0))
    }

    base_url = WEBSITE_URL + 'findcontent'
    doi_regex = re.compile(r'article/(.*/.*/.*)\?')

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        if journal not in self.JOURNALS:
            raise IncorrectJournalName()

        try:
            j = self.JOURNALS[journal][int(volume)]
        except KeyError:
            raise IncorrectVolume()
        except ValueError:
            raise ProviderError('volume is not an integer')

        return self.base_url + '?CF_JOURNAL={}&CF_VOLUME={}&CF_ISSUE=&CF_PAGE={}'.format(j, volume, page)

    def get_doi(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        url = self.get_url(journal, volume, page, **kwargs)

        result = requests.get(url, allow_redirects=False, headers={'User-Agent': 'tmp'})
        if result.status_code != 301 or 'article' not in result.headers['Location']:
            raise ArticleNotFound()

        return self.doi_regex.search(result.headers['Location']).group(1)

    def get_journals(self) -> Dict[str, IntMap]:
        print(self.WEBSITE_URL + 'journalList')
        result = requests.get(self.WEBSITE_URL + 'journalList', headers={'User-Agent': 'tmp'})
        if result.status_code != 200:
            raise NoJournalList()

        soup = BeautifulSoup(result.content, 'lxml')
        links = soup.find('div', attrs={'id': 'archive-titles-tab'}).find_all('a')
        print(links)

        return {}


class Nature(Provider):
    """Even though they have an OpenSearch API (https://www.nature.com/opensearch/), not
    everything seems to be indexed in it (not much of Nature for years < 2010, for example).

    Therefore, this one will rely on the search page.
    """

    NAME = 'Nature'
    CODE = 'nat'
    DOI_BASE = '10.1038'
    WEBSITE_URL = 'https://www.nature.com/'

    JOURNALS = {
        'Nature': IntMap(('nature', N0))
    }

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        if journal not in self.JOURNALS:
            raise IncorrectJournalName()

        try:
            j = self.JOURNALS[journal][int(volume)]
        except KeyError:
            raise IncorrectVolume()
        except ValueError:
            raise ProviderError('volume is not an integer')

        url = self.WEBSITE_URL + 'search?journal={}&volume={}&spage={}'.format(j, volume, page)

        return url

    def get_doi(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
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

    JOURNALS = {
        'Physical Chemistry Chemical Physics (PCCP)': IntMap(('phys. chem. chem. phys.', N0))
    }

    search_url = WEBSITE_URL + 'en/results'
    search_result_url = WEBSITE_URL + 'en/search/journalresult'

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        if journal not in self.JOURNALS:
            raise IncorrectJournalName()

        try:
            j = self.JOURNALS[journal][int(volume)]
        except KeyError:
            raise IncorrectVolume()
        except ValueError:
            raise ProviderError('volume is not an integer')

        url = self.search_url + '?artrefjournalname={}&artrefvolumeyear={}&artrefstartpage={}&fcategory=journal'.format(
            j, volume, page)

        return url

    def get_doi(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
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
        }, headers={'User-Agent': 'tmp'})

        if len(response.content) < 50:
            raise ArticleNotFound()

        links = BeautifulSoup(response.content, 'lxml').select('.text--small a')

        if len(links) == 0:
            raise ProviderError('article not found, did you put the first page?')
        elif len(links) > 1:
            raise ProviderError('More than one result?!')

        return links[0].attrs['href'][16:]


class ScienceDirect(Provider):
    """Science Direct (Elsevier).

    Getting the DOI requires a valid API key (Get one at https://dev.elsevier.com/index.html).
    """

    NAME = 'ScienceDirect'
    CODE = 'sd'
    API_KEY_KWARG = 'true'
    WEBSITE_URL = 'https://www.sciencedirect.com/'
    ICON_URL = 'https://sdfestaticassets-eu-west-1.sciencedirectassets.com/shared-assets/18/images/favSD.ico'

    JOURNALS = {
        'Chemical Physics': IntMap((271366, N0))
    }

    api_url = 'https://api.elsevier.com/content/search/sciencedirect'
    base_url = WEBSITE_URL + 'search/advanced'

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        if journal not in self.JOURNALS:
            raise IncorrectJournalName()

        try:
            j = self.JOURNALS[journal][int(volume)]
        except KeyError:
            raise IncorrectVolume()
        except ValueError:
            raise ProviderError('volume is not an integer')

        return self.base_url + '?cid={}&volume={}&page={}'.format(j, volume, page)

    def _api_call(self, journal: str, volume: [str, int], page: str, **kwargs) -> dict:
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

    def get_doi(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
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

    JOURNALS = {
        'Theoretical Chemistry Accounts': IntMap((214, N0)),
        'Theoretica chimica acta': IntMap((214, N0)),
    }

    base_url = WEBSITE_URL + 'journal/'

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        """TOC of the volume, find your way into that ;)
        """

        if journal not in self.JOURNALS:
            raise IncorrectJournalName()

        try:
            j = self.JOURNALS[journal][int(volume)]
        except KeyError:
            raise IncorrectVolume()
        except ValueError:
            raise ProviderError('volume is not an integer')

        return self.base_url + '/{}/volume/{}/toc'.format(j, volume)


class Wiley(Provider):
    """Wiley.

    Perform the request on their search page API, since there is no other correct API available.
    Sorry about that, open to any suggestion.
    """

    NAME = 'Wiley'
    CODE = 'wiley'
    WEBSITE_URL = 'https://onlinelibrary.wiley.com/'

    JOURNALS = {
        'Chemistry - A European Journal': IntMap((15213765, N0))
    }

    api_url = WEBSITE_URL + 'action/quickLink'

    def get_url(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        """Require a single request to get the url (which contains the DOI)
        """
        if journal not in self.JOURNALS:
            raise IncorrectJournalName()

        try:
            j = self.JOURNALS[journal][int(volume)]
        except KeyError:
            raise IncorrectVolume()
        except ValueError:
            raise ProviderError('volume is not an integer')

        url = self.api_url + '?quickLinkJournal={j}&quickLinkVolume={v}&quickLinkPage={p}&quickLink=true'.format(
            j=j, v=volume, p=page)

        result = requests.get(url)
        if result.status_code != 200:
            raise ProviderError('error while requesting search')

        j = result.json()
        if 'link' not in j:
            raise ArticleNotFound()

        return self.WEBSITE_URL + j['link'][1:]

    def get_doi(self, journal: str, volume: [str, int], page: str, **kwargs: dict) -> str:
        result_url = self.get_url(journal, volume, page)
        p = result_url.find('abs/')
        if p == -1:
            raise ProviderError('cannot find DOI')

        return result_url[p + 4:]
