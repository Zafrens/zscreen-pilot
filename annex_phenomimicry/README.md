# Chemical-response correspondence with genetic references

This annex provides processed comparisons between chemical RNA responses
and genetic-perturbation references. It includes the similar-response and
opposing ends of a standardized correspondence score. Both pair tables store
scores oriented toward their own direction, so their positive `best_z` values
have different meanings; see [score semantics](SCORE_SEMANTICS.md). The tables help nominate response families
and follow-up questions, rather than establish compound targets.

The upstream CRISPR matrices are not bundled. [Reference sources](../docs/REFERENCE_SOURCES.md)
and [methods/input access](../docs/ANALYSIS_ACCESS.md) explain how to obtain
the additional inputs for deeper analysis.

## Data layers

**Compound side.** Per-compound device-centered log1p-CP10k profiles at full
46,944-gene width, built pipeline-faithful to `docs/METHODS.md` (median
Pearson ≥ 0.99999 against the released 6,000-gene surfaces in every context),
then per-gene MAD z-scored within each context. 190,699 compound-context
signatures covering 162,914 unique compounds across the 8 contexts.

**CRISPR side.** 43 signature sets from 10 source perturb-seq datasets
(X-Atlas HEK293T/HCT116 genome-wide; Replogle 2022 K562 genome-wide +
essential + RPE1; Nadig 2024 Jurkat/HepG2; Zhu 2025 CD4 T cells, three
stimulation conditions; VCC2025 K562; Jiang 2025 cytokine-pathway panels in
6 lines): ~18.8k unique target genes, ~8M perturbed cells. Each KO signature
is the per-target mean log-expression change against that dataset's own
non-targeting controls, per-gene MAD z-scored within the dataset, so every
dataset is self-referenced against its internal controls.

## Scoring

Per (context × dataset) pair: cosine similarity between compound and KO
z-profiles over the genes both sides measured (8.2k-25.4k shared genes per
pair), standardized per target within the pair, then a Stouffer consensus
across all 43 datasets weighted by √(shared genes). Inspect each context/dataset contribution as well as the consensus;
reference sets and biological response programs can overlap.
The output is a consensus z-score per compound × target pair per context.

## Tiers

| tier | rule | pairs |
|---|---|---:|
| `B_consensus_strong` | `best_z` ≥ 8 and `n_contexts` ≥ 2 | 101 |
| `B_single_context` | `best_z` ≥ 8 and `n_contexts` = 1 | 24,751 |
| `C_moderate` | z ≥ 5 | 401,609 |

`n_contexts` counts contexts where the compound-target pair entered the
direction-specific top 50. The strong-tier rule does not require
z ≥ 8 in every counted context. These tiers apply to the mimicry table;
the antimimic table has no `tier` column.

`zel039_aec7` compounds cannot accumulate multi-context replication (the
ZEL039 library barely overlaps the other contexts), so their hits cap at
`B_single_context`; judge them on per-dataset evidence in
`showcase_hits.csv` rather than on `n_contexts`.

## Calibration (named controls with curated mechanisms)

The calibration contains **54 control-target pairs**, spanning
34 controls, 43 targets and **2,074 compound × context × dataset queries**.
Each query includes a 1,000-draw random-target empirical p-value
(`p_emp`) and hub-matched comparison (`p_emp_hub`). Queries reuse controls
and reference datasets; their count is not a count of independent experiments.

[Control target annotations](../annotations/README.md) distinguish known
pharmacology from the genetic signatures being compared. The calibration
uses eligible control-target pairs; a response comparison to another gene
is not evidence that it is the control’s direct pharmacological target.

In this set, 100 of 2,074 queries have p≤0.05 and 14 have p≤0.01.
Twenty-six of 54 pairs have at least one p≤0.05 query, and 14 have at least
two. These descriptive counts do not establish panel-wide recovery above
chance. Named comparisons include STC-15/STM2457→METTL3,
GSK126→EZH2 and GCN2-IN-7→EIF2AK4; their support varies by method and context. Inspect their full context/dataset
distributions in `curated_calibration_summary.csv` and
`validation_empirical_p.csv` rather than selecting only their best result.

**Best-of-many inflation:** any statistic that takes a best over many draws
(contexts × datasets) has a null rate far above the nominal percentile.
Judge any single compound × target claim by its per-row empirical p in
`validation_empirical_p.csv`, never by counts of datasets or contexts.

