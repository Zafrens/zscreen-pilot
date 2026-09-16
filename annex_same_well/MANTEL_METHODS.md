# Control-mean image/RNA correspondence

The [result table](evidence/mantel_bootstrap.csv) quantifies agreement between image and RNA response patterns across **35 controls measured in 11,435 wells**. The observed correlation is **0.772892**; the two-sided permutation p value is **0.00049975**.

## Recompute with the included data

From the package root:

```text
python annex_same_well/recompute_mantel.py --check
```

The script reads [same_well_wells.parquet](same_well_wells.parquet), recomputes the statistic, runs 2,000 permutations and 500 replicates of each bootstrap, and checks all seven result columns against the included table. It uses NumPy, pandas, SciPy and the package's Parquet reader. Use `--output result.csv` to save a separate result. No network access or fitted prediction model is required.

## Statistic and settings

1. Sort wells by `batch_id`, `well_id` and `public_compound_id`.
2. Convert the 448 image coordinates and 32 native RNA coordinates D00–D31 to float64. Z-score each coordinate across all wells using population SD (`ddof=0`).
3. Average standardized well vectors within each control, in sorted control-name order, yielding 35 image means and 35 RNA means.
4. Compute **correlation distance**, `1 − Pearson r`, between every pair of control-mean vectors within each modality.
5. Calculate Pearson correlation between the 595 corresponding distances.

The value answers whether controls with similar mean image profiles also have similar mean RNA profiles. It does not measure per-well prediction accuracy or direct target engagement.

Randomization uses one `numpy.random.default_rng(0)` stream, consumed in this order: permutations, control bootstrap, within-control well bootstrap. Each coordinate's scaling stays fixed during resampling.

The permutation test shuffles image control-mean identities relative to RNA means 2,000 times. Its two-sided p value is `(1 + count(abs(r_null) >= abs(r_observed))) / 2001`.

Both bootstrap procedures use 500 replicates and 2.5th/97.5th percentiles. Their SD uses `ddof=0`.

| `estimate` | Resampled unit | 95% percentile interval | Bootstrap SD |
|---|---|---:|---:|
| `compound_grain_35pairs` | Sample 35 control identities with replacement; reuse those identities in both modalities | 0.687630–0.895368 | 0.054712 |
| `well_powered_mean_of_resampled_wells` | Keep 35 controls fixed; independently sample image wells and RNA wells within each control, preserving its well count, then recompute means | 0.710930–0.777589 | 0.016643 |

**The second procedure uses separate image and RNA sample indices. It is not a paired-well bootstrap.** It conditions on the measured control identities; the first varies the control population. Their interval-width or SD ratio does not identify a benefit caused by exact pairing. The intervals also reflect finite Monte Carlo sampling at the stated seed and replicate count.

## Table schema

[mantel_bootstrap.csv](evidence/mantel_bootstrap.csv) has two rows, keyed by `estimate`:

| Field | Meaning |
|---|---|
| `estimate` | Bootstrap design label |
| `mantel_r` | Observed correlation-distance statistic; identical in both rows |
| `perm_p` | Two-sided permutation p value; identical in both rows |
| `boot_ci_lo`, `boot_ci_hi` | 2.5th and 97.5th percentiles of the corresponding bootstrap statistics |
| `boot_mean`, `boot_std` | Mean and population SD of those bootstrap statistics |
