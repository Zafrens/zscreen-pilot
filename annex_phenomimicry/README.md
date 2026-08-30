# annex_phenomimicry/ — compound × CRISPR-knockout concordance

A compound **mimics** a gene knockout (KO) when its transcriptional signature
moves genes the way the KO does. This annex compares every compound signature
in the package against a multi-atlas panel of CRISPR perturbation signatures
and ships the resulting compound × target hypotheses, calibrated against an
empirical null. Everything here is **hypothesis-grade**: a mimicry hit is a
connectivity-map suggestion that a compound may act through that gene or
pathway, not a target claim.

## Data layers

**Compound side.** Per-compound device-centered log1p-CP10k profiles at full
46,944-gene width, built pipeline-faithful to `docs/METHODS.md` (median
Pearson ≥ 0.99999 against the released 6,000-gene surfaces in every context),
then per-gene MAD z-scored within each context. 190,964 compound × context
signatures covering 163,001 unique compounds across the 8 contexts.

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
z-profiles over the genes both sides measured (8.2k–25.4k shared genes per
pair), standardized per target within the pair, then a Stouffer consensus
across all 43 datasets weighted by √(shared genes). Single-dataset hits are
noisy; consistency across independent datasets is what makes a hit credible.
The output is a consensus z-score per compound × target pair per context.

## Tiers

| tier | rule | pairs |
|---|---|---:|
| `B_consensus_strong` | z ≥ 8 in ≥ 2 contexts | 101 |
| `B_single_context` | z ≥ 8 in one context | 24,751 |
| `C_moderate` | z ≥ 5 | 401,609 |

`zel039_aec7` compounds cannot accumulate multi-context replication (the
ZEL039 library barely overlaps the other contexts), so their hits cap at
`B_single_context`; judge them on per-dataset evidence in
`showcase_hits.csv` rather than on `n_contexts`.

## Calibration (named controls with curated mechanisms)

98 control → annotated-target queries were designed; 55 pairs (35 controls,
44 gene targets) have both sides scored and form the calibration set. The
remaining 43 are compounds outside the profiled contexts (41) and two
annotation strings with no single knockout in the panel. Scoring the 55
pairs across contexts and datasets gives 2,109
(compound × context × dataset) cells. Each cell is calibrated against a
1,000-draw random-target empirical null run under the same aggregation
(`p_emp`), plus a 1,000-draw hub-matched null that draws random targets
from the same hubness class as the query target (`p_emp_hub`).

Recovery concentrates where cross-modality recovery is expected to work:
clean, non-essential targets in the drug classes with the strongest
transcriptional signatures.

- **The strongest pairs recover across many independent cells.**
  STM2457 → METTL3 reaches p ≤ 0.05 in 16 of 88 cells (4.4 expected by
  chance) across 5 contexts and 6 datasets; 8 of those cells also pass
  the hub-matched null (min p = 0.007). STC-15 → METTL3 reaches p ≤ 0.05
  in 19 of 88 cells (10 hub-matched), and MSC1094308 → DOT1L in 8 of 35
  cells (6 hub-matched). GSK126 → EZH2 and GCN2-IN-7 → EIF2AK4 also hold
  multiple cells passing both nulls, and cobimetinib → MAP2K1 passes
  both nulls in two contexts (zel031_a549, zel028_hek293).
- **Recovery is specific in both directions.** The recovering targets are
  epigenetic writers/erasers and signaling kinases, the classes with the
  strongest transcriptional signatures in sci-Plex/LINCS. Recovery is
  absent in zel024_h1650 (same compounds, same library, the
  shallowest-response line) and for essential-target knockouts dominated
  by cell death.
- The six named pairs above account for 58 of the 108 cells at p ≤ 0.05:
  19% of their 301 cells, against 2.8% across all other pairs; 14 cells
  reach p ≤ 0.01. These recovery rates sit at the top of published
  cross-modality benchmarks: PRISM reports ~15% drug ↔ target-knockout
  concordance in viability space, JUMP-CP matches compounds to CRISPR
  signatures of their known targets at a 7–11% true-positive rate
  (5% FPR), and even knockout ↔ knockout across cell lines transfers
  at r ≈ 0.4. The per-pair tail above is the calibration to read.
- 27 of the 55 pairs have at least one cell at p ≤ 0.05, and 15 have two
  or more. With a median of 30 cells per pair, per-pair cell counts are
  the unit to read (the aggregation lottery below).

Recovery concentrates on targets with clean, non-essential KO phenotypes.
Non-recovery is expected for essential targets (KO dominated by cell death),
activity-vs-abundance pharmacology, and cell-line mismatch.

**The aggregation lottery:** any statistic that takes a best over many draws
(contexts × datasets) has a null rate far above the nominal percentile.
Judge any single compound × target claim by its per-row empirical p in
`validation_empirical_p.csv`, never by counts of datasets or contexts.