## Ensemble rescoring

A second scorer summarizes two response channels. The `ens_min` score takes, per
compound and query, the minimum rank of two channels run across the 43
knockout signature sets: top-100 signed gene overlap and cosine over 1,172
curated pathway scores (Hallmark + KEGG + Reactome). The 42 scoreable control pairs have a median best
percentile of 0.01864 for `ens_min` and 0.05268 for full-gene cosine.
Twenty-nine of 42 pairs have a best `ens_min` percentile ≤5% (21 for cosine),
and 10 have at least half their queries in the top 20%. These are descriptive
best-of-many summaries; selecting the best channel/query changes the null.
The 10 consistent pairs are:

| compound | target | fraction of queries in top 20% | queries |
|---|---|---:|---:|
| STC-15 | METTL3 | 0.57 | 88 |
| STM2457 | METTL3 | 0.50 | 88 |
| SMARCA ligand 1 | SMARCA4 | 0.51 | 35 |
| N-deshydroxyethyl dasatinib | SRC | 0.57 | 72 |
| GSK126 | EZH2 | 0.50 | 30 |
| BMS-509744 | ITK | 0.72 | 25 |
| ceritinib | ALK | 0.70 | 10 |
| Crizotinib | ALK | 0.50 | 12 |
| endoxifen | ESR1 | 0.60 | 30 |
| GCN2-IN-7 | EIF2AK4 | 0.60 | 30 |

`ensemble_rescoring_panel.csv` contains the 42 retained pairs with both
scores, the fraction of queries in the top 20%, and the consistency flag.
These table summaries do not provide calibrated p-values for selecting the
best query or channel.

## Broad response targets

The strongest convergence in the comparison is not specific biology: several
hundred KO targets (e.g., XRN1, UPF1/2, SMG7, SNRPE, EIF3D; RNA homeostasis
and stress response) are each mimicked by 1-8% of the entire library across
every context. Many compounds, across unrelated chemotypes, push cells into
a generic RNA/stress state. A hit on such a target may reflect a shared RNA/stress response.
The transcriptional comparison alone does not establish cytotoxicity or a
specific target mechanism.
Every target carries a `hub_flag` (`hub_generic_stress` / `frequent` /
`specific`) in `target_hubness.csv` and in the pair tables; the ranked
`top100_phenomimics.csv` excludes `hub_generic_stress` targets, while
targets flagged `frequent` remain in the list (98 of 101 rows). The flags
function as filters rather than deletions; a genuinely RNA-targeting drug
would also hit them.

## SAR structure of the hits

Related recipes with similar reference correspondences form a useful
family-level hypothesis. The relationship is defined by response scores,
not by biochemical activity against the named target.
Families are built per target from the OBOC recipes (bb0-bb4: connect
hitters that match after dropping any one diversity position). The ranked table
(`top100_phenomimics.csv`, 101 hypotheses from 31 families covering 26
targets) keeps only families that pass every guardrail in this annex:
non-hub targets not flagged for weak knockdown, non-promiscuous compounds, and
at least three hitting members and a direct recipe-mate footprint no larger
than 200 library compounds (the cap keeps broad stress-axis chemotypes out).
Families rank by CRISPR-match strength (mean of the
three best member z-scores), log family size, and a replication bonus for
families spanning more than one context. In the recipe-preserving,
degree-weighted null (100 draws; seed 20240611), the full guardrail-filtered
set contains 166 target-specific family clusters versus 108.79 ± 9.44
(mean ± population SD) in the null, whose maximum is 131. These are the
eligible clusters before selecting the 31-family ranked list. The subset
restricted to compound-target pairs present in at least two contexts has
zero eligible clusters in both the observed and null results.
[Saved draws and summaries](family_null_check.csv) and
[method and scope](FAMILY_NULL_METHOD.md) define the comparison. Outside the ranked families, strong non-hub hits are mostly
structural singletons; treat those as a watch-list.

## The reversal track

`antimimic_pairs.parquet` contains the opposing end of the standardized
reference score. The antimimic score multiplies the signed consensus by −1 before
ranking and aggregation. Consequently, **stored `best_z` ≥ 5 corresponds to
signed consensus z ≤ −5** in the strongest retained context. For example,
stored `best_z = 8` means the most negative retained signed consensus is −8.
`mean_z` is also sign-flipped, over the retained contexts; it need not be ≥5.

