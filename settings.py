from goto_publication import providers

REGISTRY_PATH = 'journals_register.yml'

PROVIDERS = [  # please keep this alphabetic
    providers.ACS(),
    providers.APS(),
    providers.AIP(),
    providers.IOP(),
    providers.Nature(),
    providers.RSC(),
    providers.ScienceDirect(),
    providers.Springer(),
    providers.Wiley(),
]

# Load the production settings, overwrite the existing ones if needed
try:
    from settings_prod import *  # noqa
except ImportError:
    pass
