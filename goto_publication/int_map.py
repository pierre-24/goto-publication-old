from typing import Union, Any, List, Tuple


class C:
    def __init__(self, sgn: int):
        if sgn == 0:
            raise ValueError(sgn)

        self.sgn = 1 if sgn > 0 else -1

    def __str__(self):
        return '{}Inf'.format('-' if self.sgn < 0 else '')

    def __repr__(self):
        return 'C({})'.format(self.sgn)

    def __eq__(self, other: [int, 'C']):
        if type(other) != C:
            return False
        return self.sgn == other.sgn

    def __lt__(self, other: [int, 'C']):
        if type(other) is int:
            return self.sgn < 0
        elif type(other) is C:
            return self.sgn < other.sgn

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)


Inf = C(1)
mInf = C(-1)


class S:
    """Define a subset of the integers, with a beginning and a end.
    """

    def __init__(self, begin: Union[int, C] = mInf, end: Union[int, C] = Inf):
        if begin == Inf:
            if end == Inf:
                raise ValueError('two Inf')
            else:
                begin, end = end, begin
        elif end == mInf:
            if begin == mInf:
                raise ValueError('two mInf')
            else:
                begin, end = end, begin
        elif begin is not mInf and end is not Inf and end < begin:
            begin, end = end, begin

        self.begin = begin
        self.end = end

    def __repr__(self):
        return 'S({},{})'.format(repr(self.begin), repr(self.end))

    def __str__(self) -> str:
        return '[{};{}]'.format(self.begin, self.end)

    def __eq__(self, other: Any) -> bool:
        if type(other) is not S:
            return False
        return self.begin == other.begin and self.end == other.end

    @classmethod
    def from_slice(cls, slc: slice):
        if slc.step is not None:
            raise ValueError('step is not allowed')

        return cls(mInf if slc.start is None else slc.start, Inf if slc.stop is None else slc.stop)

    def is_before(self, v: [int, C]) -> bool:
        """Check if ``v`` is located before the subset (if ``c < self.begin``)"""
        return v < self.begin

    def is_after(self, v: [int, C]) -> bool:
        """Check if ``v`` is located after the subset (if ``c > self.end``)"""
        return v > self.end

    def is_in(self, v: [int, C]) -> bool:
        return not (self.is_before(v) or self.is_after(v))

    def distinct(self, v: 'S') -> bool:
        """Check if the two subset are distinct (no common values)"""
        li = [v.begin, v.end]
        return all(self.is_before(i) for i in li) or all(self.is_after(i) for i in li)

    def overlap(self, v: 'S') -> bool:
        """Check if the two subset overlap"""
        return not self.distinct(v)

    def contains(self, v: 'S') -> bool:
        """Check if ``v`` is totally contained in ``self``"""
        return self.is_in(v.begin) and self.is_in(v.end)


class IntMap:
    """Map between the integers and some values
    """

    def __init__(self, values: Union[List[Tuple[Any, S]], Tuple[Any, S], Any, None] = None):
        self.subsets = []

        if values is not None:
            if type(values) is tuple:
                if len(values) != 2:
                    raise ValueError('range should be composed of 2 values')
                self._set(*values)
            elif type(values) is list:
                self.subsets = []
                for v in values:
                    if type(v) is not tuple:
                        raise TypeError(v)
                    if len(v) != 2:
                        raise ValueError('ranges should be composed of 2 values')
                    self._set(*v)
            else:
                self._set(values)

    def _set(self, value: Any, subset: S = S()) -> None:
        """Set a value for a given subset of indices.

        :param value: value
        :param subset: subset of indices
        """

        if type(subset) is not S:
            raise TypeError(subset)

        if len(self.subsets) == 0:
            self.subsets.append((value, subset))
        else:
            is_before = []
            overlap_with = []
            is_after = []

            for i, p in enumerate(self.subsets):  # distribute subset
                if subset.is_before(p[1].end):
                    is_before.append(i)
                elif subset.is_after(p[1].begin):
                    is_after = list(range(i, len(self.subsets)))
                    break
                elif subset.overlap(p[1]):
                    overlap_with.append(i)
                else:
                    raise Exception('should not happen')

            # deal with overlap
            resulting = [(value, subset)]
            for i in overlap_with:
                other_val, other_sub = self.subsets[i]

                if subset.contains(other_sub):  # you're out
                    pass
                elif other_sub.contains(subset):  # split the subset in two part
                    resulting.insert(0, (other_val, S(other_sub.begin, subset.begin - 1)))
                    resulting.append((other_val, S(subset.end + 1, other_sub.end)))
                else:
                    if subset.is_before(other_sub.begin):
                        resulting.insert(0, (other_val, S(other_sub.begin, subset.begin - 1)))
                    else:
                        resulting.append((other_val, S(subset.end + 1, other_sub.end)))

            after = list(self.subsets[i] for i in is_after)
            self.subsets = list(self.subsets[i] for i in is_before)
            self.subsets.extend(resulting)
            self.subsets.extend(after)

    def __setitem__(self, key: [int, S, C, slice], value: Any):
        if type(key) is int or type(key) is C:  # single value
            self._set(value, S(key, key))
        elif type(key) is slice:
            self._set(value, S.from_slice(key))
        elif type(key) is S:
            self._set(value, key)
        else:
            raise TypeError(key)

    def __getitem__(self, item: [int, C]) -> Any:
        if type(item) not in [int, C]:
            raise TypeError(item)

        for subset in self.subsets:
            if subset[1].is_in(item):
                return subset[0]
            elif subset[1].is_before(item):
                break

        raise KeyError(item)
