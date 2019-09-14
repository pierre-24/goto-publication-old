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
REGISTRY.registers([
    providers.ACS(),
    providers.AIP(),
    providers.Wiley(),
    providers.ScienceDirect()
])
