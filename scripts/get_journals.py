"""
Find missing journals in provider
"""

import shutil
import argparse

import yaml
from datetime import datetime

from settings import REGISTRY_PATH, PROVIDERS

from goto_publication import journal

registry_path = '../' + REGISTRY_PATH

if __name__ == '__main__':

    providers = {}
    for p in PROVIDERS:
        providers[p.CODE] = p

    # arguments parser
    parser = argparse.ArgumentParser(description='generate journal list')
    parser.add_argument('-b', '--backup', action='store_true', help='backup previous registry')
    parser.add_argument('-m', '--mix', action='store_true', help='update registry')
    parser.add_argument(
        '-O', '--only', action='store', help='Only update given providers in a comma separated list (implies `-m`)')

    args = parser.parse_args()

    # backup
    if args.backup:
        shutil.copy(registry_path, registry_path + '.bak')

    # prepare mixing
    prev_journals = {}

    if args.mix or args.only:
        with open(registry_path) as f:
            journals_base = yaml.load(f, Loader=yaml.Loader)
        for journals in journals_base:
            try:
                j_ = journal.Journal.deserialize(journals, providers[journals['provider']])
                prev_journals[journals['name']] = j_
            except KeyError:
                pass

    p_list = list(providers.keys())
    if args.only:
        p_list = args.only.split(',')

        for p in p_list:
            if p not in providers:
                raise Exception('provider {} unknown, must be in: {}'.format(p, ', '.join(providers.keys())))

    for p in PROVIDERS:
        if p.CODE in p_list:
            print('- Getting journals from {}'.format(p.NAME), end='')
            try:
                journals = p.get_journals()
                for j in journals:
                    prev_journals[j.name] = j
                print(' ({})'.format(len(journals)))
            except NotImplementedError:
                print(' (skipped, `get_journals()` not implemented)')

    print('\nTotal: {}'.format(len(prev_journals)))

    with open(registry_path, 'w') as f:
        f.write('# generated on {}\n'.format(datetime.now()))
        yaml.dump(list(i.serialize() for i in prev_journals.values()), f, Dumper=yaml.Dumper)
