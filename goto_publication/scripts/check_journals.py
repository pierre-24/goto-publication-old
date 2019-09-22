"""
Find missing journals in provider
"""

import sys

from goto_publication import providers

PROVIDERS = [  # will be replaced by REGISTER later on
    providers.ACS(),
    providers.APS(),
    providers.AIP(),
    # providers.IOP()
]

if __name__ == '__main__':
    total_missing = 0

    for p in PROVIDERS:
        print('- Checking {} ...'.format(p.NAME))
        missing = {}

        journals = p.get_journals()

        for j in journals:
            if j not in p.JOURNALS:
                missing.update({j: journals[j]})
                total_missing += 1

        print(' ', repr(missing))

    print('\nTotal missing: {}'.format(total_missing))

    if total_missing > 0:
        sys.exit(-1)
