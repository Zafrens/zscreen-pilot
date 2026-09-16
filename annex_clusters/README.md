# Clusters Annex

This annex summarizes **1,007 chemical-response graph clusters** across
eight contexts, with coherence statistics and pathway annotations. The
graph uses recipe relationships, chemical similarity and 32-program response
similarity together.

The [original-cluster atlas](../atlas/original_clusters/README.md) adds exact
member IDs and gene/program centroids, so users can inspect the compounds
behind each census row.

## How the clusters were built

For each context separately, compounds were placed in a graph. Candidate
pairs are compounds that share a building block at the same recipe
position. An edge requires both program-usage cosine and ECFP4 Tanimoto
similarity above per-context thresholds, tuned to a joint edge rate near
1e-4.
Connected components of size 3 to 500 were kept as clusters. Members are
connected by the joint chemical/response criteria. Inspect `anchor_frac`
to see what fraction shares the reported anchor component; a graph component
need not have one variable block shared by every member.

Cluster coherence is the mean pairwise cosine similarity of the members'
measured usage profiles, calibrated against 200 size-matched random
compound sets per cluster. The saved census reports q <= 0.01 for all 1,007 clusters and median
coherence z of 4.8. Because response similarity helps define the graph,
these statistics describe the selected clusters; they are not an independent
validation of cluster discovery.

Pathway annotation starts from each cluster's 6,000-gene centroid
signature. The top up- and down-driver genes are tested by Fisher
enrichment with Benjamini-Hochberg FDR against 1,639 gene sets from
MSigDB Hallmark 2020, KEGG 2021 Human, and Reactome 2022. 855 of the
1,007 clusters have at least one significant set at q < 0.05.

## What the clusters are about

For a compact display, use a cluster’s top up-pathway when its q < 0.05;
otherwise use its top down-pathway when significant. If neither qualifies,
label it “No significant pathway.” An ordered keyword rule groups the
selected set names into the following display categories.

| Display family | Clusters |
|---|---:|
| Myc/prolif | 361 |
| No significant pathway | 152 |
| Mito/Proteostasis | 144 |
| Other | 113 |
| Mito/OXPHOS | 65 |
| Translation/ribo | 47 |
| mTORC1 | 35 |
| ER/UPR | 26 |
| Immune/IFN | 17 |
| EMT/ECM | 14 |
| Cell cycle | 9 |
| mRNA splicing | 9 |
| Stress/HSF | 4 |
| Amino acid transport | 3 |
| Hypoxia | 3 |
| p53/apoptosis | 2 |
| Glycolysis | 1 |
| Lipid/cholesterol | 1 |
| Proteasome/UPS | 1 |

[Counts](pathway_family_counts.csv) and the exact
[selection/keyword rule](pathway_family_method.json) make the display
reproducible from the census. “Other” contains significant pathways with no
matching keyword. These are descriptive display categories, not distinct
validated mechanisms.

The census records `prior_series_n=0` for 881 clusters. This is the count of
matching chemotype-series records in the same context whose component IDs
contain the cluster’s anchor ID. It does not measure member overlap,
biological novelty or correspondence to named program groups.

## `cluster_census.csv` column contract

Rows are sorted by `context`, then by `coherence_z` descending within a
context. The row key is (`context`, `cluster_id`).

This [cluster_census.csv](cluster_census.csv) is the canonical annotation
table used by the Hugging Face cluster configuration. The atlas's
[census.csv](../atlas/original_clusters/census.csv) is an enriched lookup
view of the same 1,007 keys, adding `centroid_row`, `atlas_id` and
`atlas_namespace` and sorting by context/cluster ID. Its shared annotations
agree within floating-point serialization: 63 rows have textual
differences only in q-value columns (maximum absolute difference 4 × 10⁻²⁴).
Join by the row key; use the atlas’s explicit `centroid_row` to index its arrays.

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
- `prior_series_n`: count of records in [chemotype_series.csv](../annex_chemistry/chemotype_series.csv)
  from the same context whose `bb_id_a` or `bb_id_b` contains the cluster
  anchor ID; 881 clusters have zero matching records. This is not a percentage.

The clusters are hypothesis-generation structure: candidates for
follow-up, not confirmed mechanisms.

[Inspect exact memberships and centroids](../atlas/original_clusters/README.md) · [Methods and input access](../docs/ANALYSIS_ACCESS.md).
