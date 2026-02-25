# Dataset Sources Research

> Research and evaluation of publicly available pressure wound/ulcer image datasets.

**Parent:** [data.md](../data.md)

---

## Focus Area

**Primary focus: Pressure Wounds (Pressure Ulcers / Bedsores / Decubitus Ulcers)**

---

## Search Criteria

- **Content:** Pressure wound/ulcer images
- **Labels:** Stage classification (I-IV), tissue type, severity
- **Format:** Image files (JPEG, PNG) with annotations
- **License:** Research-friendly (CC, academic use permitted)
- **Size:** Minimum ~500+ images preferred for deep learning

---

## Candidate Datasets

### 1. Kaggle - Pressure Ulcer Stages ✅ DOWNLOADED
| Attribute | Details |
|-----------|---------|
| Source | Kaggle (sinemgokoz) |
| URL | https://www.kaggle.com/datasets/sinemgokoz/pressure-ulcers-stages |
| Size | 258 images (155MB) |
| Labels | Stage I (28), II (53), III (46), IV (32), SDTI (23), Unstageable (29), Invalid (47) |
| License | Apache 2.0 |
| Format | JPG/PNG organized by stage folders |
| Notes | Primary dataset - has stage labels ready to use |

### 2. Medetec Wound Database ✅ DOWNLOADED
| Attribute | Details |
|-----------|---------|
| Source | Medetec (via GitHub mirror) |
| URL | https://github.com/mlaradji/deep-learning-for-wound-care |
| Size | 214 pressure ulcer images |
| Labels | None (requires manual labeling) |
| License | Copyright-free stock images |
| Format | JPG/PNG (various sizes) |
| Notes | Downloaded from GitHub; needs stage labeling before use |

### 3. Pressure Injury Image Dataset (PIID)
| Attribute | Details |
|-----------|---------|
| Source | Academic research |
| URL | Referenced in [ResearchGate](https://www.researchgate.net/figure/Example-images-from-the-PIID-dataset_fig2_360382131) |
| Size | 1,091 images |
| Labels | Stages I-IV with ground-truth annotations |
| License | Academic use |
| Format | Smartphone-captured images |
| Notes | Expert-annotated; achieved 85% accuracy in classification studies |

### 4. Figshare Pressure Ulcer Dataset ✅ DOWNLOADED
| Attribute | Details |
|-----------|---------|
| Source | Figshare |
| URL | https://figshare.com/articles/dataset/images_of_pressure_ulcer_2_/17206940 |
| Size | 20 images + 20 JSON annotations |
| Labels | Segmentation masks (Labelme format) - healing, sloughy, undermining |
| License | CC BY 4.0 |
| Format | JPG + JSON (Labelme) |
| Notes | Small but includes segmentation annotations; useful for future segmentation tasks |

### 5. UWM Wound Dataset
| Attribute | Details |
|-----------|---------|
| Source | University of Wisconsin-Milwaukee / AZH Wound Center |
| URL | https://github.com/uwm-bigdata/wound-classification-using-images-and-locations |
| Size | 1,109 foot ulcer images from 889 patients |
| Labels | 4 wound types: venous, diabetic, pressure, surgical |
| License | Academic/Research |
| Format | Images + location data |
| Notes | Multi-modal (image + body location); labeled by wound specialists |

### 6. Chronic Wounds Database (CW-DB)
| Attribute | Details |
|-----------|---------|
| Source | Academic |
| URL | https://chronicwounddatabase.eu |
| Size | 188 image sets from 79 patient visits |
| Labels | Manual wound outlines by experts |
| License | Research use |
| Format | Photos, thermal images, 3D meshes (coregistered) |
| Notes | Multimodal - includes thermal and 3D data |

---

## Dataset Comparison

| Dataset | Images | Pressure-Specific | Stage Labels | License | Status |
|---------|--------|-------------------|--------------|---------|--------|
| Kaggle Pressure Ulcer Stages | 258 | Yes | Yes (I-IV + extras) | Apache 2.0 | ✅ Downloaded |
| Medetec | 214 | Yes | No | Free | ✅ Downloaded |
| Figshare | 20 | Yes | Segmentation | CC BY 4.0 | ✅ Downloaded |
| PIID | 1,091 | Yes | Yes (I-IV) | Academic | Not downloaded |
| UWM Wound | 1,109 | Partial | Type only | Academic | Not downloaded |
| CW-DB | 188 sets | Mixed | No | Research | Not downloaded |

### Total Downloaded: 492 images (+ 20 segmentation annotations)

---

## Key Findings

### Challenges
- Limited large-scale public datasets for pressure ulcers specifically
- Many studies use private/hospital datasets (privacy concerns)
- Recommended: 150+ images per stage for reasonable accuracy
- Labeling variability among experts is a known issue

### Recommendations
1. **Start with Kaggle Pressure Ulcer Stages** - easiest access
2. **Supplement with Medetec** - free, well-documented
3. **Consider Figshare** - CC BY 4.0 license is permissive
4. **UWM dataset** if multi-modal approach is desired

---

## Sources Checked

- [x] Kaggle
- [x] HuggingFace (no specific pressure wound datasets found)
- [x] Papers With Code / Academic papers
- [x] GitHub repositories
- [x] Figshare
- [x] Medetec
- [ ] PhysioNet
- [ ] Grand Challenge

---

## Research Log

### 2025-02-25
- Created documentation structure
- Completed initial dataset search
- Focus narrowed to pressure wounds specifically
- Identified 6 candidate datasets
- Key finding: Kaggle has dedicated pressure ulcer stages dataset
- Downloaded 3 datasets:
  - Kaggle: 258 images with stage labels (I-IV + SDTI, Unstageable, Invalid)
  - Medetec: 214 images (no labels)
  - Figshare: 20 images with segmentation annotations
- Total: 492 images available for training
- Implemented data pipeline with interface-based converter architecture
- Standardized labels to continuous float scale (0.0-4.0)
- Label mappings:
  - Kaggle: Direct stage mapping (Stage_I→1.0, Stage_II→2.0, etc.)
  - Medetec: Heuristic mapping (sloughy→3.25, undermining→3.5, etc.)
  - Figshare: Heuristic mapping from filenames

---

## References

- [YOLO-Based Deep Learning Model for Pressure Ulcer Detection](https://www.mdpi.com/2227-9032/11/9/1222)
- [Deep learning approach for automatic pressure ulcer diagnosis](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0264139)
- [Multi-modal wound classification using wound image and location](https://www.nature.com/articles/s41598-022-21813-0)
- [Pressure Ulcer Categorisation using Deep Learning (arXiv)](https://arxiv.org/pdf/2203.06248)

---

*Last updated: 2025-02-25*
