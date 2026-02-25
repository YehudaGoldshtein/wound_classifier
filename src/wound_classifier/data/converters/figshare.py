"""Figshare Pressure Ulcer Dataset converter."""

import json
from pathlib import Path
from typing import Optional

from ..base import DataSourceConverter
from ..utils import list_images, IMAGE_EXTENSIONS


# Heuristic patterns for Figshare filenames
FIGSHARE_PATTERNS = {
    "sloughy": 3.25,
    "undermining": 3.5,
    "necrotic": 3.75,
    "healing": None,  # Unknown stage - could be any stage improving
    "pressure-ulcer": None,  # Generic, no stage info
}


class FigshareConverter(DataSourceConverter):
    """Converter for Figshare Pressure Ulcer Dataset.

    Dataset structure:
        data/raw/figshare/
        ├── healing-pressure-ulcer-*.jpg
        ├── healing-pressure-ulcer-*.json  (Labelme annotation)
        ├── sloughy-pressure-ulcer-*.jpg
        ├── sloughy-pressure-ulcer-*.json
        ├── undermining*.jpg
        ├── undermining*.json
        └── pressure-ulcer-on-*.jpg/json

    Each image has a corresponding JSON annotation file in Labelme format.
    Uses heuristic mapping based on filename patterns.
    """

    def __init__(self, raw_dir: Path, use_heuristics: bool = True):
        """Initialize Figshare converter.

        Args:
            raw_dir: Path to raw data directory
            use_heuristics: If True, use filename-based heuristic labels
        """
        super().__init__(raw_dir)
        self.use_heuristics = use_heuristics

    @property
    def source_name(self) -> str:
        return "figshare"

    def list_images(self) -> list[Path]:
        """List all image files (excluding JSON annotations)."""
        return list_images(self.raw_dir, recursive=False)

    def _get_annotation_path(self, image_path: Path) -> Optional[Path]:
        """Get path to corresponding JSON annotation file.

        Args:
            image_path: Path to image file

        Returns:
            Path to JSON file if exists, None otherwise
        """
        json_path = image_path.with_suffix(".json")
        if json_path.exists():
            return json_path
        return None

    def _parse_annotation(self, json_path: Path) -> dict:
        """Parse Labelme JSON annotation file.

        Args:
            json_path: Path to JSON file

        Returns:
            Parsed annotation data
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _get_stage_from_annotation(self, annotation: dict) -> Optional[float]:
        """Try to extract stage from annotation labels.

        Args:
            annotation: Parsed Labelme annotation

        Returns:
            Float stage if found in annotation, None otherwise
        """
        # Check shapes for stage labels
        shapes = annotation.get("shapes", [])
        for shape in shapes:
            label = shape.get("label", "").lower()

            # Look for stage patterns in labels
            if "stage" in label:
                for i in range(1, 5):
                    if str(i) in label or ["i", "ii", "iii", "iv"][i-1] in label:
                        return float(i)

        return None

    def get_stage(self, image_path: Path) -> Optional[float]:
        """Get stage label from annotation or filename heuristics.

        Args:
            image_path: Path to image file

        Returns:
            Float stage or None if unknown
        """
        # First try to get from annotation
        json_path = self._get_annotation_path(image_path)
        if json_path:
            annotation = self._parse_annotation(json_path)
            stage = self._get_stage_from_annotation(annotation)
            if stage is not None:
                return stage

        # Fall back to filename heuristics
        if self.use_heuristics:
            filename_lower = image_path.name.lower()
            for pattern, label in FIGSHARE_PATTERNS.items():
                if pattern in filename_lower:
                    return label

        return None

    def get_notes(self, image_path: Path) -> str:
        """Get notes about the image and its annotation."""
        notes = []

        # Check for annotation
        json_path = self._get_annotation_path(image_path)
        if json_path:
            notes.append("has_annotation")
            annotation = self._parse_annotation(json_path)
            shapes = annotation.get("shapes", [])
            if shapes:
                labels = [s.get("label", "") for s in shapes]
                notes.append(f"labels:{','.join(labels)}")

        # Check labeling method
        stage = self.get_stage(image_path)
        if stage is not None:
            filename_lower = image_path.name.lower()
            for pattern in FIGSHARE_PATTERNS:
                if pattern in filename_lower:
                    notes.append(f"heuristic:{pattern}")
                    break

        return ";".join(notes) if notes else "unlabeled"

    def should_include(self, image_path: Path) -> bool:
        """Include all image files."""
        return image_path.suffix.lower() in IMAGE_EXTENSIONS
