# How to read each layer

This document matches conclusions to the grain at which the data are
strongest. The reliability reference table is in
`docs/SCIENTIFIC_OVERVIEW.md`; the design argument is in
`docs/WHY_THIS_MATTERS.md`.

## 1. Program and building-block grain first

Program-level (32 usages) and building-block-level (pooled over all
compounds carrying a block) structure is the strongest layer:
cross-context structure is 10–20× stronger in program space than gene
space, and building-block effects carry split-half reliability around
0.5–0.58. The libraries repeat building blocks across thousands of
compounds so that those pooled reads are strong. Headline claims in
this package live at these levels.

## 2. A single-compound profile is a vote, not a verdict

Per-compound measurement reliability at the current sequencing depth
is 0.02–0.06 (split-half: two random halves of a compound's wells
compared). A per-compound number is therefore most useful as input to
an aggregate — a mean over carriers, a rank within a set, a
program-level coordinate. The `zel028` contexts
(`zel028_hek293`, `zel028_a549`, `zel028_h1650`) are predominantly
singleton measurements and should be read at the pooled, level level
only.

## 3. Measured versus predicted layers are labeled

Everything under `core/` is measured. Model outputs (`models/`
predictions, `y_pred_z` in the imaging annex dumps) are predictions.
Within the SAR tables, `evidence_level` / `evidence_tier` separates
`measured` rows from `grammar_level` rows. Keep the label with the
number when quoting it.

## 4. Grammar-level rows and tier-matched nulls

For `zel024`, per-compound measurements are pooled by construction,
so its structure-activity tables are defined at the recipe level.
Rows marked `grammar_level` are recipe-level expectations ("these
building blocks have this effect"). `zel039` SAR rows are
`measured`.

In `zel039`, sequencing-depth tier composition differs across
compound sets, and naive similarity statistics inherit that
structure. Every `zel039` similarity claim in this package is
computed against **tier-matched nulls**: random compound sets matched
in size and read-depth tier (shallow / mid / deep). The depth-tier
composition columns in `annex_chemistry/chemotype_series.csv` keep
that check visible alongside the effect.

## 5. Specificity lives in rank and identity

Several hypothesis-layer statistics use permissive nulls (for
example, a gene-label permutation under which 88–98% of
building-block levels match some control at p ≤ 0.01). A small
p-value against such a null is the entry ticket. The specificity of
a match lives in its rank and identity: rank-1 of a large candidate
set, recovered by independent evidence lines. Caveat flags
(`weak_null`, `singleton`, `triage_grade`, `low_coverage`) mark
where each row sits.

## 6. Imaging: markers are targets, never features

The pixels used to compute the image embeddings and latents include
the marker channels. A model that takes embeddings as inputs and
predicts marker intensities can succeed by reading the marker pixels
directly. Marker values are therefore prediction targets, not input
features. Predicting RNA program usages from embeddings is not
circular (the RNA measurement shares no pixels with the images). The
two imaging panels differ: p62 exists only in the `zel024` panel,
BRD4 and ConA only in the `zel031` panel. BRD4 appears in this
package only as that marker channel.

## 7. External concordance is a ranking aid

Matches between signatures in this package and external atlases
(CRISPR knockout panels, connectivity resources) are labeled
triage-grade: cross-cell-line and knockout-versus-compound
differences cap interpretability. All 2,727 external-atlas
resemblance rows sit in tier C, with positive-control recovery rates
attached for calibration. Mechanism recoveries that are exact enough
to name — the METTL3 inhibitor / knockout phenocopy, ZSH-3760, in
particular — are called out individually with their nulls.

## 8. Fold 0, and one model-context exception

Fold 0 (SHA256(`public_compound_id`) mod 5) was held out of basis
fitting and reference-model training, and it is the intended test
bed. Promoted usages can be slightly more predictable on fold 0 than
on folds 1–4 in some exercises (observed up to +0.14), because the
fitting pipeline's targets and the evaluation share the fold-0
design. Cross-exercise comparisons of analysis pipelines therefore
use folds 1–4; fold 0 remains the held-out test bed for models
trained on folds 1–4.

On `zel031_a549` the shared context-token trunk trails the
per-context expert model by about 9% relative (0.0434 vs 0.0479
decoded mcPearson on held-out compounds; evidence:
`core/benchmark/per_context_comparison_k32.csv`). In the other seven
contexts the trunk improves in six and is essentially flat in
`zel024_h1650`. When quoting a reference number for `zel031_a549`,
prefer the per-context expert scores.

## 9. Hypothesis tables generate the next experiment

Everything in `annex_hypotheses/` is a lead. The tier system (A
anchor-validated, B strong pooled, C triage) describes how much
independent evidence converges; the `kill_confirm_experiment` column
in `anchor_leads.csv` is the intended next measurement for each
distilled lead. A complete 3,754-row ledger will contain false
positives even with correct nulls; that is why the distilled tables
exist.
