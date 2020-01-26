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

# restrict to chemistry and physics for Wiley, Springer and ScienceDirect (Elsevier)
for p in PROVIDERS:
    if p.CODE == 'wiley':
        p.CONCEPT_IDS = [93, 43]  # use numeric IDs
    if p.CODE == 'sl':
        p.DISCIPLINES = ['Chemistry', 'Physics']
    if p.CODE == 'sd':
        p.SUBJECTS = ['CHEM', 'PHYS']

# Load the production settings, overwrite the existing ones if needed
try:
    from settings_prod import *  # noqa
except ImportError:
    pass
