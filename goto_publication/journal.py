from typing import Any, Callable

from goto_publication import int_map
import distance


class JournalError(Exception):
    pass


class InvalidVolume(JournalError):
    def __init__(self, v, *args):
        super().__init__('invalid volume {}'.format(v), *args)


class NotCallable(JournalError):
    def __init__(self, v, *args):
        super().__init__('cannot call {}'.format(v), *args)


class Journal:
    """Define a journal, containing different articles, which have an URL and a DOI (if valid).
    """

    def __init__(
            self, name: str,
            identifiers: [int_map.IntMap, Any],
            abbr: str = None,
            get_url: Callable[[str, str, str, dict], str] = None,
            get_doi: Callable[[str, str, str, dict], str] = None):

        self.name = name

        if type(identifiers) is int_map.IntMap:
            self.identifiers = identifiers
        else:
            self.identifiers = int_map.IntMap((identifiers, int_map.N0))

        self.abbr = abbr

        self._get_url = get_url
        self._get_doi = get_doi

    def close_to(self, search_term) -> float:
        """Return a float between 0 and 1 indicating wetter the journal looks like the search term
        """

        return max(
            distance.levenshtein(self.name, search_term, normalized=True),
            distance.levenshtein(self.abbr, search_term, normalized=True) if self.abbr is not None else .0
        )

    def get_journal_identifiers(self, volume: [int, str]) -> Any:
        """Get the correct journal identifier(s) corresponding to the given volume (which is casted as an int)
        """

        try:
            self.identifiers[int(volume)]
        except (KeyError, ValueError):
            raise InvalidVolume(volume)

    def get_url(self, volume: [int, str], page: [int, str]) -> str:
        """Get the corresponding url
        """

        if self._get_url:
            return self._get_url(self.get_journal_identifiers(volume), volume, page)
        else:
            raise NotCallable('get_url')

    def get_doi(self, volume: [int, str], page: [int, str]) -> str:
        """Get the corresponding DOI
        """
        if self._get_doi:
            return self._get_doi(self.get_journal_identifiers(volume), volume, page)
        else:
            raise NotCallable('get_doi')
