"""Integration tests — full pipeline with synthetic data."""
import os
import tempfile
import csv
import pytest
from grand_match import ChromosomeSetting
from tests.conftest import (
    make_sibling, make_grandparent, make_cousin, make_segment, make_triang,
    build_grand_match,
)


def _build_full_pipeline():
    """Build a complete GrandMatch scenario with 3 siblings, 2 grandparents.

    Chromosome 1:
    - Alice + Bob overlap on Smith (200-800)
    - Alice + Carol overlap on Jones (300-700)

    Triangulation data (from Alice's perspective):
    - kit-smith-match: triangulates with Bob in Smith overlap → valid Smith match
    - kit-jones-match: triangulates with Carol in Jones overlap → valid Jones match
    - kit-A (Alice): sibling as Kit1 → should be excluded
    - kit-cuz-jones: known Jones cousin as Kit1 in Smith overlap → should be excluded
    """
    siblings = {
        "kit-A": make_sibling("Alice", "kit-A"),
        "kit-B": make_sibling("Bob", "kit-B"),
        "kit-C": make_sibling("Carol", "kit-C"),
    }
    siblings_by_name = {s.name: s for s in siblings.values()}

    grandparents = {
        "Smith": make_grandparent("Smith"),
        "Jones": make_grandparent("Jones"),
    }

    jones_cousin = make_cousin("JonesCuz", "kit-cuz-jones", "Jones")
    cousins_by_kit = {"kit-cuz-jones": jones_cousin}
    cousins_by_name = {"JonesCuz": jones_cousin}

    segments = [
        # Smith segments: Alice + Bob overlap
        make_segment(1, "Alice", "kit-A", "Smith", 100, 1000),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 800),
        # Jones segments: Alice + Carol overlap
        make_segment(1, "Alice", "kit-A", "Jones", 200, 900),
        make_segment(1, "Carol", "kit-C", "Jones", 300, 700),
    ]

    triangulations = {
        "kit-A": [
            # Valid Smith match: stranger triangulates with Bob
            make_triang(1, "kit-smith-match", "kit-B", 300, 600),
            # Valid Jones match: stranger triangulates with Carol
            make_triang(1, "kit-jones-match", "kit-C", 400, 600),
            # Sibling as Kit1: should be excluded
            make_triang(1, "kit-B", "kit-smith-match", 300, 600),
            # Known Jones cousin in Smith overlap: should be excluded from Smith
            make_triang(1, "kit-cuz-jones", "kit-B", 300, 600),
        ],
        "kit-B": [],
        "kit-C": [],
    }

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


def test_full_pipeline_happy_path():
    """Full pipeline produces correct matches with proper grandparent attribution."""
    gm = _build_full_pipeline()
    result = gm.match_chromosomes()

    kit1s = set(t.Kit1_Number for t in result)

    # Valid matches should be included
    assert "kit-smith-match" in kit1s
    assert "kit-jones-match" in kit1s

    # Sibling and wrong-grandparent cousin should be excluded
    assert "kit-B" not in kit1s
    assert "kit-cuz-jones" not in kit1s

    # Verify grandparent attribution
    smith_matches = [t for t in result if t.Kit1_Number == "kit-smith-match"]
    assert all(t.grandparent == "Smith" for t in smith_matches)

    jones_matches = [t for t in result if t.Kit1_Number == "kit-jones-match"]
    assert all(t.grandparent == "Jones" for t in jones_matches)


def test_multi_chromosome_pipeline():
    """Pipeline handles multiple chromosomes, producing results for each."""
    siblings = {
        "kit-A": make_sibling("Alice", "kit-A"),
        "kit-B": make_sibling("Bob", "kit-B"),
    }
    siblings_by_name = {s.name: s for s in siblings.values()}
    grandparents = {"Smith": make_grandparent("Smith")}

    segments = [
        make_segment(1, "Alice", "kit-A", "Smith", 100, 1000),
        make_segment(1, "Bob", "kit-B", "Smith", 200, 800),
        make_segment(2, "Alice", "kit-A", "Smith", 50, 600),
        make_segment(2, "Bob", "kit-B", "Smith", 100, 500),
    ]

    triangulations = {
        "kit-A": [
            make_triang(1, "kit-match-chr1", "kit-B", 300, 600),
            make_triang(2, "kit-match-chr2", "kit-B", 200, 400),
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

    chr1_kit1s = set(t.Kit1_Number for t in result if t.Chr == 1)
    chr2_kit1s = set(t.Kit1_Number for t in result if t.Chr == 2)

    assert "kit-match-chr1" in chr1_kit1s
    assert "kit-match-chr2" in chr2_kit1s


def test_no_matches_found():
    """When all triangulations fail validation, result is empty without errors."""
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

    triangulations = {
        "kit-A": [
            # Kit1 is a sibling → excluded
            make_triang(1, "kit-B", "kit-random", 300, 600),
            # Kit2 is not an overlap sibling → group fails validation
            make_triang(1, "kit-stranger", "kit-random", 300, 600),
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
    assert result == []


def test_export_writes_correct_csv(tmp_path):
    """Export produces a CSV file with correct columns and row count."""
    gm = _build_full_pipeline()
    result = gm.match_chromosomes()

    output_dir = str(tmp_path / "test_output")
    gm.export_triangs_to_csv(triangs=result, directory=output_dir)

    csv_path = os.path.join(output_dir, "matched_triangulations.csv")
    assert os.path.exists(csv_path)

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Should have the same number of rows as the result
    assert len(rows) == len(result)

    # Verify expected columns exist
    expected_columns = {"Chr", "Kit1_Number", "Kit1_Name", "Kit2_Number",
                        "B37_Start", "B37_End", "cM", "grandparent", "source_sibling"}
    assert expected_columns.issubset(set(rows[0].keys()))

    # Verify grandparent attribution made it to CSV
    grandparents_in_csv = set(r["grandparent"] for r in rows)
    assert "Smith" in grandparents_in_csv
    assert "Jones" in grandparents_in_csv
