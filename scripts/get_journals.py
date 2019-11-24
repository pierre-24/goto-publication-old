"""
Find missing journals in provider
"""

import yaml
from datetime import datetime

from settings import REGISTER_PATH, PROVIDERS

if __name__ == '__main__':
    # TODO: API key

    journals = []

    for p in PROVIDERS:
        print('- Getting journals from {}'.format(p.NAME), end='')
        try:
            j = p.get_journals()
            journals.extend(i.serialize() for i in j)
            print(' ({})'.format(len(j)))
        except NotImplementedError:
            print(' (skipped, `get_journals()` not implemented)')

    print('\nTotal: {}'.format(len(journals)))

    with open('../' + REGISTER_PATH, 'w') as f:
        f.write('# generated on {}\n'.format(datetime.now()))
        yaml.dump(journals, f, Dumper=yaml.Dumper)
