"""Base classes and data structures for wound data processing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ImageRecord:
    """Standardized record for a processed wound image.

    Attributes:
        filename: Name of the processed file
        original_source: Source dataset identifier (e.g., 'kaggle', 'medetec')
        original_filename: Original filename in the raw dataset
        original_path: Full path to the original file
        stage: Wound severity label (0.0-4.0 continuous scale)
               0.0 = healthy/healed
               1.0 = Stage I (non-blanchable erythema)
               2.0 = Stage II (partial thickness)
               3.0 = Stage III (full thickness, fat visible)
               4.0 = Stage IV (full thickness, bone/tendon visible)
               None = unlabeled/unknown
        width: Image width in pixels
        height: Image height in pixels
        verified: Whether the label has been manually verified
        notes: Additional notes (e.g., labeling method, uncertainty)
    """
    filename: str
    original_source: str
    original_filename: str
    original_path: Path
    stage: Optional[float]
    width: int
    height: int
    verified: bool = False
    notes: str = ""

    def __post_init__(self):
        """Validate stage is in valid range."""
        if self.stage is not None:
            if not 0.0 <= self.stage <= 4.0:
                raise ValueError(f"Stage must be between 0.0 and 4.0, got {self.stage}")

    @property
    def is_labeled(self) -> bool:
        """Check if this image has a label."""
        return self.stage is not None

    @property
    def stage_folder(self) -> str:
        """Get the folder name based on rounded stage.

        Returns:
            Folder name like 'stage_1', 'stage_2', etc., or 'unlabeled'
        """
        if self.stage is None:
            return "unlabeled"

        # Round to nearest integer stage (1-4)
        rounded = round(self.stage)
        # Clamp to valid range
        rounded = max(1, min(4, rounded))
        return f"stage_{rounded}"

    def to_csv_row(self) -> dict:
        """Convert to dictionary for CSV export."""
        return {
            "filename": self.filename,
            "original_source": self.original_source,
            "original_filename": self.original_filename,
            "stage": self.stage if self.stage is not None else "",
            "width": self.width,
            "height": self.height,
            "verified": str(self.verified).lower(),
            "notes": self.notes
        }


class DataSourceConverter(ABC):
    """Abstract base class for data source converters.

    Each data source (Kaggle, Medetec, Figshare, etc.) should implement
    this interface to convert raw data to the standardized format.
    """

    def __init__(self, raw_dir: Path):
        """Initialize converter with path to raw data.

        Args:
            raw_dir: Path to the raw data directory for this source
        """
        self._raw_dir = Path(raw_dir)
        if not self._raw_dir.exists():
            raise FileNotFoundError(f"Raw directory not found: {self._raw_dir}")

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier for this data source.

        Returns:
            Short identifier like 'kaggle', 'medetec', 'figshare'
        """
        pass

    @property
    def raw_dir(self) -> Path:
        """Path to raw data directory."""
        return self._raw_dir

    @abstractmethod
    def list_images(self) -> list[Path]:
        """List all image files in this data source.

        Returns:
            List of paths to image files
        """
        pass

    @abstractmethod
    def get_stage(self, image_path: Path) -> Optional[float]:
        """Extract stage label for an image.

        Args:
            image_path: Path to the image file

        Returns:
            Float stage value (0.0-4.0) or None if unknown
        """
        pass

    def get_notes(self, image_path: Path) -> str:
        """Get notes for an image (e.g., labeling method).

        Override this method to provide source-specific notes.

        Args:
            image_path: Path to the image file

        Returns:
            Notes string
        """
        return ""

    def should_include(self, image_path: Path) -> bool:
        """Check if an image should be included in processing.

        Override this method to filter out unwanted images.

        Args:
            image_path: Path to the image file

        Returns:
            True if image should be processed
        """
        return True


# Constants for label standardization
STAGE_LABELS = {
    "healthy": 0.0,
    "stage_1": 1.0,
    "stage_i": 1.0,
    "stage_2": 2.0,
    "stage_ii": 2.0,
    "stage_3": 3.0,
    "stage_iii": 3.0,
    "stage_4": 4.0,
    "stage_iv": 4.0,
}

# Heuristic mappings for descriptive labels
HEURISTIC_LABELS = {
    "sloughy": 3.25,      # Slough typically Stage III-IV
    "undermining": 3.5,   # Undermining indicates deeper wound
    "necrotic": 3.75,     # Necrotic tissue often Stage IV
    "eschar": 3.5,        # Eschar can be III or IV
    "granulation": 2.5,   # Granulation can appear II-III
}
