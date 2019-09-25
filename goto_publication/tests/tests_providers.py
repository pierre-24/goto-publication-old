import unittest
import requests
from typing import Tuple, Union, Any

from goto_publication import providers


class TestProviders(unittest.TestCase):
    """Check if resulting DOI is correct
    """

    def _check(self, p: providers.Provider, info: Tuple[Any, Union[str, int], Union[str, int]], **kwargs):
        """Check that DOI results in a 302 at https://dx.doi.org.

        NOTE: **DO NOT CHECK THE URL**!
        Otherwise, you will messed up the read count of the corresponding articles, which may result in troubles.
        """

        doi = p.get_doi(*info, **kwargs)
        result = requests.get('https://dx.doi.org/' + doi, allow_redirects=False)
        self.assertEqual(result.status_code, 302)

    # !! Please keep the list alphabetic
    def test_ACS(self):
        self._check(providers.ACS(), ('jacsat', 138, 5052))  # Beaujean et al.

    def test_APS(self):
        self._check(providers.APS(), (('prl', 'PhysRevLett'), 116, 231301))  # S. W. Hawking et al.

    def test_AIP(self):
        self._check(providers.AIP(), ('The Journal of Chemical Physics', 151, '064303'))  # Beaujean et al.

    def test_IOP(self):
        self._check(providers.IOP(), ('1751-8121', 52, 320201))  # G. Adresso et al.

    def test_Nature(self):
        self._check(providers.Nature(), ('nature', 227, 680))  # U.K. Laemmli et al. (second most cited)

    def test_RSC(self):
        self._check(providers.RSC(), ('phys. chem. chem. phys.', 21, 2222))  # M. Merced Montero-Campillo et al.

    def test_ScienceDirect(self):
        pass  # doi requires API key

    def test_Springer(self):
        pass  # no DOI for Springer

    def test_Wiley(self):
        self._check(providers.Wiley(), ('15213765', 15, 186))  # Pyyklö et al. (most cited)
