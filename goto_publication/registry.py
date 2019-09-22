from typing import List, Callable
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

    def _get_result(self,
                    callback: Callable[[jrnl.Journal, str, str, dict], dict],
                    journal: str,
                    volume: str,
                    page: str,
                    **kwargs: dict) -> dict:

        if len(journal) == 0:
            raise RegistryError('journal_identifier', 'Journal cannot be empty')

        if journal not in self.journals:
            raise RegistryError('journal_identifier', 'Unknown journal_identifier "{}"'.format(journal))

        if len(volume) == 0:
            raise RegistryError('volume', 'Volume cannot be empty')

        journal_obj = self.journals[journal]
        provider_name = journal_obj.provider.NAME
        response = journal_obj.provider.get_info()

        try:
            response.update(callback(journal_obj, volume, page, **kwargs))
        except jrnl.JournalError as e:
            raise RegistryError('journal', str(e))
        except providers.ProviderError as e:
            raise RegistryError('journal', '{}: {}'.format(provider_name, str(e)))
        except NotImplementedError:
            raise RegistryError('journal', '{}: {}'.format(provider_name, 'not yet implemented'))

        return response

    def get_url(self, journal: str, volume: str, page: str, **kwargs: dict) -> dict:
        """Get the URL
        """

        def cb_url(j, v, pg, **kw):
            url = j.get_url(v, pg, **kw)
            return {'url': url}

        return self._get_result(cb_url, journal, volume, page, **kwargs)

    def get_doi(self, journal: str, volume: str, page: str, **kwargs: dict) -> dict:
        """Get the DOI
        """

        def cb_doi(j, v, pg, **kw):
            doi = j.get_doi(v, pg, **kw)
            return {'doi': doi, 'url': 'https://dx.doi.org/' + doi}

        return self._get_result(cb_doi, journal, volume, page, **kwargs)
