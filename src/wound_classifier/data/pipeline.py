"""Data pipeline for processing wound images from multiple sources."""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from tqdm import tqdm

from .base import DataSourceConverter, ImageRecord
from .utils import resize_image, get_image_info, is_valid_image


@dataclass
class ProcessingReport:
    """Report of pipeline processing results."""
    total_images: int = 0
    processed: int = 0
    labeled: int = 0
    unlabeled: int = 0
    skipped: int = 0
    errors: int = 0
    by_source: dict = field(default_factory=dict)
    by_stage: dict = field(default_factory=dict)
    error_messages: list = field(default_factory=list)

    def __str__(self) -> str:
        lines = [
            "=" * 50,
            "Data Pipeline Processing Report",
            "=" * 50,
            f"Total images found: {self.total_images}",
            f"Successfully processed: {self.processed}",
            f"  - Labeled: {self.labeled}",
            f"  - Unlabeled: {self.unlabeled}",
            f"Skipped: {self.skipped}",
            f"Errors: {self.errors}",
            "",
            "By Source:",
        ]
        for source, count in self.by_source.items():
            lines.append(f"  - {source}: {count}")

        lines.append("")
        lines.append("By Stage:")
        for stage, count in sorted(self.by_stage.items()):
            lines.append(f"  - {stage}: {count}")

        if self.error_messages:
            lines.append("")
            lines.append(f"First {min(5, len(self.error_messages))} errors:")
            for msg in self.error_messages[:5]:
                lines.append(f"  - {msg}")

        lines.append("=" * 50)
        return "\n".join(lines)


