# Reading mimic and antimimic scores

Both pair tables store larger numbers for stronger evidence **in that table's
own direction**. Do not infer the direction from the sign of `best_z` alone.

| Table | Stored context score | Filter on aggregated `best_z` |
|---|---|---|
| [phenomimic_pairs.parquet](phenomimic_pairs.parquet) | Signed consensus z | ≥5 |
| [antimimic_pairs.parquet](antimimic_pairs.parquet) | −1 × signed consensus z | ≥5 |

The signed consensus combines target-standardized cosine scores across
reference datasets. The antimimic extraction sets `sgn = -1` and stores
`consensus_z = sgn * sc` before aggregation. Only direction-specific ranks
1–50 per compound and context enter the aggregation. For each compound-target
pair, the published `best_z` is the maximum of those stored scores and
`mean_z` their mean; `n_contexts` counts those retained context rows. The
final antimimic table excludes named controls and retains `best_z >= 5`.

**Example:** signed consensus scores −8 and −4 in two retained contexts
become stored scores 8 and 4. The table records `best_z = 8`, `mean_z = 6`
and `n_contexts = 2`. Negating `best_z` gives the most negative retained
signed consensus; negating `mean_z` gives the signed mean across these
retained contexts. Unretained contexts are absent from these summaries.

This score measures a position relative to a target's score distribution.
A negative standardized consensus is not proof that the unstandardized
cosine is negative, and neither score establishes rescue, antagonism or
direct molecular target engagement.

## Schema

The antimimic table has 561,355 rows and 12 columns:

`public_compound_id`, `target_gene`, `n_contexts`, `contexts`, `best_z`,
`mean_z`, `best_rank`, `mean_rank`, `is_named_control`, `kd_delta_median`,
`kd_flag_weak`, `hub_flag`.

`best_rank` and `mean_rank` summarize direction-specific ranks, where smaller
is better. There is no `tier` column and no `bb0`–`bb4`; obtain recipes by
joining [core/recipes.parquet](../core/recipes.parquet) on `public_compound_id`.
The `hub_flag` is the shared target lookup derived from mimicry hit frequency,
not a separately estimated frequency of antimimic hits.

Use the shared-gene, per-target standardization and consensus definitions
in the [scoring guide](README.md#scoring). Exact reconstruction of the
full-axis scores requires [additional inputs](../docs/ANALYSIS_ACCESS.md).
