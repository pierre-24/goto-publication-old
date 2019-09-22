from typing import Any, Dict

from goto_publication import int_map, providers
import distance


class JournalError(Exception):
    def __init__(self, j, v, *args):
        super().__init__('{}: {}'.format(j, v), *args)


class InvalidVolume(JournalError):
    def __init__(self, j):
        super().__init__(j, 'invalid volume')


class Journal:
    """Define a journal_identifier, containing different articles, which have an URL and a DOI (if valid).
    """

    def __init__(self, name: str, identifier: [int_map.IntMap, Any], provider: 'providers.Provider', abbr: str = None):
        self.name = name

        if type(identifier) is int_map.IntMap:
            self.identifier = identifier
        else:
            self.identifier = int_map.IntMap((identifier, int_map.N0))

        self.abbr = abbr

        self.search_terms = [self.name.lower()]
        if self.abbr is not None:
            self.search_terms.append(self.abbr.lower())

        self.provider = provider

    def serialize(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'identifier': self.identifier.serialize(),
            'provider': self.provider.CODE,
            'abbr': self.abbr
        }

    @classmethod
    def deserialize(cls, d: Dict[str, Any], provider: 'providers.Provider'):
        return cls(d.get('name'), int_map.IntMap.deserialize(d.get('identifier', [])), provider, d.get('abbr', None))

    def close_to(self, search_term) -> float:
        """Return a float between 0 and 1 indicating wetter the journal_identifier looks like the search term
        """

        return max(distance.levenshtein(i, search_term, normalized=True) for i in self.search_terms)

    def get_journal_identifiers(self, volume: [int, str]) -> Any:
        """Get the correct journal_identifier identifier(s) corresponding to the given volume (which is casted as an int)
        """

        try:
            return self.identifier[int(volume)]
        except (KeyError, ValueError):
            raise InvalidVolume(volume)

    def get_url(self, volume: [int, str], page: [int, str], **kwargs: dict) -> str:
        """Get the corresponding url"""

        return self.provider.get_url(self.get_journal_identifiers(volume), volume, page, **kwargs)

    def get_doi(self, volume: [int, str], page: [int, str], **kwargs: dict) -> str:
        """Get the corresponding DOI"""

        return self.provider.get_doi(self.get_journal_identifiers(volume), volume, page, **kwargs)