class DataPipeline:
    """Pipeline for processing wound images from multiple data sources.

    Converts raw images from various sources into a standardized format
    with consistent sizing, format, and metadata tracking.
    """

    def __init__(
        self,
        raw_dir: Path,
        processed_dir: Path,
        metadata_path: Path,
        target_size: tuple[int, int] = (224, 224),
    ):
        """Initialize the data pipeline.

        Args:
            raw_dir: Root directory containing raw data sources
            processed_dir: Directory for processed output
            metadata_path: Path to metadata CSV file
            target_size: Target image dimensions (width, height)
        """
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.metadata_path = Path(metadata_path)
        self.target_size = target_size

        self._converters: list[DataSourceConverter] = []
        self._records: list[ImageRecord] = []

    def register(self, converter: DataSourceConverter) -> None:
        """Register a data source converter.

        Args:
            converter: DataSourceConverter instance
        """
        self._converters.append(converter)

    def _setup_directories(self) -> None:
        """Create output directory structure."""
        # Labeled stage folders
        for i in range(1, 5):
            (self.processed_dir / "labeled" / f"stage_{i}").mkdir(
                parents=True, exist_ok=True
            )

        # Unlabeled folder
        (self.processed_dir / "unlabeled").mkdir(parents=True, exist_ok=True)

        # Metadata directory
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

    def _generate_filename(self, source: str, index: int, original: str) -> str:
        """Generate standardized filename.

        Args:
            source: Source identifier
            index: Image index within source
            original: Original filename

        Returns:
            Standardized filename like 'kaggle_001.jpg'
        """
        return f"{source}_{index:04d}.jpg"

    def run(
        self,
        include_unlabeled: bool = True,
        skip_existing: bool = True,
        show_progress: bool = True,
    ) -> ProcessingReport:
        """Run the pipeline to process all registered sources.

        Args:
            include_unlabeled: Include images without labels
            skip_existing: Skip images that already exist in output
            show_progress: Show progress bar

        Returns:
            ProcessingReport with results
        """
        self._setup_directories()
        report = ProcessingReport()
        self._records = []

        # Collect all images from all converters
        all_images = []
        for converter in self._converters:
            images = converter.list_images()
            report.by_source[converter.source_name] = 0
            for img in images:
                if converter.should_include(img):
                    all_images.append((converter, img))

        report.total_images = len(all_images)

        # Process images
        source_counters = {c.source_name: 0 for c in self._converters}

        iterator = tqdm(all_images, desc="Processing images") if show_progress else all_images

        for converter, image_path in iterator:
            try:
                # Get stage label
                stage = converter.get_stage(image_path)

                # Skip unlabeled if not requested
                if stage is None and not include_unlabeled:
                    report.skipped += 1
                    continue

                # Validate image
                if not is_valid_image(image_path):
                    report.skipped += 1
                    continue

                # Generate output filename
                source_counters[converter.source_name] += 1
                new_filename = self._generate_filename(
                    converter.source_name,
                    source_counters[converter.source_name],
                    image_path.name
                )

                # Determine output directory
                if stage is not None:
                    # Round to nearest stage for folder
                    rounded_stage = max(1, min(4, round(stage)))
                    output_dir = self.processed_dir / "labeled" / f"stage_{rounded_stage}"
                else:
                    output_dir = self.processed_dir / "unlabeled"

                output_path = output_dir / new_filename

                # Skip if exists
                if skip_existing and output_path.exists():
                    # Still record it
                    width, height, _ = get_image_info(output_path)
                    record = ImageRecord(
                        filename=new_filename,
                        original_source=converter.source_name,
                        original_filename=image_path.name,
                        original_path=image_path,
                        stage=stage,
                        width=width,
                        height=height,
                        notes=converter.get_notes(image_path)
                    )
                    self._records.append(record)
                    report.processed += 1
                    if stage is not None:
                        report.labeled += 1
                        stage_key = f"stage_{max(1, min(4, round(stage)))}"
                        report.by_stage[stage_key] = report.by_stage.get(stage_key, 0) + 1
                    else:
                        report.unlabeled += 1
                        report.by_stage["unlabeled"] = report.by_stage.get("unlabeled", 0) + 1
                    report.by_source[converter.source_name] += 1
                    continue

                # Process image
                width, height = resize_image(
                    image_path,
                    output_path,
                    self.target_size
                )

                # Create record
                record = ImageRecord(
                    filename=new_filename,
                    original_source=converter.source_name,
                    original_filename=image_path.name,
                    original_path=image_path,
                    stage=stage,
                    width=width,
                    height=height,
                    notes=converter.get_notes(image_path)
                )
                self._records.append(record)

                # Update report
                report.processed += 1
                report.by_source[converter.source_name] += 1

                if stage is not None:
                    report.labeled += 1
                    stage_key = f"stage_{max(1, min(4, round(stage)))}"
                    report.by_stage[stage_key] = report.by_stage.get(stage_key, 0) + 1
                else:
                    report.unlabeled += 1
                    report.by_stage["unlabeled"] = report.by_stage.get("unlabeled", 0) + 1

            except Exception as e:
                report.errors += 1
                report.error_messages.append(f"{image_path}: {e}")

        # Write metadata CSV
        self._write_metadata()

        return report

    def _write_metadata(self) -> None:
        """Write metadata CSV file."""
        fieldnames = [
            "filename", "original_source", "original_filename",
            "stage", "width", "height", "verified", "notes"
        ]

        with open(self.metadata_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in self._records:
                writer.writerow(record.to_csv_row())

    @property
    def records(self) -> list[ImageRecord]:
        """Get all processed image records."""
        return self._records


def create_default_pipeline(
    project_root: Path,
    target_size: tuple[int, int] = (224, 224),
) -> DataPipeline:
    """Create a pipeline with all default converters.

    Args:
        project_root: Root directory of the project
        target_size: Target image dimensions

    Returns:
        Configured DataPipeline instance
    """
    from .converters import KaggleConverter, MedetecConverter, FigshareConverter

    raw_dir = project_root / "data" / "raw"
    processed_dir = project_root / "data" / "processed"
    metadata_path = project_root / "data" / "metadata" / "sources.csv"

    pipeline = DataPipeline(
        raw_dir=raw_dir,
        processed_dir=processed_dir,
        metadata_path=metadata_path,
        target_size=target_size,
    )

    # Register converters
    if (raw_dir / "kaggle").exists():
        pipeline.register(KaggleConverter(raw_dir / "kaggle"))

    if (raw_dir / "medetec").exists():
        pipeline.register(MedetecConverter(raw_dir / "medetec"))

    if (raw_dir / "figshare").exists():
        pipeline.register(FigshareConverter(raw_dir / "figshare"))

    return pipeline


if __name__ == "__main__":
    # Run pipeline from command line
    import sys

    project_root = Path(__file__).parent.parent.parent.parent
    pipeline = create_default_pipeline(project_root)

    print("Running data pipeline...")
    report = pipeline.run(include_unlabeled=True)
    print(report)
