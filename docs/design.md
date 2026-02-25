# Design & Architecture

> Architectural decisions, design patterns, and system design rationale.

**Parent:** [MAIN.md](../MAIN.md)

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   1. TRAIN (offline)                                        │
│   python -m wound_classifier train --config train.yaml      │
│                         │                                   │
│                         ▼                                   │
│              checkpoints/best.pth                           │
│                         │                                   │
│   ──────────────────────┼───────────────────────────────    │
│                         │                                   │
│   2. SERVE (production) │                                   │
│   python -m wound_classifier serve --checkpoint best.pth    │
│                         │                                   │
│                         ▼                                   │
│              ┌─────────────────┐                            │
│              │  REST API       │                            │
│              │  POST /predict  │ ◄── { image: base64 }      │
│              │                 │ ──► { stage: 2.7 }         │
│              └─────────────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## CLI Modes

The application uses a single entry point with subcommands:

### `train` - Model Training
```bash
python -m wound_classifier train --config configs/train.yaml
python -m wound_classifier train --epochs 100 --batch-size 32
```
- Loads training data from `data/processed/`
- Trains model with specified configuration
- Saves checkpoints to `checkpoints/`
- Outputs training metrics and logs

### `predict` - CLI Prediction
```bash
python -m wound_classifier predict --checkpoint checkpoints/best.pth --image wound.jpg
python -m wound_classifier predict --checkpoint checkpoints/best.pth --dir images/
```
- Loads trained model from checkpoint
- Runs inference on single image or directory
- Outputs predicted stage (0.0-4.0) with confidence
- Useful for testing and debugging

### `serve` - API Server
```bash
python -m wound_classifier serve --checkpoint checkpoints/best.pth --port 8000
```
- Starts REST API server (FastAPI)
- Endpoints:
  - `POST /predict` - Accept image, return stage prediction
  - `GET /health` - Health check
- Production deployment mode

---

## Project Structure

```
src/wound_classifier/
├── __init__.py
├── cli.py              # Entry point with subcommands
├── data/               # Data loading and preprocessing ✅
│   ├── base.py
│   ├── utils.py
│   ├── pipeline.py
│   └── converters/
├── models/             # Model architectures
│   ├── __init__.py
│   └── resnet.py       # or efficientnet.py
├── training/           # Training infrastructure
│   ├── __init__.py
│   ├── trainer.py      # Training loop
│   ├── losses.py       # Loss functions
│   └── metrics.py      # Evaluation metrics
├── inference/          # Prediction utilities
│   ├── __init__.py
│   └── predictor.py
└── server/             # API server
    ├── __init__.py
    └── app.py          # FastAPI application
```

---

## Design Decisions

### 1. Continuous Labels (0.0-4.0)

**Decision:** Use float labels instead of discrete classes.

**Rationale:**
- Wound severity is biologically continuous
- Enables regression-based models
- Captures borderline cases (e.g., 2.5 = between Stage II and III)
- More nuanced predictions for clinical use

### 2. Interface-Based Data Pipeline

**Decision:** Abstract `DataSourceConverter` interface with concrete implementations.

**Rationale:**
- Easy to add new data sources
- Each source has different labeling schemes
- Testable and maintainable
- Follows Open/Closed principle

### 3. Single Project with CLI Modes

**Decision:** One project with `train`, `predict`, `serve` subcommands.

**Rationale:**
- Shared code (models, data loading)
- Single codebase to maintain
- Standard pattern in ML projects
- Checkpoint file links training to inference

### 4. Configuration-Driven Training

**Decision:** YAML config files for training parameters.

**Rationale:**
- Reproducible experiments
- Easy to version control configs
- Override via CLI when needed
- Separate code from hyperparameters

---

## Data Flow

### Training
```
data/raw/ → DataPipeline → data/processed/ → DataLoader → Model → checkpoints/
```

### Inference
```
image → Predictor(checkpoint) → stage (0.0-4.0)
```

### API
```
HTTP POST /predict → image decode → Predictor → JSON response
```

---

*Last updated: 2025-02-25*
