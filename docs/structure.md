# Project Structure

> Overview of directories, modules, and file organization.

**Parent:** [MAIN.md](../MAIN.md)

---

## Directory Layout

```
wound_classifier/
├── src/wound_classifier/       # Main package
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point (planned)
│   ├── data/                   # Data processing ✅
│   │   ├── base.py             # DataSourceConverter ABC, ImageRecord
│   │   ├── utils.py            # Image utilities
│   │   ├── pipeline.py         # DataPipeline orchestrator
│   │   └── converters/         # Source-specific converters
│   │       ├── kaggle.py
│   │       ├── medetec.py
│   │       └── figshare.py
│   ├── models/                 # Model architectures (planned)
│   ├── training/               # Training loop (planned)
│   ├── inference/              # Prediction (planned)
│   └── server/                 # API server (planned)
│
├── data/
│   ├── raw/                    # Original datasets (git-ignored)
│   │   ├── kaggle/
│   │   ├── medetec/
│   │   └── figshare/
│   ├── processed/              # Preprocessed images (git-ignored)
│   │   ├── labeled/
│   │   │   ├── stage_1/
│   │   │   ├── stage_2/
│   │   │   ├── stage_3/
│   │   │   └── stage_4/
│   │   └── unlabeled/
│   └── metadata/
│       └── sources.csv         # Image provenance tracking
│
├── configs/                    # Configuration files (planned)
│   ├── train.yaml
│   └── model.yaml
│
├── checkpoints/                # Saved model weights (git-ignored)
│
├── notebooks/                  # Jupyter experiments
│
├── tests/                      # Test suite
│
├── docs/                       # Documentation
│   ├── data.md
│   ├── data/
│   │   ├── sources.md
│   │   └── pipeline.md
│   ├── design.md
│   └── structure.md            # (this file)
│
├── MAIN.md                     # Documentation hub
├── README.md                   # Project overview
├── pyproject.toml              # Package configuration
├── requirements.txt            # Dependencies
└── .gitignore
```

---

## Module Descriptions

### `data/` ✅ Complete
- **Purpose:** Data loading, preprocessing, and pipeline
- **Key classes:** `DataSourceConverter`, `ImageRecord`, `DataPipeline`
- **Entry point:** `python -m wound_classifier.data.pipeline`

### `models/` (Planned)
- **Purpose:** Neural network architectures
- **Will contain:** ResNet/EfficientNet wrappers for wound classification

### `training/` (Planned)
- **Purpose:** Training loop and utilities
- **Will contain:** Trainer class, loss functions, metrics, callbacks

### `inference/` (Planned)
- **Purpose:** Model loading and prediction
- **Will contain:** Predictor class for single/batch inference

### `server/` (Planned)
- **Purpose:** REST API for production deployment
- **Will contain:** FastAPI application with `/predict` endpoint

### `cli.py` (Planned)
- **Purpose:** Command-line interface
- **Subcommands:** `train`, `predict`, `serve`

---

## Configuration Files

### `configs/train.yaml` (Planned)
```yaml
model:
  architecture: resnet18
  pretrained: true

training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001

data:
  image_size: 224
  augmentation: true
```

---

*Last updated: 2025-02-25*
