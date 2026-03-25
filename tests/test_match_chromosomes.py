"""Tests for GrandMatch.match_chromosomes()

Test setup:
- Chromosome 1, grandparent "Smith"
- Alice (kit-A) has Smith segment 100-1000
- Bob (kit-B) has Smith segment 200-800
- Overlap: kit-A and kit-B share Smith from 200-800
- bestSiblingKit = kit-A (first in overlap.sibling_kits)
- Triangulation is from Alice's file; Kit2 must be Bob to confirm the match

NOTE: Because of Bug 1 (last TriangGroup is never evaluated), we must add
a "flushing" group after the group under test. We use a sibling kit as
Kit1 for the flushing group since siblings are always excluded, making
it a no-op that just triggers evaluation of the previous group.
"""
import pytest
from tests.conftest import (
    make_sibling, make_grandparent, make_cousin, make_segment, make_triang,
    build_grand_match,
)


def _flush_triang(chr: int = 1) -> "Triang":
    """A trailing triang with a Kit1 that sorts LAST, triggering eval of the previous group.

    Uses 'zzz-flush' so it sorts after any real kit numbers.
    This group will itself be dropped (never evaluated as last group — Bug 1),
    but it forces the PREVIOUS group to be evaluated.
    """
    return make_triang(chr, "zzz-flush", "kit-random", 300, 600)


def _setup_two_sibling_overlap(
    extra_cousins=None,
    triangulations_for_alice=None,
    extra_siblings=None,
):
    """Helper to build a GrandMatch with a standard 2-sibling overlap on chr 1."""
    siblings = {
        "kit-A": make_sibling("Alice", "kit-A"),
        "kit-B": make_sibling("Bob", "kit-B"),
    }
    if extra_siblings:
        siblings.update(extra_siblings)

    siblings_by_name = {s.name: s for s in siblings.values()}

    grandparents = {
        "Smith": make_grandparent("Smith"),
        "Jones": make_grandparent("Jones"),
    }

    cousins_by_kit = {}
    cousins_by_name = {}
    if extra_cousins:
        for c in extra_cousins:
            cousins_by_kit[c.kit] = c
            cousins_by_name[c.name] = c

    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 1000),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 800),
    ]

    trianqs_alice = triangulations_for_alice or []
    trianqs_bob = []

    triangulations = {"kit-A": trianqs_alice, "kit-B": trianqs_bob}
    for kit in siblings:
        if kit not in triangulations:
            triangulations[kit] = []

    gm = build_grand_match(
        siblings_by_kit=siblings,
        siblings_by_name=siblings_by_name,
        grandparents_by_name=grandparents,
        cousins_by_kit=cousins_by_kit,
        cousins_by_name=cousins_by_name,
        segments=segments,
        triangulations_by_sibling=triangulations,
    )
    return gm


# --- Core matching tests ---
# These tests work around Bug 1 by appending a flush group.

def test_basic_valid_match():
    """A stranger triangulates with Alice, and Kit2=Bob (the other overlap sibling) → included."""
    gm = _setup_two_sibling_overlap(
        triangulations_for_alice=[
            make_triang(1, "kit-stranger", "kit-B", 300, 600),
            _flush_triang(),
        ],
    )
    result = gm.match_chromosomes()

    stranger_results = [t for t in result if t.Kit1_Number == "kit-stranger"]
    assert len(stranger_results) == 1
    assert stranger_results[0].grandparent == "Smith"


def test_kit1_is_sibling_excluded():
    """If Kit1 is itself a sibling, exclude it."""
    gm = _setup_two_sibling_overlap(
        triangulations_for_alice=[
            make_triang(1, "kit-B", "kit-stranger", 300, 600),
            _flush_triang(),
        ],
    )
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-B" not in kit1s


