"""
Find missing journals in provider
"""

import yaml
from datetime import datetime

from goto_publication import providers

from settings import REGISTER_PATH

PROVIDERS = [  # will be replaced by REGISTER later on
    providers.ACS(),
    providers.APS(),
    providers.AIP(),
    # providers.IOP()
]

if __name__ == '__main__':
    journals = []

    for p in PROVIDERS:
        print('- Getting journals from {}'.format(p.NAME), end='')
        j = p.get_journals()
        journals.extend(i.serialize() for i in j)
        print(' ({})'.format(len(j)))

    print('\nTotal: {}'.format(len(journals)))

    with open('../' + REGISTER_PATH, 'w') as f:
        f.write('# generated on {}\n'.format(datetime.now()))
        yaml.dump(journals, f, Dumper=yaml.Dumper)
