from goto_publication import providers, __program_name__ as pname, __version__ as pversion, __author__ as pauthor

APP_CONFIG = {
    # Flask secret key: generate a new one with
    # `python -c "import random; print(repr(''.join([chr(random.randrange(32, 126)) for _ in range(24)])))"`
    'SECRET_KEY': ';+b&#Yl] U$y7dzmW&IRh$GO',

    # Limit API usage (see https://flask-limiter.readthedocs.io/en/stable/#rate-limit-string-notation):
    # 'API_RATE_LIMITER_LIST': '3/second',
    # 'API_RATE_LIMITER_SUGGESTS': '2/second',
    # 'API_RATE_LIMITER_GET': '1/second',
    # 'RATELIMIT_HEADERS_ENABLED': True,
    # You can also set global limits (see https://flask-limiter.readthedocs.io/en/stable/#configuration)
}

API_CONFIG = {
    'DEFAULT_COUNT': 25,
    'MAX_COUNT': 100,
    'DEFAULT_CUTOFF': 0.6,
    'DEFAULT_NUM_SUGGESTIONS': 15,
}

WEBPAGE_INFO = {
    'repo_url': 'https://github.com/pierre-24/goto-publication/',
    'prog_name': pname,
    'prog_version': pversion,
    'author_url': 'https://pierrebeaujean.net',
    'author_name': pauthor,
    'subtitle': 'Citation-based URL/DOI searches and redirections for chemistry and physics',
    'site_description': 'Citation-based URL/DOI searches and redirections for chemistry and physics'
}

REGISTRY_PATH = 'journals_register.yml'

PROVIDERS = [  # please keep this alphabetic
    providers.ACS(),
    providers.APS(),
    providers.AIP(),
    providers.IOP(),
    providers.Nature(),
    providers.RSC(),
    providers.ScienceDirect(concepts=['CHEM', 'PHYS']),
    providers.Springer(concepts=['Chemistry', 'Physics']),
    providers.Wiley(concepts=[93, 43]),
]

# Load the production settings, overwrite the existing ones if needed
try:
    from settings_prod import *  # noqa
except ImportError:
    pass
