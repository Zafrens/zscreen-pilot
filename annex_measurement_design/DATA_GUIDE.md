# Measurement-design evidence

The files below describe measured results, fixed sample identities and the settings used in the comparisons. [Methods](METHODS.md) defines preprocessing, endpoints and sampling units.

| Files | Unit and use |
|---|---|
| `evidence/pairing_summary.csv` | Per training-size and pairing-arm summaries used in the figure. Correlations/R² are means over native RNA coordinates. |
| `evidence/pairing_results.csv` | Each completed exact/shuffled fit, with seed, training size and test metrics. |
| `evidence/pairing_coordinate_results.csv` | Per-fit, per-native-RNA-coordinate prediction results. |
| `evidence/pairing_well_split.csv` | Fixed train/test membership, keyed by batch and well. |
| `evidence/pairing_training_samples.csv` | Saved training selections for each size and seed. |
| `evidence/pairing_group_counts.csv` | Control/batch counts in the comparison arms. |
| `evidence/batch_contexts.csv` | Controls and batch support by cell context. |
| `evidence/batch_partitions.csv`, `batch_subsets.csv` | Fixed acquisition/reference partitions and enumerated acquisition subsets. |
| `evidence/batch_accumulation_summary.csv` | Per-context, split-seed and acquisition-size summaries. The main accumulation figure and README table use `split_seed=20260915`; the sensitivity figure uses all 20 seeds, `20260915`–`20260934`. The README endpoint ranges use `mean_median_gene_pearson` at the largest acquisition size for each context. |
| `evidence/batch_accumulation_results.csv` | Per-subset gene/program agreement. |
| `evidence/batch_accumulation_per_control.csv` | Per-control agreement within each subset/partition. |

The fourth figure uses the [same-well learning-curve table](../annex_same_well/evidence/learning_curve.csv). Its horizontal axis is total sampled cross-validation dataset wells, not training wells per fold.

**Coordinate systems:** pairing targets are native RNA encoder coordinates D00–D31; the control program projections are core P01–P32. They both have 32 columns but are different representations.

**Sampling units:** pairing fits hold out wells within two measured batches. Accumulation compares disjoint batch sets. Repeated random starts and overlapping batch partitions are computational sensitivity checks, not new experimental replicates.

[analysis_settings.json](analysis_settings.json) contains the pairing and batch-accumulation settings. All file references in this guide point to data included in this package.
