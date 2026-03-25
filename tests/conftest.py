import pytest
from typing import Dict, List

from grand_match import (
    Sibling, Cousin, Grandparent, GrandparentSegment,
    SiblingOverlap, Triang, ChromosomeModel, ChromosomeSetting,
    TriangGroup, GrandMatch,
)


# --- Factory helpers ---

def make_sibling(name: str, kit: str) -> Sibling:
    return Sibling(name=name, kit=kit)


def make_grandparent(name: str) -> Grandparent:
    return Grandparent(name=name)


def make_cousin(name: str, kit: str, grandparent: str) -> Cousin:
    return Cousin(name=name, kit=kit, grandparent=grandparent)


def make_segment(chr: int, sibling: str, kit: str, grandparent: str, start: int, end: int) -> GrandparentSegment:
    return GrandparentSegment(Chr=chr, Sibling=sibling, Kit=kit, Grandparent=grandparent, B37_Start=start, B37_End=end)


def make_triang(
    chr: int, kit1_number: str, kit2_number: str,
    start: int, end: int,
    kit1_name: str = "", kit2_name: str = "",
    kit1_email: str = "", kit2_email: str = "",
    cm: str = "10.0",
) -> Triang:
    return Triang(
        Chr=chr,
        Kit1_Number=kit1_number, Kit1_Name=kit1_name or kit1_number, Kit1_Email=kit1_email,
        Kit2_Number=kit2_number, Kit2_Name=kit2_name or kit2_number, Kit2_Email=kit2_email,
        B37_Start=start, B37_End=end, cM=cm,
    )


# --- Standard test data fixtures ---

@pytest.fixture
def siblings_by_kit() -> Dict[str, Sibling]:
    alice = make_sibling("Alice", "kit-A")
    bob = make_sibling("Bob", "kit-B")
    carol = make_sibling("Carol", "kit-C")
    return {"kit-A": alice, "kit-B": bob, "kit-C": carol}


@pytest.fixture
def siblings_by_name(siblings_by_kit) -> Dict[str, Sibling]:
    return {s.name: s for s in siblings_by_kit.values()}


@pytest.fixture
def grandparents_by_name() -> Dict[str, Grandparent]:
    return {
        "Smith": make_grandparent("Smith"),
        "Jones": make_grandparent("Jones"),
    }


@pytest.fixture
def cousins_by_kit() -> Dict[str, Cousin]:
    return {
        "kit-cuz-smith": make_cousin("CousinSmith", "kit-cuz-smith", "Smith"),
    }


@pytest.fixture
def cousins_by_name(cousins_by_kit) -> Dict[str, Cousin]:
    return {c.name: c for c in cousins_by_kit.values()}


def build_grand_match(
    siblings_by_kit: Dict[str, Sibling],
    siblings_by_name: Dict[str, Sibling],
    grandparents_by_name: Dict[str, Grandparent],
    cousins_by_kit: Dict[str, Cousin],
    cousins_by_name: Dict[str, Cousin],
    segments: List[GrandparentSegment],
    triangulations_by_sibling: Dict[str, List[Triang]],
    chromosome_settings: Dict[int, ChromosomeSetting] = None,
) -> GrandMatch:
    """Build a minimal GrandMatch instance ready to run the pipeline."""
    gm = GrandMatch()
    gm.siblingsByKit = siblings_by_kit
    gm.siblingsByName = siblings_by_name
    gm.grandparentsByName = grandparents_by_name
    gm.cousinByKit = cousins_by_kit
    gm.cousinByName = cousins_by_name
    gm.grandparent_segments = segments

    # Default: enable all chromosomes found in segments
    if chromosome_settings is None:
        chrs = set(s.Chr for s in segments)
        chromosome_settings = {c: ChromosomeSetting(chr=c, mode="Yes") for c in chrs}

    gm.triangulationBySiblingKit = triangulations_by_sibling
    gm.create_chromosome_models(chromosome_settings)
    gm.LoopOnChromosomeData()
    return gm