## The hub guardrail

The strongest convergence in the comparison is not specific biology: several
hundred KO targets (e.g., XRN1, UPF1/2, SMG7, SNRPE, EIF3D; RNA homeostasis
and stress response) are each mimicked by 1–8% of the entire library across
every context. Many compounds, across unrelated chemotypes, push cells into
a generic RNA/stress state. A hit on such a target indicates a broadly
cytotoxic or RNA-stress phenotype rather than a specific target hypothesis.
Every target carries a `hub_flag` (`hub_generic_stress` / `frequent` /
`specific`) in `target_hubness.csv` and in the pair tables; the ranked
`top100_phenomimics.csv` excludes hub targets. The flags function as
filters rather than deletions; a genuinely RNA-targeting drug would also
hit them.

## SAR structure of the hits

A single compound matching a target is an isolated hit; several related
compounds matching the same target is a structure-activity relationship.
Families are built per target from the OBOC recipes (bb0–bb4: family-mates
match after dropping any one diversity position). The ranked table
(`top100_phenomimics.csv`, 101 hypotheses from 31 families covering 26
targets) keeps only families that pass every guardrail in this annex:
non-hub targets with validated knockdown, non-promiscuous compounds, and
3 to 200 recipe-mates per family (the cap keeps broad stress-axis
chemotypes out). Families rank by CRISPR-match strength (mean of the
three best member z-scores), log family size, and a replication bonus for
families spanning more than one context. Under a recipe-preserving,
degree-matched null (100 draws), the guardrail-filtered set yields 166
such families against 108.8 ± 9.4 expected by chance, above all 100
draws. The targets concentrate in cell-cycle and proteostasis machinery,
the genes with the strongest knockout phenotypes in perturb-seq. Outside
the ranked families, strong non-hub hits are mostly structural
singletons; treat those as a watch-list.

## The reversal track

`antimimic_pairs.parquet` holds the mirror image: compounds whose signature
*reverses* a KO signature (z ≤ −5), i.e. rescue/antagonist hypotheses. Same
scoring, same caveats, opposite sign.

## Caveats (read before acting on any row)

- CRISPR KO ≠ pharmacological inhibition (complete loss vs partial, no
  off-targets, no exposure/PK). Hits are hypothesis-grade.
- Gene-panel mismatch: some datasets measure ~8–9k genes; only shared genes
  enter each pair's score.
- `kd_flag_weak` marks targets whose own-transcript depletion was marginal
  — their KO signatures may not reflect the intended gene.
- Check `hub_flag` before treating any hit as specific.

## Files

| file | rows | what it is |
|---|---:|---|
| `phenomimic_pairs.parquet` | 426,461 | All mimicry pairs at tier C or better: `public_compound_id`, `target_gene`, `n_contexts`, `contexts`, `best_z`, `mean_z`, `best_rank`, `mean_rank`, `is_named_control`, `kd_delta_median`, `kd_flag_weak`, `tier`, recipe columns `bb0`–`bb4`, `hub_flag`. |
| `antimimic_pairs.parquet` | 561,355 | The reversal track (z ≤ −5): rescue/antagonist hypotheses, same column convention. |
| `showcase_hits.csv` | 2,000 | Shortlist with exact per-dataset evidence: `n_datasets_scored`, `n_datasets_top5pct`, `n_datasets_top1pct`, `best_percentile`, `best_dataset_exact`, plus consensus columns. 530 pairs recover in ≥ 3 datasets at ≤ 5th percentile. |
| `top100_phenomimics.csv` | 101 | The ranked, lab-facing list: SAR families passing every guardrail in this annex (non-hub target with validated knockdown, non-promiscuous compounds, 3–200 recipe-mates), ranked by CRISPR-match strength, family size, and cross-context replication. `family_id`, `target_gene`, `family_size`, `family_max_z`, `family_evidence`, `public_compound_id`, `best_z`, `tier`, `contexts`, `n_contexts`, `total_family_size`, `hub_flag`, `kd_delta_median`, `composite_score`, `is_family_representative`. |
| `top100_family_summary.csv` | 31 | Per-family rollup of the top 100. |
| `validation_empirical_p.csv` | 2,109 | Per (control × context × dataset × target) empirical p-values: `p_emp` against a 1,000-draw random-target null, `p_emp_hub` against a 1,000-draw hub-matched null, `p_emp_20draw` (legacy 20-draw null, first 1,546 rows), plus `control_name`, `target_gene`, `cosine`, `rank_mimic`, `percentile`. The calibration reference for any single-claim review. |
| `target_hubness.csv` | 18,789 | Per-target guardrail: `n_compounds_hit`, `hub_frac`, `hub_flag`. |
