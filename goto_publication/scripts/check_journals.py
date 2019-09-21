"""
Find missing journals in provider
"""

import sys

from goto_publication import providers

PROVIDERS = [  # will be replaced by REGISTER later on
    # providers.ACS(),
    providers.APS()
    # providers.AIP()
]

if __name__ == '__main__':
    total_missing = 0

    for p in PROVIDERS:
        print('- Checking {} ...'.format(p.NAME))

        for j in p.get_journals():
            journal_name = j
            if type(j) is tuple:
                journal_name = j[0]
            if journal_name not in p.JOURNALS:
                print('  - missing {}'.format(j if type(j) is tuple else '\'{}\''.format(j)))
                total_missing += 1

    print('\nTotal missing: {}'.format(total_missing))

    if total_missing > 0:
        sys.exit(-1)
