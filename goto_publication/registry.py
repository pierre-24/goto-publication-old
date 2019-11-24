from typing import List
import yaml
import difflib

from goto_publication import providers, journal as jrnl


class RegistryError(Exception):
    def __init__(self, var, err, *args):
        self.var = var
        self.what = err
        super().__init__(var + ':' + err, *args)


class Registry:
    """Store all providers and perform actions
    """

    NUM_SUGGESTIONS = 10

    def __init__(self, registry_path: str, providers_: List[providers.Provider]):
        # register the providers
        self.providers = {}
        self.registers(providers_)

        # get journals
        self.registry_path = registry_path

        with open(self.registry_path) as f:
            journals_base = yaml.load(f, Loader=yaml.Loader)

        self.journals = {}
        self._suggs_name = {}
        for j in journals_base:
            try:
                journal = jrnl.Journal.deserialize(j, self.providers[j['provider']])
                self.journals[j['name']] = journal
                self._suggs_name[journal.name.lower()] = journal
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

        lst = difflib.get_close_matches(q, self._suggs_name.keys(), n=self.NUM_SUGGESTIONS)
        return list(self._suggs_name[n].name for n in lst)

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
