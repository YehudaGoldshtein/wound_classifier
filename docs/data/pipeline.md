# Data Pipeline

> Documentation for data preprocessing, multi-source integration, and data loading.

**Parent:** [data.md](../data.md)

---

## Label Standardization

All labels use a **continuous float scale (0.0 - 4.0)**:

| Value | Meaning |
|-------|---------|
| 0.0 | Healthy/healed skin |
| 1.0 | Stage I (non-blanchable erythema) |
| 2.0 | Stage II (partial thickness skin loss) |
| 3.0 | Stage III (full thickness, fat visible) |
| 4.0 | Stage IV (full thickness, bone/tendon visible) |
| None | Unlabeled/unknown |

**Intermediate values allowed** (e.g., 2.5 = borderline Stage II/III)

---

## Architecture

### Interface-Based Design

```
src/wound_classifier/data/
├── base.py              # ImageRecord, DataSourceConverter ABC
├── utils.py             # Image processing utilities
├── converters/
│   ├── kaggle.py        # KaggleConverter (1.0-4.0 labels)
│   ├── medetec.py       # MedetecConverter (heuristic labels)
│   └── figshare.py      # FigshareConverter (heuristic labels)
└── pipeline.py          # DataPipeline orchestrator
```

### DataSourceConverter Interface

```python
class DataSourceConverter(ABC):
    @property
    def source_name(self) -> str: ...      # e.g., "kaggle"
    @property
    def raw_dir(self) -> Path: ...         # Path to raw data
    def list_images(self) -> list[Path]: ... # List all images
    def get_stage(self, path) -> float | None: ... # Get label (0.0-4.0)
    def get_notes(self, path) -> str: ...  # Labeling method notes
    def should_include(self, path) -> bool: ... # Filter images
```

---

## Label Mappings

### KaggleConverter
| Folder | Float Label | Notes |
|--------|-------------|-------|
| Stage_I | 1.0 | Non-blanchable erythema |
| Stage_II | 2.0 | Partial thickness |
| Stage_III | 3.0 | Full thickness |
| Stage_IV | 4.0 | Full thickness + bone/tendon |
| SDTI | None | Excluded (suspected, unconfirmed) |
| Unstageable | None | Excluded (cannot determine) |
| Invalid | None | Excluded (bad images) |

### MedetecConverter (Heuristic)
| Filename Pattern | Float Label | Rationale |
|------------------|-------------|-----------|
| `sloughy-*` | 3.25 | Slough typically Stage III-IV |
| `undermining*` | 3.5 | Undermining = deeper wound |
| `necrotic-*` | 3.75 | Necrotic tissue often Stage IV |
| `eschar-*` | 3.5 | Eschar can be III or IV |
| `granulation-*` | 2.5 | Granulation can appear II-III |
| `healing-*` | None | Unknown original stage |
| Other | None | Requires manual labeling |

### FigshareConverter
| Source | Float Label | Notes |
|--------|-------------|-------|
| JSON annotation | varies | If stage annotation exists |
| `sloughy-*` | 3.25 | Heuristic from filename |
| Other | None | Unlabeled |

---

## Folder Structure

```
data/
├── raw/                        # Original unmodified data
│   ├── kaggle/Dataset/         # Stage_I, Stage_II, etc.
│   ├── medetec/                # Flat image files
│   └── figshare/               # Images + JSON annotations
│
├── processed/
│   ├── labeled/                # Images with known labels
│   │   ├── stage_1/            # 0.5 ≤ label < 1.5
│   │   ├── stage_2/            # 1.5 ≤ label < 2.5
│   │   ├── stage_3/            # 2.5 ≤ label < 3.5
│   │   └── stage_4/            # 3.5 ≤ label ≤ 4.0
│   └── unlabeled/              # Images without labels
│
└── metadata/
    └── sources.csv             # Full provenance tracking
```

---

## Metadata CSV Format

| Column | Type | Description |
|--------|------|-------------|
| filename | str | Processed filename (e.g., `kaggle_0001.jpg`) |
| original_source | str | Source identifier (kaggle/medetec/figshare) |
| original_filename | str | Original filename |
| stage | float | Label (0.0-4.0) or empty if None |
| width | int | Image width in pixels |
| height | int | Image height in pixels |
| verified | bool | Manual verification status |
| notes | str | Labeling method, uncertainty, etc. |

---

## Usage

### Run Pipeline

```python
from pathlib import Path
from wound_classifier.data.pipeline import create_default_pipeline

project_root = Path(".")
pipeline = create_default_pipeline(project_root, target_size=(224, 224))
report = pipeline.run(include_unlabeled=True)
print(report)
```

### Command Line

```bash
python -m wound_classifier.data.pipeline
```

---

## Status

| Step | Status |
|------|--------|
| Folder structure | Complete |
| Download Kaggle | Complete (258 images) |
| Download Medetec | Complete (214 images) |
| Download Figshare | Complete (20 images + annotations) |
| Pipeline implementation | Complete |
| Quality control | Pending |
| Train/Val/Test split | Pending |

---

## Downloaded Data Summary

### Kaggle Pressure Ulcer Stages (258 images)
| Category | Count | Label |
|----------|-------|-------|
| Stage I | 28 | 1.0 |
| Stage II | 53 | 2.0 |
| Stage III | 46 | 3.0 |
| Stage IV | 32 | 4.0 |
| SDTI | 23 | excluded |
| Unstageable | 29 | excluded |
| Invalid | 47 | excluded |
| **Usable** | **159** | |

### Medetec (214 images)
- Heuristic labels based on filename patterns
- ~50-100 may get heuristic labels (sloughy, undermining, etc.)
- Remaining go to unlabeled folder

### Figshare (20 images + 20 JSON annotations)
- Labelme format segmentation annotations
- Heuristic labels from filename patterns

---

*Last updated: 2025-02-25*
