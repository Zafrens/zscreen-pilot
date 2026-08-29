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

98 control → annotated-target queries, 1,546 (compound × context × dataset)
scored cells, calibrated against a 20-draw random-target empirical null run
under the same aggregation:

- Annotated targets rank at ≤ 5th percentile in **5.9% of cells vs 4.9%**
  for random targets — a real but modest average edge.
- **6.1% of rows beat all 20 null draws** (empirical p ≤ 0.05), against a
  4.8% expectation.
- **25 control → target pairs sit at the 20-draw floor** — the credible
  core: STC-15/STM2457→METTL3, MSC1094308→DOT1L, GSK126→EZH2,
  BMS-509744→ITK, N-deshydroxyethyl dasatinib→SRC, AZD-7624→MAPK14,
  GCN2-IN-7→EIF2AK4, XL019→JAK2, ZM336372→RAF1, JAB-3068→PTPN11,
  KME-2780→TBK1, IRAK inhibitor 1→IRAK1, SMARCA ligand 1→SMARCA2/4,
  MK2-IN-1→MAPKAPK2, palbociclib→CDK4, endoxifen→ESR1,
  ZF135/MRTX-1719→PRMT5, rucaparib/veliparib→PARP1, momelotinib→JAK1/JAK2,
  fexagratinib→FGFR2/3.

Recovery concentrates on targets with clean, non-essential KO phenotypes.
Non-recovery is expected for essential targets (KO dominated by cell death),
activity-vs-abundance pharmacology, and cell-line mismatch.

**The aggregation lottery:** any statistic that takes a best over many draws
(contexts × datasets) has a null rate far above the nominal percentile.
Judge any single compound × target claim by its per-row empirical p in
`validation_empirical_p.csv`, never by counts of datasets or contexts.

## The hub guardrail

The strongest convergence in the comparison is not specific biology: several
hundred KO targets (XRN1, UPF1/2, SMG7, SNRPE, EIF3D, … — RNA homeostasis
and stress response) are each mimicked by 1–8% of the entire library across
every context. Many compounds, across unrelated chemotypes, push cells into
a generic RNA/stress state. A hit on such a target says "broadly
RNA/cytotoxic-acting compound", not a specific target hypothesis. Every
target carries a `hub_flag` (`hub_generic_stress` / `frequent` / `specific`)
in `target_hubness.csv` and in the pair tables; the ranked
`top100_phenomimics.csv` excludes hub targets. The flags are filters, not
deletions — a genuinely RNA-targeting drug would also hit them.

## SAR structure of the hits

A single compound matching a target is a weak observation; several related
compounds matching the same target is a structure-activity relationship.
Families are built per target from the OBOC recipes (bb0–bb4: family-mates
match after dropping any one diversity position), with single-linkage
Tanimoto ≥ 0.5 on fingerprints for the few recipe-less zel039 compounds.
Only families with ≥ 3 members are trusted for the ranked table
(`top100_phenomimics.csv`, 100 hypotheses from 31 families covering 28
targets). Most strong non-hub hits are structural singletons — they belong
on a watch-list, not in a follow-up queue.

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
| `top100_phenomimics.csv` | 100 | The ranked, lab-facing list: non-hub hypotheses from SAR families of ≥ 3 members, ranked by family size. `family_id`, `target_gene`, `family_size`, `family_max_z`, `family_evidence` (`recipe` / Tanimoto), `public_compound_id`, `best_z`, `tier`, `contexts`, `is_family_representative`. |
| `top100_family_summary.csv` | 31 | Per-family rollup of the top 100. |
| `validation_empirical_p.csv` | 1,546 | Per (control × context × dataset × target) empirical p-values against the 20-draw random-target null: `control_name`, `target_gene`, `cosine`, `rank_mimic`, `percentile`, `p_emp`. The calibration reference for any single-claim review. |
| `target_hubness.csv` | 18,789 | Per-target guardrail: `n_compounds_hit`, `hub_frac`, `hub_flag`. |
