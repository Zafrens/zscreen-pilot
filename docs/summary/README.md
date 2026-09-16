# Z-Screen pilot in brief

Z-Screen links public chemical recipes to cellular responses. The pilot contains **190,699 compound-context profiles**, **162,914 recipes**, **eight library–cell contexts**, and RNA representations on **6,000 genes and 32 shared transcriptional programs**.

The reusable package includes processed matrices and aligned identifiers, three reference-model checkpoints with inference code, four worked notebooks, and controls, imaging and same-well measurements. Selected annexes help readers explore chemical families, inspect hypotheses and understand measurement utility.

The retained HSPA5 example illustrates a coherent family-level response. Its genetic resemblance is a mechanism hypothesis, and its retrospective selection curves measure recovery of a fixed RNA-response score. Additional upstream analyses require the inputs identified in their methods. [Analysis and access note](../ANALYSIS_ACCESS.md).

## Quantitative results at a glance

| Result | Recorded evaluation |
|---|---|
| Recipe-to-program prediction | Mean per-program Pearson 0.105–0.530; permutation-null z = 6.1–28.1 across eight contexts |
| Pinned fold-0 baselines | Best simple model and three-seed transformer each lead in four of eight contexts |
| Held-out building blocks | Structure-input model r = 0.339 ± 0.020 in `zel024_hek293`; retrospective evaluation |
| Image-to-program prediction | Saved-row means: 0.1360 for `clip_ridge` in `zel024_hek293`; 0.1342 for `mean448_mlp` in `zel039_aec7` |
| Chemistry-constrained atlas | 1,007 families; 855 with significant pathway annotations; explicit member/centroid exports |
| Nominal design capacity | 2,095,149 library-grid × context states versus 190,699 measured profiles; not a synthesis-feasibility assertion |

**Continue with:** [the data and model overview](../../README.md), [Start Here](../../START_HERE.md), [the scientific overview](../SCIENTIFIC_OVERVIEW.md), or [the annex index](../ANNEX_INDEX.md).
