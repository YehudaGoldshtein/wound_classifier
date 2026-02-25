# Wound Image Classification

A deep learning project for classifying wound images.

## Project Structure

```
wound_classifier/
├── src/wound_classifier/   # Source code
├── tests/                  # Unit tests
├── data/
│   ├── train/              # Training images (organized by class)
│   └── val/                # Validation images (organized by class)
├── checkpoints/            # Saved model weights
├── configs/                # Configuration files
├── notebooks/              # Jupyter notebooks
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Data Organization

Place images in class-specific subdirectories:
```
data/train/
├── class_1/
│   ├── image1.jpg
│   └── image2.jpg
├── class_2/
│   └── ...
```
