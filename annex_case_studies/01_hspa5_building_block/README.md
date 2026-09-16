# A shared chemical component produces a coherent RNA response

In the AEC7 pilot, **1,512 compounds after the retained-measurement filter** share `BB_2371372935` at position `bb0` and support a coherent aggregate RNA response. The broader core recipe table contains **2,267 compounds** with that same `bb0` value. Profiles from two disjoint sets of member compounds correlate at **0.981**. The response resembles an HSPA5 genetic-perturbation signature, providing a biological reference for exploring the family and its chemical partners.

| Quantity | Result |
|---|---:|
| Member compounds | 1,512 |
| Retained cells | 5,373 |
| Member-half profile correlation | 0.9805847 |
| HSPA5 signed top-500 correspondence | 0.092 |
| Raw HSPA5 reference rank for this aggregate | 3 |

[Exact values and definitions](data/series_summary.csv).

## How to use this example

Join the public building-block ID to [core recipes](../../core/recipes.parquet) to explore its chemical partners. The displayed family uses the retained-measurement filter; selecting all matching core recipes returns 2,267 compounds, not the filtered 1,512-member analysis group. The [summary row](data/series_summary.csv) records the filtered count; this annex does not ship the complete filtered member list or cell-level filter inputs to reconstruct that membership from recipes alone.

The result illustrates a useful scale of analysis: many recipes provide observations of the same component across different chemical combinations. [The partner comparison](../02_partner_responses/README.md) asks what changes when the group is narrowed to a particular combination.

## Brief method

Member-cell responses were pooled within device/sample strata, compared with matched no-compound capture references and combined across available strata using the fixed-depth normalization. This full-gene response construction is separate from the core 32-program projection.

The two halves contain different member compounds from the same experiment collection. Genetic correspondence compares signed RNA changes with an external **teloHAEC** perturbation reference; the chemical cells are **AEC7**. It measures transcriptional resemblance and does not establish direct HSPA5 engagement.

The public 6,000-gene surfaces alone do not reconstruct the full-gene correspondence score. [Data scope](../../docs/ANALYSIS_ACCESS.md) · [Reference sources](../../docs/REFERENCE_SOURCES.md).

[All examples](../README.md).
