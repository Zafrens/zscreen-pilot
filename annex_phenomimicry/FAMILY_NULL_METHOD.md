# Family-count comparison

[family_null_check.csv](family_null_check.csv) contains 100 null draws
(seed 20240611) and six summary rows. Columns are `draw`,
`count_all_filtered` and `count_replicated_subset`.

The unit is a target-specific family cluster. Input pairs pass the
[response/recipe guardrails](README.md#sar-structure-of-the-hits). Families
contain at least three hitting compounds and have a direct recipe-mate
footprint of no more than 200 library compounds.

For each target, retain its number of hitting compounds and sample that
many distinct compounds from the filtered pool, with probability weighted
by each compound’s number of target hits. Keep the selected compounds’
recipes, rebuild target-specific components using the same drop-one-position
recipe rule, and apply the same size criteria. This preserves target hit
counts; compound hit degrees are sampling weights, not exactly fixed counts.

The observed full filtered set contains 166 eligible clusters. The null
mean is 108.79, population SD 9.442769720796965, and range 84–131. The
empirical tail fraction, including the usual one-count adjustment, is
`(1 + number of null counts >= 166) / (1 + 100) = 1/101`.
These counts precede selection of the ranked 31-family shortlist.

`count_replicated_subset` applies the same procedure after retaining only
input compound-target pairs with `n_contexts >= 2`. Its observed count
and all 100 null counts are zero; its empirical p-value is 1.

The table supports these summary calculations. Regenerating the complete
family selection and null requires the corresponding scoring and compound
filter inputs; see [methods and input access](../docs/ANALYSIS_ACCESS.md).
Family enrichment does not establish direct target engagement.
