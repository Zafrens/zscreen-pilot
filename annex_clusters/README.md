# Clusters Annex

This annex holds the unsupervised cluster census: analog-family compound
clusters recovered from the 32-program usage vectors, with their
coherence statistics and pathway annotations. One file,
`cluster_census.csv`, 1,007 rows, one row per cluster across the 8
contexts.

## How the clusters were built

For each context separately, compounds were placed in a graph. Candidate
pairs are compounds that share a building block at the same recipe
position. An edge requires both program-usage cosine and ECFP4 Tanimoto
similarity above per-context thresholds, tuned to a joint edge rate near
1e-4.
Connected components of size 3 to 500 were kept as clusters. Members of
a cluster are genuine analog families: a shared core block at one
position, varied substituents at the others.

Cluster coherence is the mean pairwise cosine similarity of the members'
measured usage profiles, calibrated against 200 size-matched random
compound sets per cluster. All 1,007 clusters pass q <= 0.01, and the
median coherence z is 4.8.

Pathway annotation starts from each cluster's 6,000-gene centroid
signature. The top up- and down-driver genes are tested by Fisher
enrichment with Benjamini-Hochberg FDR against 1,639 gene sets from
MSigDB Hallmark 2020, KEGG 2021 Human, and Reactome 2022. 855 of the
1,007 clusters have at least one significant set at q < 0.05.

## What the clusters are about

Dominant pathway families across the 1,007 clusters, counted from each
cluster's top enriched gene set:

- Myc/proliferation: 369 clusters
- mitochondrial/proteostasis: 163
- mitochondrial/OXPHOS: 83
- translation/ribosome: 47
- mTORC1: 39
- ER/unfolded protein response: 33
- immune/interferon: 23
- EMT/ECM: 17

The remaining 233 clusters fall in smaller families.

875 of the 1,007 clusters have no prior named theme in
`annex_hypotheses/program_atlas.csv`, so most of this structure is new.

## `cluster_census.csv` column contract

Rows are sorted by `context`, then by `coherence_z` descending within a
context. The row key is (`context`, `cluster_id`).

- `context`: library x cell-type context, e.g. `zel024_hek293`.
- `cluster_id`: cluster identifier within the context.
- `n_members`: number of compounds in the cluster.
- `coherence`: mean pairwise cosine similarity of the members'
  32-program usage profiles.
- `coherence_z`: standard score of `coherence` against 200 size-matched
  random compound sets from the same context.
- `coherence_q`: Benjamini-Hochberg FDR q-value of the coherence
  statistic. Every row passes q <= 0.01.
- `anchor_bb`: building block shared by the largest fraction of members
  at one recipe position (`BB_##########`). Constant (fixed) positions
  are excluded from anchor detection, so the anchor is always a
  variable, discriminating block.
- `anchor_pos`: recipe position of the anchor block (`bb0` to `bb4`).
- `anchor_frac`: fraction of members carrying the anchor block at
  `anchor_pos`.
- `top_up_set`: top enriched gene set among the cluster's up-driver
  genes, formatted as `library:set name`.
- `top_up_q`: FDR q-value of `top_up_set`. A value >= 0.05 means the
  best available set did not reach significance.
- `top_dn_set`, `top_dn_q`: the same two fields for the cluster's
  down-driver genes.
- `prior_series_n`: percentage of members overlapping a previously
  reported chemotype series (`annex_chemistry/chemotype_series.csv`);
  0 for 881 of the 1,007 clusters.

The clusters are hypothesis-generation structure: candidates for
follow-up, not confirmed mechanisms.
