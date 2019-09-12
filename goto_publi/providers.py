class ProviderError(Exception):
    pass


class Provider:
    PROVIDER_CODE = ''
    PROVIDER_NAME = ''
    JOURNALS = []

    def __init__(self):
        pass

    def get_url(self, journal: str, volume: str, page: str) -> str:
        raise NotImplementedError()


class AIP(Provider):
    """American Institute of Physics"""

    PROVIDER_NAME = 'American Institute of Physics (AIP)'
    PROVIDER_CODE = 'aip'

    JOURNALS = [
        'Journal of Applied Physics',
        'The Journal of Chemical Physics',
        'Journal of Mathematical Physics'
    ]

    base_url = 'https://aip.scitation.org/action/quickLink'

    def get_url(self, journal: str, volume: str, page: str) -> str:
        return self.base_url + '?quickLinkJournal={j}&quickLinkVolume={v}&quickLinkPage={p}&quickLink=true'.format(
            j=journal, v=volume, p=page)


class ACS(Provider):
    """American chemical society
    """

    PROVIDER_NAME = 'American Chemical Society'
    PROVIDER_CODE = 'acs'

    journal_codes = {
        'Journal of the American Chemical Society': 'jacsat'
    }

    JOURNALS = list(journal_codes.keys())

    base_url = 'https://pubs.acs.org/action/quickLink'

    def get_url(self, journal: str, volume: str, page: str) -> str:
        if journal not in self.journal_codes:
            raise ProviderError('not a valid name: {}'.format(journal))

        return self.base_url + '?quickLinkJournal={j}&quickLinkVolume={v}&quickLinkPage={p}&quickLink=true'.format(
            j=self.journal_codes[journal], v=volume, p=page)
