"""Tests for OverlapCalculator.calculate_overlaps()"""
from grand_match import OverlapCalculator
from tests.conftest import make_segment


def test_two_overlapping_segments():
    """Two siblings share an overlapping region → one overlap covering the intersection."""
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 500),
        make_segment(1, "Bob", "kit-B", "Smith", 300, 700),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    # Should have overlaps covering the full range with varying sibling counts
    two_sibling_overlaps = [o for o in overlaps if len(o.sibling_kits) == 2]
    assert len(two_sibling_overlaps) >= 1
    # The two-sibling overlap should span the intersection (300-500)
    overlap = two_sibling_overlaps[0]
    assert overlap.B37_Start == 300
    assert overlap.B37_End == 500
    assert set(overlap.sibling_kits) == {"kit-A", "kit-B"}


def test_no_overlap():
    """Two non-overlapping segments → no multi-sibling overlaps."""
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 200),
        make_segment(1, "Bob", "kit-B", "Smith", 300, 400),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    multi_sibling = [o for o in overlaps if len(o.sibling_kits) > 1]
    assert len(multi_sibling) == 0


def test_three_siblings_overlapping():
    """Three siblings all overlap in a region → overlap lists all 3 kits."""
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 600),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 700),
        make_segment(1, "Carol", "kit-C", "Smith", 300, 800),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    three_sibling_overlaps = [o for o in overlaps if len(o.sibling_kits) == 3]
    assert len(three_sibling_overlaps) >= 1
    overlap = three_sibling_overlaps[0]
    assert overlap.B37_Start == 300
    assert overlap.B37_End == 600
    assert set(overlap.sibling_kits) == {"kit-A", "kit-B", "kit-C"}


def test_partial_overlaps():
    """A overlaps B, B overlaps C, but A doesn't overlap C → distinct overlaps."""
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 300),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 500),
        make_segment(1, "Carol", "kit-C", "Smith", 400, 600),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    two_sibling_overlaps = [o for o in overlaps if len(o.sibling_kits) == 2]
    assert len(two_sibling_overlaps) >= 2

    # AB overlap should be in 200-300 range
    ab_overlaps = [o for o in two_sibling_overlaps if set(o.sibling_kits) == {"kit-A", "kit-B"}]
    assert len(ab_overlaps) >= 1

    # BC overlap should be in 400-500 range
    bc_overlaps = [o for o in two_sibling_overlaps if set(o.sibling_kits) == {"kit-B", "kit-C"}]
    assert len(bc_overlaps) >= 1


def test_adjacent_segments():
    """Segments that touch at a boundary (end == start of next) → no multi-sibling overlap."""
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 300),
        make_segment(1, "Bob", "kit-B", "Smith", 300, 500),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    multi_sibling = [o for o in overlaps if len(o.sibling_kits) > 1]
    assert len(multi_sibling) == 0


def test_single_segment():
    """A single segment produces one overlap with just that sibling."""
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 500),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    assert len(overlaps) == 1
    assert overlaps[0].sibling_kits == ["kit-A"]
    assert overlaps[0].B37_Start == 100
    assert overlaps[0].B37_End == 500


def test_all_overlaps_have_correct_grandparent():
    """Every overlap should carry the grandparent from the input segments."""
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 500),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 600),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    for overlap in overlaps:
        assert overlap.Grandparent == "Smith"
