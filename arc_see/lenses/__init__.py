"""Lens system — pure functions that transform grids into annotations."""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


# --- Annotation types ---

@dataclass(frozen=True)
class RegionLabels:
    """Output of spatial lenses: integer-labeled regions."""
    labels: np.ndarray          # (64, 64) int array, 0 = background
    count: int                  # number of distinct regions (excluding background)

@dataclass(frozen=True)
class EdgeMask:
    """Binary edge mask."""
    mask: np.ndarray            # (64, 64) bool array

@dataclass(frozen=True)
class ContainmentTree:
    """Nested containment: which regions are inside which."""
    parent: dict[int, int | None]   # region_id → parent_region_id (None = top-level)
    children: dict[int, list[int]]  # region_id → list of contained region_ids

@dataclass(frozen=True)
class DisplacementField:
    """Per-object displacement vectors between frames."""
    vectors: dict[int, tuple[float, float]]  # object_id → (dy, dx)

@dataclass(frozen=True)
class ChangeMask:
    """Appeared/disappeared or same-position-color-change mask."""
    appeared: np.ndarray        # (64, 64) bool
    disappeared: np.ndarray     # (64, 64) bool

@dataclass(frozen=True)
class StateChangeMask:
    """Same position, different color."""
    mask: np.ndarray            # (64, 64) bool
    old_colors: np.ndarray      # (64, 64) int, valid where mask is True
    new_colors: np.ndarray      # (64, 64) int, valid where mask is True

@dataclass(frozen=True)
class SymmetryResult:
    """Detected symmetry axes."""
    horizontal: bool
    vertical: bool
    rotational_order: int       # 0 = none, 2 = 180°, 4 = 90°

@dataclass(frozen=True)
class PeriodicityResult:
    """Detected repeating patterns."""
    row_period: int | None      # None if no row periodicity
    col_period: int | None

@dataclass(frozen=True)
class AlignmentResult:
    """Grid-like arrangement detection."""
    row_lines: list[int]        # y-coordinates of detected row boundaries
    col_lines: list[int]        # x-coordinates of detected column boundaries

@dataclass(frozen=True)
class ProximityGraph:
    """Distance graph between objects."""
    distances: dict[tuple[int, int], float]  # (obj_a, obj_b) → centroid distance

@dataclass(frozen=True)
class ColorCorrespondence:
    """Color-to-object-group mapping."""
    color_to_objects: dict[int, list[int]]   # color → list of object_ids
    object_to_color: dict[int, int]          # object_id → dominant color

@dataclass(frozen=True)
class SizeCount:
    """Object sizes and group counts."""
    sizes: dict[int, int]       # object_id → pixel count
    count_by_size: dict[int, int]  # pixel_count → number of objects with that size

@dataclass(frozen=True)
class GoalDetection:
    """Candidate goal pattern and similarity to current state."""
    pattern: np.ndarray | None  # extracted goal region, or None if no goal detected
    location: tuple[int, int, int, int] | None  # (y1, x1, y2, x2) bounding box
    similarity: float           # 0.0-1.0, similarity of current state to goal


# Union of all annotation types
Annotation = (
    RegionLabels | EdgeMask | ContainmentTree |
    DisplacementField | ChangeMask | StateChangeMask |
    SymmetryResult | PeriodicityResult | AlignmentResult |
    ProximityGraph | ColorCorrespondence | SizeCount |
    GoalDetection
)


# --- Lens protocols ---

@runtime_checkable
class Lens(Protocol):
    """A lens that operates on a single grid."""
    name: str
    def __call__(self, grid: np.ndarray) -> Annotation: ...

@runtime_checkable
class TemporalLens(Protocol):
    """A lens that operates on grid history."""
    name: str
    def __call__(self, current: np.ndarray, history: list[np.ndarray]) -> Annotation: ...

@runtime_checkable
class DependentLens(Protocol):
    """A lens that depends on another lens's output."""
    name: str
    depends_on: str  # name of the lens this depends on
    def __call__(self, grid: np.ndarray, dependency: Annotation) -> Annotation: ...


# --- Registry ---

_LENSES: dict[str, Lens | TemporalLens | DependentLens] = {}

def register(lens: Lens | TemporalLens | DependentLens) -> None:
    _LENSES[lens.name] = lens

def get_all() -> dict[str, Lens | TemporalLens | DependentLens]:
    return dict(_LENSES)
