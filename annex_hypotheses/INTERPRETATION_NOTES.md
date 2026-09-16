# Interpreting hypothesis scores and program labels

## Selected response-family hypotheses

| Stable ID | Interpretation |
|---|---|
| `ZSH-0001` | A heat-shock family with a separately measured HTH-01-015 control connection. Neighborhood, cluster and building-block effects share a ridge-model basis, so their agreement is not three independent biological validations. The phenotype does not identify library compounds as NUAK1/ROCK inhibitors. |
| `ZSH-3757` | The 53-member `BB_8930974984` series on `BB_2371372935` has coherence 0.793, ring-1 correlation −0.328, cliff percentile 1.00 and deep-tier fraction 0.774. The 47-member `BB_7908408907` series has coherence 0.961, ring-1 correlation +0.658, cliff percentile 0.18 and deep-tier fraction 0. These are distinct series with different evidence. |
| `ZSH-3760` | The recorded +8.8 to +16.1 z values describe a signed-rank comparison. They are distinct from cosine/consensus and ensemble scores. Method-specific resemblance does not establish METTL3 inhibition by library compounds. |

[Machine-readable notes](interpretation_notes.json) link these stable IDs
to the relevant tables. [Control target annotations](../annotations/README.md)
distinguish known pharmacology from response resemblance.

## Program labels use separate namespaces

[program_atlas.csv](program_atlas.csv) describes 26 response groups. Its
`primary_program` and `member_programs` labels belong to namespace
`zscreen_program_atlas_groups`; they are not row indices of
`core/basis/shared_basis_k32.npy`. Identify a group by `context` and
`program_group_id`, and interpret its genes, gene-set annotations and
recipe associations together.

[program_label_namespaces.json](program_label_namespaces.json) lists the
atlas labels and leaves `current_shared_basis_program` null because no
validated mapping is supplied. Use the core basis registry for current
array columns P01–P32. Join different representations only through a
documented mapping, not by matching their printed program numbers.
