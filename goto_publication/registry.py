from typing import List
import yaml

from goto_publication import providers, journal as jrnl


class RegistryError(Exception):
    def __init__(self, var, err, *args):
        self.var = var
        self.what = err
        super().__init__(var + ':' + err, *args)


class Registry:
    """Store all providers and perform actions
    """

    def __init__(self, registry_path: str, providers_: List[providers.Provider]):
        # register the providers
        self.providers = {}
        self.registers(providers_)

        # get journals
        self.registry_path = registry_path

        with open(self.registry_path) as f:
            journals_base = yaml.load(f, Loader=yaml.Loader)

        self.journals = {}
        for j in journals_base:
            try:
                self.journals[j['name']] = jrnl.Journal.deserialize(j, self.providers[j['provider']])
            except KeyError:
                pass

    def register(self, provider: providers.Provider):
        """Register a provider

        :param provider: provider
        """

        self.providers[provider.CODE] = provider

    def registers(self, providers_: List[providers.Provider]):
        for p in providers_:
            self.register(p)

    def suggest_journals(self, q: str) -> list:
        """Suggest journal_identifier names based on search string

        :param q: search string
        """

        distances = [(i, j.close_to(q)) for i, j in self.journals.items()]
        distances.sort(key=lambda k: k[1])

        return list(e[0] for e in distances[:5])

    def _check_input(self, journal: str, volume: str, page: str, **kwargs: dict) -> None:
        """Check input correctness, raise ``RegistryError`` if not.
        """

        if len(journal) == 0:
            raise RegistryError('journal', 'Journal cannot be empty')

        if journal not in self.journals:
            raise RegistryError('journal', 'Unknown journal "{}"'.format(journal))

        if len(volume) == 0:
            raise RegistryError('volume', 'Volume cannot be empty')

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> dict:
        """Get the URL
        """

        self._check_input(journal, volume, page, **kwargs)

        journal_obj = self.journals[journal]
        response = journal_obj.provider.get_info()

        try:
            response.update({'url': journal_obj.get_url(volume, page, **kwargs)})
        except jrnl.JournalError as e:
            raise RegistryError('journal', str(e))

        return response

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> dict:
        """Get the DOI
        """

        self._check_input(journal, volume, page, **kwargs)

        journal_obj = self.journals[journal]
        response = journal_obj.provider.get_info()

        try:
            doi = journal_obj.get_doi(volume, page, **kwargs)
            response.update({'doi': doi, 'url': 'https://dx.doi.org/' + doi})
        except jrnl.JournalError as e:
            raise RegistryError('journal', str(e))

        return response
