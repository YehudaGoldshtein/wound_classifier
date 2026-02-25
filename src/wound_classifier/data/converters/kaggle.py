"""Kaggle Pressure Ulcer Stages dataset converter."""

from pathlib import Path
from typing import Optional

from ..base import DataSourceConverter
from ..utils import list_images


# Mapping from Kaggle folder names to float stage labels
KAGGLE_STAGE_MAP = {
    "stage_i": 1.0,
    "stage_ii": 2.0,
    "stage_iii": 3.0,
    "stage_iv": 4.0,
}

# Folders to exclude (no clear stage mapping)
EXCLUDED_FOLDERS = {"sdti", "unstageable", "invalid"}


class KaggleConverter(DataSourceConverter):
    """Converter for Kaggle Pressure Ulcer Stages dataset.

    Dataset structure:
        data/raw/kaggle/Dataset/
        ├── Stage_I/      -> 1.0
        ├── Stage_II/     -> 2.0
        ├── Stage_III/    -> 3.0
        ├── Stage_IV/     -> 4.0
        ├── SDTI/         -> excluded
        ├── Unstageable/  -> excluded
        └── Invalid/      -> excluded
    """

    @property
    def source_name(self) -> str:
        return "kaggle"

    def _get_dataset_dir(self) -> Path:
        """Get the Dataset subdirectory."""
        dataset_dir = self.raw_dir / "Dataset"
        if dataset_dir.exists():
            return dataset_dir
        return self.raw_dir

    def list_images(self) -> list[Path]:
        """List all images in Stage_I through Stage_IV folders."""
        images = []
        dataset_dir = self._get_dataset_dir()

        for folder in dataset_dir.iterdir():
            if not folder.is_dir():
                continue

            folder_name = folder.name.lower().replace(" ", "_")

            # Skip excluded folders
            if folder_name in EXCLUDED_FOLDERS:
                continue

            # Only include stage folders
            if folder_name in KAGGLE_STAGE_MAP:
                images.extend(list_images(folder, recursive=False))

        return sorted(images)

    def get_stage(self, image_path: Path) -> Optional[float]:
        """Extract stage from parent folder name.

        Args:
            image_path: Path to image file

        Returns:
            Float stage (1.0-4.0) or None if not in a stage folder
        """
        folder_name = image_path.parent.name.lower().replace(" ", "_")
        return KAGGLE_STAGE_MAP.get(folder_name)

    def get_notes(self, image_path: Path) -> str:
        """Get notes indicating the source folder."""
        folder_name = image_path.parent.name
        return f"kaggle:{folder_name}"

    def should_include(self, image_path: Path) -> bool:
        """Only include images from Stage_I through Stage_IV folders."""
        folder_name = image_path.parent.name.lower().replace(" ", "_")
        return folder_name in KAGGLE_STAGE_MAP