def test_kit1_is_cousin_of_different_grandparent_excluded():
    """If Kit1 is a known cousin of Jones (not Smith), exclude it."""
    jones_cousin = make_cousin("JonesCuz", "kit-jones-cuz", "Jones")
    gm = _setup_two_sibling_overlap(
        extra_cousins=[jones_cousin],
        triangulations_for_alice=[
            make_triang(1, "kit-jones-cuz", "kit-B", 300, 600),
            _flush_triang(),
        ],
    )
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-jones-cuz" not in kit1s


def test_group_contains_excluded_cousin_via_kit2():
    """If any triang in the group has Kit2 = a cousin of a different grandparent, exclude the group."""
    jones_cousin = make_cousin("JonesCuz", "kit-jones-cuz", "Jones")
    gm = _setup_two_sibling_overlap(
        extra_cousins=[jones_cousin],
        triangulations_for_alice=[
            make_triang(1, "kit-stranger", "kit-B", 300, 600),
            make_triang(1, "kit-stranger", "kit-jones-cuz", 300, 600),
            _flush_triang(),
        ],
    )
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-stranger" not in kit1s


def test_group_missing_required_overlap_sibling():
    """Group doesn't include Bob as Kit2 → missing required overlap sibling → excluded."""
    gm = _setup_two_sibling_overlap(
        triangulations_for_alice=[
            make_triang(1, "kit-stranger", "kit-random", 300, 600),
            _flush_triang(),
        ],
    )
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-stranger" not in kit1s


def test_group_contains_non_overlap_sibling():
    """Group has Kit2 = Carol (a sibling NOT in this overlap) → excluded."""
    carol = make_sibling("Carol", "kit-C")
    gm = _setup_two_sibling_overlap(
        extra_siblings={"kit-C": carol},
        triangulations_for_alice=[
            make_triang(1, "kit-stranger", "kit-B", 300, 600),
            make_triang(1, "kit-stranger", "kit-C", 300, 600),
            _flush_triang(),
        ],
    )
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-stranger" not in kit1s


# --- Regression tests for fixed bugs ---

def test_last_group_is_included():
    """The final Kit1 group should be evaluated and included if valid.

    Current code only evaluates a group when a NEW Kit1 is encountered,
    so the very last group is silently dropped.
    """
    gm = _setup_two_sibling_overlap(
        triangulations_for_alice=[
            # Only one Kit1 group — it's the last group and never flushed
            make_triang(1, "kit-stranger", "kit-B", 300, 600),
        ],
    )
    result = gm.match_chromosomes()

    kit1s = [t.Kit1_Number for t in result]
    assert "kit-stranger" in kit1s


def test_triang_not_mutated_across_overlaps():
    """When the same Triang falls in two overlaps, its grandparent should not be overwritten.

    Current code sets t.grandparent directly on the Triang object, so processing
    a second overlap overwrites the first attribution.
    """
    siblings = {
        "kit-A": make_sibling("Alice", "kit-A"),
        "kit-B": make_sibling("Bob", "kit-B"),
    }
    siblings_by_name = {s.name: s for s in siblings.values()}
    grandparents = {
        "Smith": make_grandparent("Smith"),
        "Jones": make_grandparent("Jones"),
    }

    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 1000),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 800),
        make_segment(1, "Alice", "kit-A", "Jones", 100, 1000),
        make_segment(1, "Bob", "kit-B", "Jones", 200, 800),
    ]

    shared_triang = make_triang(1, "kit-stranger", "kit-B", 300, 600)
    flush = make_triang(1, "zzz-flush", "kit-random", 300, 600)

    gm = build_grand_match(
        siblings_by_kit=siblings,
        siblings_by_name=siblings_by_name,
        grandparents_by_name=grandparents,
        cousins_by_kit={},
        cousins_by_name={},
        segments=segments,
        triangulations_by_sibling={"kit-A": [shared_triang, flush], "kit-B": []},
    )
    result = gm.match_chromosomes()

    smith_results = [t for t in result if t.grandparent == "Smith"]
    jones_results = [t for t in result if t.grandparent == "Jones"]
    assert len(smith_results) >= 1, "Should have Smith-attributed results"
    assert len(jones_results) >= 1, "Should have Jones-attributed results"
