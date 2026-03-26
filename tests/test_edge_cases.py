"""Edge case tests for overlap calculation and triangulation matching."""
import pytest
from grand_match import OverlapCalculator, ChromosomeSetting
from tests.conftest import (
    make_sibling, make_grandparent, make_cousin, make_segment, make_triang,
    build_grand_match,
)


# --- Overlap Calculator edge cases ---

def test_segments_with_negative_values():
    """Segments with (-1, -1) represent 'no segment' and should not produce meaningful overlaps.

    Real data has these for Dennis/Diane Mystery on chr 2.
    """
    segments = [
        make_segment(2, "Alice", "kit-A", "Smith", 100, 500),
        make_segment(2, "Bob", "kit-B", "Smith", -1, -1),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    # The (-1, -1) segment should not produce a valid multi-sibling overlap
    # with the real segment
    for o in overlaps:
        if len(o.sibling_kits) > 1:
            assert o.B37_Start >= 0, "Overlap start should not be negative"
            assert o.B37_End >= 0, "Overlap end should not be negative"


def test_segment_starting_at_zero():
    """Segments starting at position 0 should be handled correctly.

    The sweep-line starts active_event_number at 0, so a segment starting
    at 0 should be activated on the first iteration.
    """
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 0, 500),
        make_segment(1, "Bob", "kit-B", "Smith", 0, 300),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    two_sibling = [o for o in overlaps if len(o.sibling_kits) == 2]
    assert len(two_sibling) >= 1
    overlap = two_sibling[0]
    assert overlap.B37_Start == 0
    assert overlap.B37_End == 300


def test_identical_segments():
    """Two siblings with exactly the same start/end should produce one overlap."""
    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 500),
        make_segment(1, "Bob", "kit-B", "Smith", 100, 500),
    ]
    calculator = OverlapCalculator(segments)
    overlaps = calculator.calculate_overlaps()

    two_sibling = [o for o in overlaps if len(o.sibling_kits) == 2]
    assert len(two_sibling) >= 1
    overlap = two_sibling[0]
    assert overlap.B37_Start == 100
    assert overlap.B37_End == 500
    assert set(overlap.sibling_kits) == {"kit-A", "kit-B"}


# --- Match chromosomes edge cases ---

def _build_standard_gm(triangulations_for_alice, extra_siblings=None):
    """Build a GrandMatch with Alice+Bob Smith overlap on chr 1."""
    siblings = {
        "kit-A": make_sibling("Alice", "kit-A"),
        "kit-B": make_sibling("Bob", "kit-B"),
    }
    if extra_siblings:
        siblings.update(extra_siblings)

    siblings_by_name = {s.name: s for s in siblings.values()}
    grandparents = {"Smith": make_grandparent("Smith")}

    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 1000),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 800),
    ]

    triangulations = {"kit-A": triangulations_for_alice, "kit-B": []}
    for kit in siblings:
        if kit not in triangulations:
            triangulations[kit] = []

    return build_grand_match(
        siblings_by_kit=siblings,
        siblings_by_name=siblings_by_name,
        grandparents_by_name=grandparents,
        cousins_by_kit={},
        cousins_by_name={},
        segments=segments,
        triangulations_by_sibling=triangulations,
    )


def test_empty_triangulation_for_sibling():
    """A sibling with no triangulation records should not crash the pipeline."""
    siblings = {
        "kit-A": make_sibling("Alice", "kit-A"),
        "kit-B": make_sibling("Bob", "kit-B"),
    }
    siblings_by_name = {s.name: s for s in siblings.values()}
    grandparents = {"Smith": make_grandparent("Smith")}

    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 1000),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 800),
    ]

    # Both siblings have empty triangulation lists
    gm = build_grand_match(
        siblings_by_kit=siblings,
        siblings_by_name=siblings_by_name,
        grandparents_by_name=grandparents,
        cousins_by_kit={},
        cousins_by_name={},
        segments=segments,
        triangulations_by_sibling={"kit-A": [], "kit-B": []},
    )
    result = gm.match_chromosomes()
    assert result == []


def test_multiple_valid_kit1_groups():
    """Several strangers all pass validation — all should appear in results."""
    gm = _build_standard_gm([
        make_triang(1, "kit-stranger1", "kit-B", 300, 600),
        make_triang(1, "kit-stranger2", "kit-B", 300, 600),
        make_triang(1, "kit-stranger3", "kit-B", 400, 700),
    ])
    result = gm.match_chromosomes()

    kit1s = set(t.Kit1_Number for t in result)
    assert "kit-stranger1" in kit1s
    assert "kit-stranger2" in kit1s
    assert "kit-stranger3" in kit1s


def test_kit1_on_multiple_chromosomes():
    """Same stranger matches on chr 1 and chr 2 — both should be included."""
    siblings = {
        "kit-A": make_sibling("Alice", "kit-A"),
        "kit-B": make_sibling("Bob", "kit-B"),
    }
    siblings_by_name = {s.name: s for s in siblings.values()}
    grandparents = {"Smith": make_grandparent("Smith")}

    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 1000),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 800),
        make_segment(2, "Alice", "kit-A", "Smith", 100, 1000),
        make_segment(2, "Bob", "kit-B", "Smith", 200, 800),
    ]

    triangulations = {
        "kit-A": [
            make_triang(1, "kit-stranger", "kit-B", 300, 600),
            make_triang(2, "kit-stranger", "kit-B", 300, 600),
        ],
        "kit-B": [],
    }

    gm = build_grand_match(
        siblings_by_kit=siblings,
        siblings_by_name=siblings_by_name,
        grandparents_by_name=grandparents,
        cousins_by_kit={},
        cousins_by_name={},
        segments=segments,
        triangulations_by_sibling=triangulations,
    )
    result = gm.match_chromosomes()

    chr1_results = [t for t in result if t.Chr == 1 and t.Kit1_Number == "kit-stranger"]
    chr2_results = [t for t in result if t.Chr == 2 and t.Kit1_Number == "kit-stranger"]
    assert len(chr1_results) >= 1
    assert len(chr2_results) >= 1


def test_triang_exactly_at_overlap_boundary():
    """Triang with start/end exactly matching overlap boundaries should be included."""
    # Overlap is 200-800 (intersection of Alice 100-1000 and Bob 200-800)
    gm = _build_standard_gm([
        make_triang(1, "kit-stranger", "kit-B", 200, 800),
    ])
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-stranger" in kit1s


def test_triang_partially_outside_overlap():
    """Triang with B37_Start inside overlap but B37_End outside should be excluded.

    The boundary check requires: start >= overlap.start AND start <= overlap.end AND end <= overlap.end
    """
    # Overlap is 200-800; triang ends at 900 which is outside
    gm = _build_standard_gm([
        make_triang(1, "kit-stranger", "kit-B", 300, 900),
    ])
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-stranger" not in kit1s


def test_triang_completely_outside_overlap():
    """Triang entirely outside the overlap region should be excluded."""
    # Overlap is 200-800; triang is at 50-150
    gm = _build_standard_gm([
        make_triang(1, "kit-stranger", "kit-B", 50, 150),
    ])
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-stranger" not in kit1s
