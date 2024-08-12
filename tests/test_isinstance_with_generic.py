from typing import List, Set, Tuple, Union

from entob.util import isinstance_with_generic


def test_isinstance_with_generic():
    types = (
        Union[Tuple[int, int], Set[int], List[int]],
        Union[Tuple[str, str], Set[str], List[str]],
    )

    # list
    assert isinstance_with_generic([], types)
    assert isinstance_with_generic([1, 2], types)
    assert isinstance_with_generic([1, 2, 3], types)
    assert isinstance_with_generic([1, 2, 3, 4, 5], types)
    assert isinstance_with_generic(["1"], types)
    assert isinstance_with_generic(["1", "2", "3", "4"], types)

    assert not isinstance_with_generic([1, 2, 3, 4, None], types)
    assert not isinstance_with_generic([(1, 2), {1, 2}], types)
    assert not isinstance_with_generic([(1, 2), (1, 2)], types)
    assert not isinstance_with_generic([1, 2, 3, 4, "5"], types)
    assert not isinstance_with_generic([1, 2, 3, 4, 5.0], types)
    assert not isinstance_with_generic([None], types)

    # set
    assert isinstance_with_generic({1}, types)
    assert isinstance_with_generic({1, 2}, types)
    assert isinstance_with_generic({1, 2, 3}, types)
    assert isinstance_with_generic({1, 2, 3, 4, 5}, types)
    assert isinstance_with_generic({"1"}, types)
    assert isinstance_with_generic({"1", "2"}, types)
    assert isinstance_with_generic(set(), types)

    assert not isinstance_with_generic({1, 2, None}, types)
    assert not isinstance_with_generic({(1, 2), (1, 2)}, types)
    assert not isinstance_with_generic({1, 2, "3"}, types)
    assert not isinstance_with_generic({1, 2, 3.0}, types)
    assert not isinstance_with_generic({None}, types)

    # tuple
    assert isinstance_with_generic((1, 2), types)
    assert isinstance_with_generic(("1", "2"), types)

    assert not isinstance_with_generic((1,), types)
    assert not isinstance_with_generic(("1",), types)
    assert not isinstance_with_generic((1, None), types)
    assert not isinstance_with_generic((1, 3.0), types)
    assert not isinstance_with_generic((1, 2, 3, 4, 5), types)
    assert not isinstance_with_generic(("1", None), types)
    assert not isinstance_with_generic(("1", 3.0), types)
    assert not isinstance_with_generic(("1", "2", "3"), types)
    assert not isinstance_with_generic(tuple(), types)
    assert not isinstance_with_generic((None,), types)

    assert not isinstance_with_generic(None, types)
    assert not isinstance_with_generic(1, types)
    assert not isinstance_with_generic("1", types)
    assert not isinstance_with_generic(1.0, types)
    assert not isinstance_with_generic(True, types)
    assert not isinstance_with_generic(False, types)
    assert not isinstance_with_generic(([], []), types)

    assert isinstance_with_generic(1, (int, str))
    assert isinstance_with_generic("1", (int, str))
    assert isinstance_with_generic(True, (int, str))
    assert isinstance_with_generic(False, (int, str))
    assert isinstance_with_generic(1.0, float)
    assert not isinstance_with_generic(None, (int, str))
    assert not isinstance_with_generic(1.0, (int, str))
    assert not isinstance_with_generic(([], []), (int, str))
