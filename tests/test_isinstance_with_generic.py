from typing import List, Set, Tuple, Union

from mageclass import _isinstance_with_generic


def test_isinstance_with_generic():
    types = (
        Union[Tuple[int, int], Set[int], List[int]],
        Union[Tuple[str, str], Set[str], List[str]],
    )

    # list
    assert _isinstance_with_generic([], types)
    assert _isinstance_with_generic([1, 2], types)
    assert _isinstance_with_generic([1, 2, 3], types)
    assert _isinstance_with_generic([1, 2, 3, 4, 5], types)
    assert _isinstance_with_generic(["1"], types)
    assert _isinstance_with_generic(["1", "2", "3", "4"], types)

    assert not _isinstance_with_generic([1, 2, 3, 4, None], types)
    assert not _isinstance_with_generic([1, 2, 3, 4, "5"], types)
    assert not _isinstance_with_generic([1, 2, 3, 4, 5.0], types)
    assert not _isinstance_with_generic([None], types)

    # set
    assert _isinstance_with_generic({1}, types)
    assert _isinstance_with_generic({1, 2}, types)
    assert _isinstance_with_generic({1, 2, 3}, types)
    assert _isinstance_with_generic({1, 2, 3, 4, 5}, types)
    assert _isinstance_with_generic({"1"}, types)
    assert _isinstance_with_generic({"1", "2"}, types)
    assert _isinstance_with_generic(set(), types)

    assert not _isinstance_with_generic({1, 2, None}, types)
    assert not _isinstance_with_generic({1, 2, "3"}, types)
    assert not _isinstance_with_generic({1, 2, 3.0}, types)
    assert not _isinstance_with_generic({None}, types)

    # tuple
    assert _isinstance_with_generic((1, 2), types)
    assert _isinstance_with_generic(("1", "2"), types)

    assert not _isinstance_with_generic((1,), types)
    assert not _isinstance_with_generic(("1",), types)
    assert not _isinstance_with_generic((1, None), types)
    assert not _isinstance_with_generic((1, 3.0), types)
    assert not _isinstance_with_generic((1, 2, 3, 4, 5), types)
    assert not _isinstance_with_generic(("1", None), types)
    assert not _isinstance_with_generic(("1", 3.0), types)
    assert not _isinstance_with_generic(("1", "2", "3"), types)
    assert not _isinstance_with_generic(tuple(), types)
    assert not _isinstance_with_generic((None,), types)

    assert not _isinstance_with_generic(None, types)
    assert not _isinstance_with_generic(1, types)
    assert not _isinstance_with_generic("1", types)
    assert not _isinstance_with_generic(1.0, types)
    assert not _isinstance_with_generic(True, types)
    assert not _isinstance_with_generic(False, types)
    assert not _isinstance_with_generic(([], []), types)