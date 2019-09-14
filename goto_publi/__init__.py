"""
goto-publi: citation-based redirection
"""

__version__ = '0.1'
__author__ = 'Pierre Beaujean'
__maintainer__ = 'Pierre Beaujean'
__email__ = 'pierre.beaujean@unamur.be'
__status__ = 'Development'

from goto_publi import registry, providers

REGISTRY = registry.Registry()
REGISTRY.registers([  # please keep this alphabetic
    providers.ACS(),
    providers.AIP(),
    providers.Nature(),
    providers.RSC(),
    providers.ScienceDirect(),
    providers.Springer(),
    providers.Wiley(),
])
