# Chemical-response cluster atlas

This atlas connects the 1,007 clusters in the public census to their exact 5,346 compound memberships and their RNA centroids. The graph clusters cover eight contexts. The graph combines shared recipe components, chemical similarity and transcriptional-program similarity.

Use this atlas to inspect the compounds behind a response family, compare its expression pattern with other families and retrieve the recipes for follow-up.

## Files and keys

| File | Contents |
| --- | --- |
| `members.parquet` / `members.csv` | One row per cluster membership. Key: `(context, cluster_id, public_compound_id)`. The CSV and Parquet encode the same table. |
| `census.csv` | Enriched lookup view of the [canonical cluster annotations](../../annex_clusters/cluster_census.csv), adding `centroid_row`, `atlas_id` and `atlas_namespace`. |
| `centroid_keys.csv` | Row identities for both centroid arrays, sorted by context and then cluster ID. |
| `program_centroids.npy` | 1,007 × 32 float32 array. Each row is the coordinate-wise **median** of its members' core program usages. Columns follow the pinned shared k=32 basis. |
| `gene_centroids.npy` | 1,007 × 6,000 float32 array. Each row is the arithmetic **mean** of its members' core gene surfaces. Columns follow `core/surfaces/harmonized_6000_genes.parquet`. |
| `graph_thresholds.csv` | Original program-cosine and chemical-similarity thresholds by context. |

`atlas_namespace` is `zscreen_original_graph_v1`. An `atlas_id` combines this namespace, context and cluster ID. These IDs name the joint chemistry/response graph clusters. A recipe-defined family such as the [HSPA5 example](../../annex_case_studies/01_hspa5_building_block/README.md) is a different scientific object and should not be joined by an assumed cluster number.

## Read a cluster

```python
from pathlib import Path
import numpy as np
import pandas as pd

package = Path(".")  # Run from the package root, or set this explicitly.
atlas = package / "atlas/original_clusters"
members = pd.read_parquet(atlas / "members.parquet")
keys = pd.read_csv(atlas / "centroid_keys.csv")
genes = pd.read_parquet(package / "core/surfaces/harmonized_6000_genes.parquet")
gene_centroids = np.load(atlas / "gene_centroids.npy")

selected = keys.query("context == 'zel039_aec7' and cluster_id == 115").iloc[0]
compound_ids = members.loc[members.atlas_id.eq(selected.atlas_id), "public_compound_id"]
response = gene_centroids[int(selected.centroid_row)]
print(selected.atlas_id, len(compound_ids), response.shape)
```

Join annotations by `(context, cluster_id)`. The canonical [annex census](../../annex_clusters/cluster_census.csv) and this atlas census contain the same 1,007 keys and shared annotations; 63 rows differ only in q-value text serialization (maximum absolute difference 4 × 10⁻²⁴). The annex census sorts by context/coherence, while this lookup sorts by context/cluster ID and adds the atlas fields. Use `centroid_row` only to address the arrays declared here. Sorting a census by coherence does not reorder the corresponding arrays.

## Reproduction

From the package root:

```text
python atlas/original_clusters/verify.py --package .
```

This reconstructs centroids and coherence from the released core data and member IDs, checks compound and row identities, and compares both census views. All inputs required by this verification are included in the package.

Centroid inputs are the core program usages and harmonized surfaces. Program-atlas labels use a [separate namespace](../../annex_hypotheses/INTERPRETATION_NOTES.md); they must not be joined by an assumed cluster number.