This is a hypothesis track for follow-up. A negative standardized consensus
does not itself guarantee a negative raw cosine or demonstrate phenotypic
rescue. See [score semantics](SCORE_SEMANTICS.md) for the scoring and aggregation rules. Unlike the mimicry table, it
has neither `tier` nor `bb0`–`bb4`; join [core recipes](../core/recipes.parquet)
on `public_compound_id` when recipe columns are needed.

## Interpretation

- Genetic perturbation and drug treatment differ in extent, timing and
  cellular consequences. Correspondence does not establish direct inhibition.
- Gene-panel mismatch: some datasets measure ~8-9k genes; only shared genes
  enter each pair's score.
- `kd_flag_weak` marks targets whose own-transcript depletion was marginal.
  Their KO signatures may not reflect the intended gene.
- Check `hub_flag` before treating any hit as specific.

## Files

| file | rows | what it is |
|---|---:|---|
| `phenomimic_pairs.parquet` | 426,461 | All mimicry pairs at tier C or better: `public_compound_id`, `target_gene`, `n_contexts`, `contexts`, `best_z`, `mean_z`, `best_rank`, `mean_rank`, `is_named_control`, `kd_delta_median`, `kd_flag_weak`, `tier`, recipe columns `bb0`-`bb4`, `hub_flag`. |
| [antimimic_pairs.parquet](antimimic_pairs.parquet) | 561,355 | Direction-adjusted antimimic scores: stored `best_z` ≥5 corresponds to signed consensus ≤−5. Twelve columns: `public_compound_id`, `target_gene`, `n_contexts`, `contexts`, `best_z`, `mean_z`, `best_rank`, `mean_rank`, `is_named_control`, `kd_delta_median`, `kd_flag_weak`, `hub_flag`. No tier or recipe columns. |
| `showcase_hits.csv` | 2,000 | Shortlist with exact per-dataset evidence: `n_datasets_scored`, `n_datasets_top5pct`, `n_datasets_top1pct`, `best_percentile`, `best_dataset_exact`, plus consensus columns. Dataset-count fields can aggregate across contexts and must not be read as independent successes divided by datasets; use explicit query rows for that comparison. |
| `top100_phenomimics.csv` | 101 | The ranked, lab-facing list: SAR families passing every guardrail in this annex (non-hub target not flagged for weak knockdown, non-promiscuous compounds, at least 3 hitting members and a recipe-mate footprint of at most 200 compounds), ranked by CRISPR-match strength, family size, and cross-context replication. `family_id`, `target_gene`, `family_size`, `family_max_z`, `family_evidence`, `public_compound_id`, `best_z`, `tier`, `contexts`, `n_contexts`, `total_family_size`, `hub_flag`, `kd_delta_median`, `composite_score`, `is_family_representative`. |
| `top100_family_summary.csv` | 31 | Per-family rollup of the top 100. |
| `validation_empirical_p.csv` | 2,074 | Known-target calibration queries with random-target `p_emp`, hub-matched `p_emp_hub`, and a separate 20-draw comparison in `p_emp_20draw`. |
| `ensemble_rescoring_panel.csv` | 42 | Control-pair panel; `n_cells` is the column name for context/dataset queries, not biological cells. |
| `curated_calibration_summary.csv` | 54 | Counts per retained control-target pair; descriptive, without best-of-many significance claims. |
| [curation_summary.json](curation_summary.json) | 14 fields | Calibration denominators, p-value counts and ensemble summaries. |
| [family_null_check.csv](family_null_check.csv) | 106 | 100 null draws plus six summary rows for all filtered pairs and the replicated subset. |
| `target_hubness.csv` | 18,789 | Per-target guardrail: `n_compounds_hit`, `hub_frac`, `hub_flag`. |

## Method names are part of the result

The signed-rank z values in ZSH-3760, this annex’s cosine/consensus scores,
and its two-channel ensemble scores have different definitions. Do not
transfer rankings or calibration between them.
[Interpretation notes](../annex_hypotheses/INTERPRETATION_NOTES.md).

`n_cells` in the ensemble table denotes context/dataset **queries**, not
biological cells. Known pharmacology and response correspondences are
separate fields; see [control annotations](../annotations/README.md).
