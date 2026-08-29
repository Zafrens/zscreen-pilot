# How to read the hypothesis tables

These tables convert the program and grammar layers into leads that
can be taken into an experiment. Each row states the evidence that
put it on the list, the null against which that evidence was judged,
and — for the distilled leads — a measurement that would kill or
confirm the claim. The distilled entry point is `anchor_leads.csv`;
the 1,027-row ledger is the complete mining output and is
correspondingly coarser.

## The unit of claim is the building block, not the compound

Claims are made at the level of **building-block (BB) levels and bb
grammar** — "compounds built on `BB_2085420374` tend to induce a
heat-shock program" — not at the level of individual compounds. The
libraries repeat blocks across hundreds to thousands of carriers, so
bb-level effects are the strongest, most reproducible layer. A
single-compound reading of these tables is a candidate for
confirmation on that compound's raw measurements.

## Specificity lives in match rank and identity

The level→control match p-values come from a gene-label permutation
null that is deliberately weak: all 35 controls are strong
perturbations sharing broad program axes, so most levels match some
control at p ≤ 0.01 (88–98% of levels, depending on context). A
small p-value therefore certifies only that a program-level
alignment exists. The informative content of a match is **which**
control ranks first and **how** the match identity converges across
independent analyses (neighborhood enrichment, direct effect-vector
alignment, unsupervised program recovery). The `weak_null` caveat
flag marks every row where this applies.

## Context-specific reading rules

- **zel039_aec7** similarity analyses used **tier-matched nulls**
  throughout. Compounds share a sequencing-depth-tier structure that
  inflates naive similarity; every zel039 coherence, neighborhood,
  and imaging number in this annex was computed against null sets
  matched on size and depth tier.
- **zel024_hek293** tables are **grammar-level**. That context's
  surfaces are pure bb-backbone (per-compound own-data weight ≈ 0),
  so two-position series coherence and neighborhood enrichment hold
  essentially by construction (1,823/1,827 series pass even label
  permutation). Use zel024 rows for series discovery and annotation;
  they are marked `grammar_level` / `triage_grade`.
- **zel028 contexts** support pooled, level-level reads only
  (singleton measurements); rows from these contexts carry the
  `singleton` caveat.
- Depth-tier skew can masquerade as signal at series level; check
  tier composition columns before trusting any single series.

## External concordance

Compound ↔ CRISPR-knockout concordance lives in
`annex_phenomimicry/`: 43 knockout signature sets from 10
perturb-seq datasets, calibrated against a random-target empirical
null. Recovery of known pharmacology is real but modest on average
and concentrated in 25 control → target pairs at the null floor,
named individually in that annex. The dominant background is a
generic RNA/stress hub axis; check `hub_flag` before treating any
hit as specific. Same-MOA controls do not cluster with each other
in any cell line, which bounds what an MOA-level claim can mean
here.

## What this annex does not contain

No table here supports a BRD4-linked mechanism; BRD4 appears in the
package only as a marker channel in the zel031 imaging panel. There
are no compound-level drug claims, no validated targets, and no
clinical-relevance statements. The `kill_confirm_experiment` column
is the intended next step for each lead: every flagship hypothesis
states the experiment that would kill or confirm it.
