"""Tests for TriangGroup reset behavior."""
from grand_match import TriangGroup
from tests.conftest import make_triang


def test_reset_clears_all_state():
    """After reset, all group tracking state should be cleared."""
    group = TriangGroup()
    group.kit_Number = "kit-old"
    group.chr = "1"
    group.triang_list.append(make_triang(1, "kit-x", "kit-y", 100, 200))
    group.siblingKitCountGroup["kit-y"] = 1
    group.groupContainsExcludedCousin = True

    group.reset("kit-new", "2")

    assert group.triang_list == []
    assert group.siblingKitCountGroup == {}
    assert group.groupContainsExcludedCousin is False


def test_reset_sets_new_identifiers():
    """Reset should update kit_Number and chr to new values."""
    group = TriangGroup()
    group.reset("kit-new", "5")

    assert group.kit_Number == "kit-new"
    assert group.chr == "5"
