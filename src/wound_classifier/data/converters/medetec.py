"""Medetec Wound Database converter."""

import re
from pathlib import Path
from typing import Optional

from ..base import DataSourceConverter, HEURISTIC_LABELS
from ..utils import list_images


# Patterns for heuristic label extraction
MEDETEC_PATTERNS = {
    r"sloughy": 3.25,           # Slough typically Stage III-IV
    r"undermining": 3.5,        # Undermining indicates deeper wound
    r"necrotic": 3.75,          # Necrotic tissue often Stage IV
    r"eschar": 3.5,             # Eschar can be III or IV
    r"granulat": 2.5,           # Granulation can appear II-III
    r"stage[_\s]*(i{1,3}v?|[1-4])": None,  # Will be parsed specially
}


def _parse_stage_from_name(filename: str) -> Optional[float]:
    """Try to extract stage number from filename.

    Args:
        filename: Image filename

    Returns:
        Float stage if found, None otherwise
    """
    filename_lower = filename.lower()

    # Try to find stage patterns like "stage_1", "stage_iv", "stage-3"
    stage_match = re.search(r"stage[_\s-]*(i{1,3}v?|[1-4])", filename_lower)
    if stage_match:
        stage_str = stage_match.group(1)
        # Convert roman numerals
        roman_map = {"i": 1, "ii": 2, "iii": 3, "iv": 4}
        if stage_str in roman_map:
            return float(roman_map[stage_str])
        # Try integer
        try:
            return float(int(stage_str))
        except ValueError:
            pass

    return None


def _get_heuristic_stage(filename: str) -> Optional[float]:
    """Get heuristic stage based on filename patterns.

    Args:
        filename: Image filename

    Returns:
        Float stage based on heuristics, or None
    """
    filename_lower = filename.lower()

    # First try exact stage extraction
    stage = _parse_stage_from_name(filename_lower)
    if stage is not None:
        return stage

    # Then try heuristic patterns
    for pattern, label in MEDETEC_PATTERNS.items():
        if label is not None and re.search(pattern, filename_lower):
            return label

    return None


class MedetecConverter(DataSourceConverter):
    """Converter for Medetec Wound Database.

    Dataset structure:
        data/raw/medetec/
        └── [flat list of images with descriptive names]

    Images have descriptive filenames but no formal stage labels.
    Uses heuristic mapping based on filename patterns:
        - sloughy-* -> 3.25
        - undermining* -> 3.5
        - necrotic-* -> 3.75
        - eschar-* -> 3.5
        - granulation-* -> 2.5
        - Others -> None (unlabeled)
    """

    def __init__(self, raw_dir: Path, use_heuristics: bool = True):
        """Initialize Medetec converter.

        Args:
            raw_dir: Path to raw data directory
            use_heuristics: If True, use filename-based heuristic labels
        """
        super().__init__(raw_dir)
        self.use_heuristics = use_heuristics

    @property
    def source_name(self) -> str:
        return "medetec"

    def list_images(self) -> list[Path]:
        """List all images in the medetec directory."""
        return list_images(self.raw_dir, recursive=False)

    def get_stage(self, image_path: Path) -> Optional[float]:
        """Get stage label using heuristics if enabled.

        Args:
            image_path: Path to image file

        Returns:
            Float stage based on heuristics, or None if unlabeled
        """
        if not self.use_heuristics:
            return None

        return _get_heuristic_stage(image_path.name)

    def get_notes(self, image_path: Path) -> str:
        """Get notes indicating labeling method."""
        stage = self.get_stage(image_path)
        filename = image_path.name

        if stage is not None:
            # Determine which pattern matched
            filename_lower = filename.lower()
            for pattern in ["sloughy", "undermining", "necrotic", "eschar", "granulat"]:
                if pattern in filename_lower:
                    return f"heuristic:{pattern}"
            if _parse_stage_from_name(filename_lower) is not None:
                return "filename:stage_number"
            return "heuristic:unknown_pattern"

        return "unlabeled"

    def should_include(self, image_path: Path) -> bool:
        """Include all valid images."""
        return True
