# Gallery data guide

| Path | Unit and use |
|---|---|
| `config.json` | Frozen panel, thresholds, marker columns, RNA context, and display percentiles. |
| `data/fov_metadata.parquet` | Public metadata for all 10,661 ZS13 source crops; public compound/component IDs and QC flags. |
| `data/crop_marker_intensities.parquet` | Per-crop segmentation counts and mean marker intensities for the same panel; joined by panel and HDF5 row index. |
| `data/source_channels.csv` | Source channel index and measured stain names. |
| `data/ZS13_crop_02208.npy`, `data/ZS13_crop_09607.npy` | Preserved float32 measured channel arrays, each `(5, 340, 340)`, selected by the frozen rule. |
| `data/raw_crop_registry.json` | Source shape, crop identity, exact-value and file hashes; unspecified image cell line remains null. |
| `evidence/family_selection_scores.csv` | All component families considered, family support, response norm and eligibility. |
| `evidence/selected_family_distribution.csv` | Every measured member of both selected families, response distance/norm, crop count, eligibility and chosen flag. |
| `evidence/representative_crop_candidates.csv` | Every valid crop for each chosen compound, marker means, segmented-cell count and median-distance score. |
| `evidence/selected_examples.csv` | The two final public compounds, components, crop indices and quantitative selection scores. |
| `evidence/linked_programs.csv` | All 32 raw and standardized selected-compound usages, standardized family medians, and context centers/scales. |
| `evidence/display_scaling.csv` | Common lower/upper grayscale limits for each of five channels. |
| `evidence/figures/` | PNG and editable-text SVG of measured microscopy channels and linked RNA profiles. |

These exported tables contain public identifiers. The gallery provides crop arrays and the full ZS13 metadata/marker tables needed to audit its selection; it does not expand the other imaging panels into a complete raw-image archive.
