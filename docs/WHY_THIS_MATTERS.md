# Why this pilot matters

## A chemical library is also an experimental design

A combinatorial library reuses chemical components in many combinations. That repetition lets researchers hold a component fixed, vary its partners and compare the resulting cellular responses.

Z-Screen connects public recipes to high-dimensional RNA measurements, with imaging and controls in the available contexts. The pilot contains 162,914 recipes and 190,699 compound-context profiles. Its shared 6,000-gene and 32-program representations provide a consistent starting point for exploring chemical effects and training predictive models. [Data overview](SCIENTIFIC_OVERVIEW.md).

## Recurring components make response families inspectable

The original atlas contains 1,007 chemistry-constrained response families. V2 supplies explicit members and centroids alongside the existing pathway census, so a reader can move from a group-level claim to its constituent compounds and measured profiles. [Original atlas](../atlas/original_clusters/README.md).

One compact example is the AEC7 family containing building block `BB_2371372935`: 1,512 compounds and 5,373 retained cells yield aggregate profiles that correlate at 0.981 between disjoint member-compound halves. The halves share the source experiment collection. The HSPA5-associated RNA pattern supplies a biological reference for further study; it does not establish HSPA5 binding or inhibition. [Family example](../annex_case_studies/01_hspa5_building_block/README.md).

Partner-defined groups show different aggregate reference preferences, motivating balanced chemical comparisons. The more restrictive common-stratum sensitivity is inconclusive, so a causal partner-dependent mechanism switch has not been established. [Partner example](../annex_case_studies/02_partner_responses/README.md).

## The same measurements support model development

The reference model predicts a response's 32 program coordinates from its public recipe and context. Checkpoints, embedding inputs, fixed folds and inference code make this an immediate worked example. Researchers can compare other recipe representations or ask where predictions transfer across contexts. [Model guide](../models/README.md) · [Benchmark](../core/benchmark/README.md).

Retrospective selection curves illustrate a related use: selecting compounds according to a fixed RNA-response objective and updating the model after observations arrive. This is a retrospective example of learning from feedback. [Learning example](../annex_case_studies/03_adaptive_replay/README.md) · [Methods and access](ANALYSIS_ACCESS.md).

## Quantitative results and comparable resources

Held-out recipe predictions reach mean per-program Pearson **0.105–0.530** across eight contexts (**z = 6.1–28.1** under the recorded permutation null). The separate fold-0 comparison finds simple recipe models and the reference transformer each ahead in four contexts. Held-out-building-block and imaging evaluations add complementary evidence. [Exact selectors, results, and source tables](PILOT_RESULTS_REFERENCE.md).

The nominal `zel028` recipe grid contains **673,728 combinations**, of which **117,950** are observed somewhere in the three measured contexts. The [design arithmetic](PILOT_RESULTS_REFERENCE.md#combinatorial-design-arithmetic) distinguishes library-wide vocabulary from context-specific coverage and from synthesis feasibility. A [primary-source resource comparison](PILOT_RESULTS_REFERENCE.md#relation-to-complementary-public-resources) places the pilot alongside LINCS, PRISM, Tahoe-100M and JUMP Cell Painting by measurement purpose.

## What scaling could answer

| Expand… | To investigate… |
|---|---|
| Chemical combinations | How recurring component effects depend on their partners |
| Measurements per combination | Which weak or variable responses stabilize with additional support |
| Cellular settings | Which responses transfer and which depend on context |
| Paired images and RNA | How molecular responses relate to cellular form and heterogeneity |
| Prospective learning rounds | Whether selection improves when new measurements inform the next experiments |

The [design-space figure](../figures/measured_and_nominal_design_space.png) distinguishes observed coverage from nominal combinations of available blocks. The [measurement-design annex](../annex_measurement_design/README.md) provides existing pairing and batch-accumulation results, with their sampling units and modest absolute prediction fit stated. These pilot results motivate experiments; they do not establish universal scaling laws.

## Build on the data

Use the core resource to develop a model, explore a family, join an imaging measurement, or formulate a biological follow-up. Public IDs and explicit matrix axes keep those analyses tied to the same objects. [Start Here](../START_HERE.md) · [Annex index](ANNEX_INDEX.md).

For a new library, deeper measurements, structure-level chemistry or related analysis inputs, contact [hello@zafrens.com](mailto:hello@zafrens.com).
