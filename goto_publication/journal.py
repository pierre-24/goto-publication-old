from typing import Any, Dict

from goto_publication import providers
import iso4


class JournalError(Exception):
    def __init__(self, j, v, *args):
        super().__init__('{} ({})'.format(v, j), *args)


class AccessError(JournalError):
    def __init__(self, p, j, v):
        super().__init__(j + ' [' + p + ']', v)


class Journal:
    """Define a journal_identifier, containing different articles, which have an URL and a DOI (if valid).
    """

    def __init__(self, name: str, identifier: Any, provider: 'providers.Provider', abbr: str = None):
        self.name = name
        self.identifier = identifier
        self.abbr = abbr

        if self.abbr is None:
            self.abbr = iso4.abbreviate(self.name, periods=False, disambiguation_langs=set('en'))

        self.provider = provider

    def serialize(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'identifier': self.identifier,
            'provider': self.provider.CODE,
            'abbr': self.abbr
        }

    @classmethod
    def deserialize(cls, d: Dict[str, Any], provider: 'providers.Provider'):
        return cls(d.get('name'), d.get('identifier'), provider, d.get('abbr', None))

    def get_url(self, volume: [int, str], page: [int, str], **kwargs: dict) -> str:
        """Get the corresponding url"""

        try:
            return self.provider.get_url(self.identifier, volume, page, **kwargs)
        except providers.ProviderError as e:
            raise AccessError(self.provider.CODE, self.name, str(e))
        except NotImplementedError:
            raise AccessError(self.provider.CODE, self.name, 'Not yet implemented')

    def get_doi(self, volume: [int, str], page: [int, str], **kwargs: dict) -> str:
        """Get the corresponding DOI"""

        try:
            return self.provider.get_doi(self.identifier, volume, page, **kwargs)
        except providers.ProviderError as e:
            raise AccessError(self.provider.CODE, self.name, str(e))
        except NotImplementedError:
            raise AccessError(self.provider.CODE, self.name, 'Not yet implemented')
