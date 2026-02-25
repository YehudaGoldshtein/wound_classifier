# Data Documentation

> Documentation for datasets, data sources, and data pipeline decisions.

**Parent:** [MAIN.md](../MAIN.md)

---

## Subsections

### [Dataset Sources](data/sources.md)
Research and evaluation of available wound image datasets.

### [Dataset Selection](data/selection.md)
Final dataset choices and rationale.

### [Data Pipeline](data/pipeline.md)
Preprocessing, augmentation, and loading implementation.

---

## Focus

**Pressure Wounds** (Pressure Ulcers / Bedsores / Decubitus Ulcers)

## Label Standardization

All labels are standardized to a **continuous float scale (0.0 - 4.0)**:

| Value | Meaning |
|-------|---------|
| 0.0 | Healthy/healed skin |
| 1.0 | Stage I (non-blanchable erythema) |
| 2.0 | Stage II (partial thickness skin loss) |
| 3.0 | Stage III (full thickness, fat visible) |
| 4.0 | Stage IV (full thickness, bone/tendon visible) |
| 2.5 | Example: borderline Stage II/III |
| None | Unlabeled/unknown |

**Rationale:** Wound severity is fundamentally continuous (color, depth, tissue composition). Float labels enable regression-based models that capture the true biological nature of wound progression.

---

## Requirements

- [x] Pressure wound images with stage classification labels (I-IV)
- [ ] Sufficient volume for training (150+ images per stage recommended)
- [x] Permissive licensing for research/development
- [ ] Quality annotations by medical professionals

---

## Status

| Phase | Status |
|-------|--------|
| Source Research | Complete |
| Data Download | Complete (492 images) |
| Pipeline Implementation | Complete |
| Data Processing | Ready to run |

## Current Data

| Source | Images | Labels | Notes |
|--------|--------|--------|-------|
| Kaggle | 258 | Stage I-IV (1.0-4.0) | Direct folder-based labels |
| Medetec | 214 | Heuristic (3.25-3.5) or None | Filename-based heuristics |
| Figshare | 20 | Heuristic or None | Has segmentation masks |
| **Total** | **492** | | |

## Output Structure

```
data/processed/
├── labeled/
│   ├── stage_1/    # 0.5 ≤ label < 1.5
│   ├── stage_2/    # 1.5 ≤ label < 2.5
│   ├── stage_3/    # 2.5 ≤ label < 3.5
│   └── stage_4/    # 3.5 ≤ label ≤ 4.0
└── unlabeled/      # label = None
```

---

*Last updated: 2025-02-25*
