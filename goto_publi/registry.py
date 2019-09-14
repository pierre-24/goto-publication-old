from typing import List
import distance

from goto_publi import providers


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

        self.providers[provider.PROVIDER_CODE] = provider
        for j in provider.JOURNALS:
            self.journals[j] = provider.PROVIDER_CODE

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

    def _get_provider(self, journal: str) -> providers.Provider:
        if len(journal) == 0:
            raise RegistryError('journal', 'Journal cannot be empty')

        if journal not in self.journals:
            raise RegistryError('journal', 'Unknown journal "{}"'.format(journal))

        return self.providers[self.journals[journal]]

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        if len(volume) == 0:
            raise RegistryError('volume', 'Volume cannot be empty')

        try:
            return self._get_provider(journal).get_url(journal, volume, page, **kwargs)
        except providers.ProviderError as e:
            raise RegistryError('journal', '{}: {}'.format(
                self.providers[self.journals[journal]].PROVIDER_NAME,
                str(e)))

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> str:
        if len(volume) == 0:
            raise RegistryError('volume', 'Volume cannot be empty')

        try:
            return self._get_provider(journal).get_doi(journal, volume, page, **kwargs)
        except providers.ProviderError as e:
            raise RegistryError('journal', '{}: {}'.format(
                self.providers[self.journals[journal]].PROVIDER_NAME,
                str(e)))
