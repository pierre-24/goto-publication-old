from typing import List, Callable
import distance

from goto_publication import providers


class RegistryError(Exception):
    def __init__(self, var, err, *args):
        self.var = var
        self.what = err
        super().__init__(var + ':' + err, *args)


class Registry:
    """Store all providers and perform actions
    """

    def __init__(self):
        self.providers = {}
        self.journals = {}

    def register(self, provider: providers.Provider):
        """Register a provider

        :param provider: provider
        """

        self.providers[provider.CODE] = provider
        for j in provider.JOURNALS:
            self.journals[j] = provider.CODE

    def registers(self, providers_: List[providers.Provider]):
        for p in providers_:
            self.register(p)

    def suggest_journals(self, q: str) -> list:
        """Suggest journal names based on search string

        :param q: search string
        """

        distances = [(i, distance.levenshtein(i, q, normalized=True)) for i in self.journals.keys()]
        distances.sort(key=lambda k: k[1])

        return list(e[0] for e in distances[:5])

    def _get_result(self,
                    callback: Callable[[providers.Provider, str, str, str, dict], dict],
                    journal: str,
                    volume: str,
                    page: str,
                    **kwargs: dict) -> dict:

        if len(journal) == 0:
            raise RegistryError('journal', 'Journal cannot be empty')

        if journal not in self.journals:
            raise RegistryError('journal', 'Unknown journal "{}"'.format(journal))

        if len(volume) == 0:
            raise RegistryError('volume', 'Volume cannot be empty')

        provider = self.providers[self.journals[journal]]
        response = provider.get_info()

        try:
            response.update(callback(provider, journal, volume, page, **kwargs))
        except providers.ProviderError as e:
            raise RegistryError('journal', '{}: {}'.format(provider.NAME, str(e)))
        except NotImplementedError:
            raise RegistryError('journal', '{}: {}'.format(provider.NAME, 'not yet implemented'))

        return response

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> dict:
        """Get the URL
        """

        def cb_url(p, j, v, pg, **kw):
            url = p.get_url(j, v, pg, **kw)
            return {'url': url}

        return self._get_result(cb_url, journal, volume, page, **kwargs)

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> dict:
        """Get the DOI
        """

        def cb_doi(p, j, v, pg, **kw):
            doi = p.get_doi(j, v, pg, **kw)
            return {'doi': doi, 'url': 'https://dx.doi.org/' + doi}

        return self._get_result(cb_doi, journal, volume, page, **kwargs)
