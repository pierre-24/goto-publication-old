import unittest
import itertools

from goto_publication import int_map


class TestIntMap(unittest.TestCase):
    """Check if IntMap is correct"""

    def test_infinity(self):
        self.assertTrue(int_map.Inf == int_map.Inf)
        self.assertTrue(int_map.mInf == int_map.mInf)
        self.assertTrue(int_map.Inf != int_map.mInf)
        self.assertTrue(1 != int_map.mInf)

        self.assertTrue(1 < int_map.Inf)
        self.assertTrue(1 > int_map.mInf)
        self.assertTrue(int_map.mInf < int_map.Inf)

    def test_subset(self):
        # check is_in
        p_mInf_Inf = int_map.S()
        self.assertTrue(all(p_mInf_Inf.is_in(i) for i in range(0, 5)))

        p_2_Inf = int_map.S(begin=2)
        self.assertTrue(all(p_2_Inf.is_in(i) for i in range(2, 5)))
        self.assertFalse(any(p_2_Inf.is_in(i) for i in range(0, 1)))

        p_mInf_2 = int_map.S(end=2)
        self.assertTrue(all(p_mInf_2.is_in(i) for i in range(0, 2)))
        self.assertFalse(any(p_mInf_2.is_in(i) for i in range(3, 5)))

        p_4_5 = int_map.S(4, 5)
        self.assertTrue(all(p_4_5.is_in(i) for i in [4, 5]))
        self.assertFalse(any(p_4_5.is_in(i) for i in [0, 1, 2, 3, 6]))

        p_1_3 = int_map.S(1, 3)
        p_0_1 = int_map.S(0, 1)
        p_0_2 = int_map.S(0, 2)
        p_0_6 = int_map.S(0, 6)

        # check overlap
        overlap_matrix = [
            [p_mInf_Inf, [
                (p_mInf_Inf, True), (p_mInf_2, True), (p_2_Inf, True), (p_1_3, True), (p_4_5, True), (p_0_1, True),
                (p_0_6, True), (p_0_2, True)]],
            [p_mInf_2, [
                (p_mInf_2, True), (p_2_Inf, True), (p_1_3, True), (p_4_5, False), (p_0_1, True), (p_0_6, True),
                (p_0_2, True)]],
            [p_2_Inf, [
                (p_2_Inf, True), (p_1_3, True), (p_4_5, True), (p_0_1, False), (p_0_6, True), (p_0_2, True)]],
            [p_1_3, [
                (p_1_3, True), (p_4_5, False), (p_0_1, True), (p_0_6, True), (p_0_2, True)]]
        ]

        for p1, li in overlap_matrix:
            for p2, expected_result in li:
                self.assertEqual(
                    expected_result, p1.overlap(p2), msg='<{},{}>!={}'.format(p1, p2, expected_result))
                self.assertEqual(
                    expected_result, p2.overlap(p1), msg='<{},{}>!={}'.format(p2, p1, expected_result))

    def test_int_map(self):
        S = int_map.S

        # check init
        v1 = 'tmp1'
        imap = int_map.IntMap(v1)
        self.assertEqual(len(imap.subsets), 1)
        self.assertEqual(imap.subsets[0], (v1, S()))

        p1 = int_map.S(2, 3)
        imap = int_map.IntMap((v1, p1))
        self.assertEqual(len(imap.subsets), 1)
        self.assertEqual(imap.subsets[0], (v1, p1))

        p0 = S(0, 1)
        v0 = 'tmp0'
        v2 = 'tmp2'
        p2 = S(5, 6)

        correct_order = [(v0, p0), (v1, p1), (v2, p2)]
        for i in itertools.permutations(correct_order):
            imap = int_map.IntMap(list(i))
            self.assertEqual(imap.subsets, correct_order)

        # check set
        def _check(max_, ranges_):
            lst = [None] * max_
            imap_ = int_map.IntMap()

            for r in ranges_:  # create list
                imap_[r[1]:r[2]] = r[0]
                for i in range(r[1], r[2] + 1):
                    lst[i] = r[0]

            for i in range(max_):  # check list are the same
                e = lst[i]
                if e is None:
                    with self.assertRaises(KeyError):
                        _ = imap_[i]
                else:
                    self.assertEqual(e, imap_[i])

            return imap_

        v3 = 'tmp3'
        _check(10, [(v0, 0, 1), (v1, 2, 4), (v2, 5, 7), (v3, 3, 6)])
        _check(10, [(v0, 0, 1), (v1, 2, 4), (v2, 5, 7), (v3, 2, 4)])
        _check(10, [(v0, 0, 1), (v1, 2, 4), (v2, 5, 7), (v3, 2, 8)])

        # check access
        imap = int_map.IntMap()
        imap[:5] = v0
        imap[7:9] = v1
        imap[11:] = v2

        self.assertEqual(imap[-1], v0)
        self.assertEqual(imap[2], v0)
        self.assertEqual(imap[7], v1)
        self.assertEqual(imap[12], v2)

        with self.assertRaises(KeyError):  # access a hole
            _ = imap[6]

        with self.assertRaises(KeyError):
            _ = imap[10]

        # test serialization (as a list)
        li = imap.serialize()
        imap2 = int_map.IntMap.deserialize(li)

        self.assertEqual(imap2.serialize(), li)
        self.assertEqual(imap2.subsets, imap.subsets)
