# Scientific overview

Z-Screen combines a chemical recipe with measurements of the resulting cellular response. This guide describes the distributed pilot data, reference model and selected supporting analyses. Detailed transformations and evaluation settings are linked from their respective sections.

## Chemical design and core RNA data

Compounds are assembled from recurring chemical building blocks at defined positions. A public recipe specifies the block at each occupied position, `bb0`–`bb4`. The [recipe table](../core/recipes.parquet) contains 162,914 unique public compound IDs. The eight library–cell contexts contain 190,699 profiles in total:

| Context | Cell background | Compound-context profiles |
|---|---|---:|
| `zel024_hek293` | HEK293 | 13,914 |
| `zel024_h1650` | H1650 | 10,686 |
| `zel028_hek293` | HEK293 | 61,396 |
| `zel028_a549` | A549 | 40,622 |
| `zel028_h1650` | H1650 | 25,906 |
| `zel031_a549` | A549 | 8,321 |
| `zel031_thp1` | THP1 | 9,041 |
| `zel039_aec7` | AEC7 endothelial | 20,813 |

Source: [context and compound table](../core/splits/fold_assignments.parquet). A compound can occur in more than one cellular context.

The core RNA pipeline pools nanowell counts by compound and device, normalizes for total counts, subtracts the mean response on each device, and averages across devices. A **pseudobulk** is a count profile formed by pooling wells. A **device** is a measurement batch. The released harmonized matrices use a common 6,000-gene panel. [Core methods](METHODS.md) · [Gene panel](../core/surfaces/harmonized_6000_genes.parquet).

**Cell-line naming:** the Zafrens cell line is **AEC7**. AEC7 is closely related to **teloHAEC**, the cell line used for the external genetic reference. The comparison links AEC7 chemical-response measurements to teloHAEC genetic-perturbation profiles. External reference IDs retain their source names.

### Shared transcriptional programs

The 32 core programs are coordinated gene-expression patterns learned from the harmonized responses using semi-nonnegative matrix factorization. This method represents a response as a weighted combination of shared patterns. A **usage** is one of those weights. Each compound-context response therefore has both a gene-level profile and 32 program coordinates.

The same pinned basis defines `P01`–`P32` across the core contexts. The [hypothesis annex](../annex_hypotheses/README.md) adds biological interpretations, recurring components and controls. Its [annotation label namespaces](../annex_hypotheses/INTERPRETATION_NOTES.md) must not be treated as direct current-basis indices. The [basis registry](../core/basis/basis_registry.json) specifies the exact released basis; a 12-program companion supports coarser analyses.

The original recipe-to-program model and benchmark use fixed compound folds. Fold 0 was excluded from basis fitting and model training. Its checkpoints, predictions, and evaluation tables remain a reusable reference for learning from recipes. [Model guide](../models/README.md) · [Benchmark](../core/benchmark/README.md) · [Model and projection methods](METHODS.md).

## Selected response and learning examples

### A recurring component and a coherent response

The ZEL039 building-block family analysis pools cells from compounds sharing public building block `BB_2371372935`. The family contains 1,512 compounds and 5,373 retained cells. Its aggregate RNA response correlates at 0.9806 between disjoint halves of member compounds and has an HSPA5 genetic-response correspondence. These aggregate effects were calculated from source counts, separately from the core program projection. [Case study and exact summary](../annex_case_studies/01_hspa5_building_block/README.md).

### Partner-defined response differences

Two groups within that family share `bb0` and differ at `bb1`. Their full-group and member-half comparisons favor HSPA5 with partner P1 and TRAF2 with partner P2. The case-study tables preserve all four core/partner groups examined in the compound-family analysis. A separate matched analysis found measurement-support imbalance and an inconclusive 18-pair common-stratum sensitivity; the per-coordinate HSPA5 effect is uncertain. The aggregate difference remains exploratory, and a causal partner-dependent mechanism switch has not been established. [Case study and scores](../annex_case_studies/02_partner_responses/README.md).

### Learning from successive measurements

The retrospective HSPA5 and METTL3 campaigns hide existing response scores, reveal selected compounds in batches, and update a recipe-based predictor. Each strategy starts from the same 200 compounds and receives six further batches of 200. The comparison measures recovery of a fixed high-score set at equal selection budgets. The campaign split and response definitions are separate from the core model's five-fold split. [Case study](../annex_case_studies/03_adaptive_replay/README.md) · [Short methods and additional inputs](ANALYSIS_ACCESS.md).

## Which representation should I use?

| Layer | Biological or analytical unit | Representation | Useful for |
|---|---|---|---|
| Core RNA | Compound × library–cell context | Device-centered response on 6,000 genes; projection onto shared `P01`–`P32` | Comparing recipes, programs, and contexts; reference-model development |
| Family aggregate responses | Building-block or pair group within a context | Response rebuilt from source counts, with member-compound halves | Reproducibility of chemical-family effects and partner comparisons |
| Signed top-gene comparison (selected results only) | Chemical or aggregate response against a specified genetic reference | Signed top-gene correspondence on context-specific aligned gene axes: 36,591 genes for AEC7 and 25,375 for HEK293 | Interpretation of defined objectives; full score inputs are outside this package |
| Library imaging | Compound, detection, or other unit specified by the table | Image embeddings, marker intensities, or native image features | Relating morphology and markers to chemistry and RNA |
| Same-well experiment | (`batch_id`, `well_id`) | 448 image features and native RNA encoder coordinates `D00`–`D31` | Joint image/RNA analysis at a directly paired well |

The gene axes and normalization are part of a response's definition. Replacing the family-analysis bridge axes with the core 6,000-gene panel changes the analysis. Likewise, same-well `D00`–`D31` and core `P01`–`P32` belong to different learned representations. A genetic match identifies correspondence between RNA responses; direct molecular binding and useful biological function are separate experimental questions.

## Chemical and biological organization

The original atlas contains 1,007 chemical response families across eight contexts. Its graph combines shared recipe components, structural similarity, and program similarity. The families were formed without target labels; 855 have at least one significant pathway annotation. Use `(context, cluster_id)` to identify a family. [Verified family memberships and centroids](../atlas/original_clusters/README.md).

The [chemistry annex](../annex_chemistry/README.md) contains component effects, model attribution, series, and response-cliff tables. The [hypothesis annex](../annex_hypotheses/README.md) contains a program atlas, selected biological examples, and a broader follow-up ledger. These are complementary ways to move from a broad response pattern to specific chemistry.

## Genetic references and controls

The [phenomimicry annex](../annex_phenomimicry/README.md) supplies processed compound–genetic correspondence and calibration results. The HSPA5 and METTL3 learning examples use a distinct signed top-gene scoring representation. Full genetic-reference matrices, compact signatures and score-reconstruction inputs are outside this pilot package; [ANALYSIS_ACCESS.md](ANALYSIS_ACCESS.md) explains the methods and source access. The MSC1094308 annotation is [VCP/p97 and VPS4B](../annotations/README.md); known-target calibration uses the stated target assignments.

The [controls annex](../annex_controls/README.md) contains 35 named compounds across five contexts: 256,052 wells summarized into 1,259 control-by-batch pseudobulks. It supplies core-panel responses, program usages, counts, and batch metadata. These measurements support interpretation of response patterns and studies of measurement design.

## Imaging and paired measurements

The [library imaging annex](../annex_imaging/README.md) supplies embeddings, marker intensities, and available detection-level features. Its RNA comparisons use the shared core programs where specified in the evaluation table.

The separate [same-well study](../annex_same_well/README.md) contains 11,435 wells from two batches and 35 controls. Each well has an image summary and native RNA encoder coordinates. Image-to-RNA prediction reaches mean per-coordinate Pearson correlation 0.277 in the reported five-fold evaluation and 0.238 when each control is held out in turn. The [learning curve](../annex_same_well/evidence/learning_curve.csv) varies the **total wells sampled into each cross-validation dataset**. It provides an empirical starting point for asking how a larger paired dataset improves the cross-modal map.

### Selected measurement-design results

At a fixed 2,287-well test set, the [pairing comparison](../annex_measurement_design/README.md) trains on 350, 1,000, 3,000 or 8,000 paired wells. It removes control/batch means using training wells only. Mean residual RNA-coordinate correlation rises from 0.046 to 0.125 with exact pairing; within-control/batch shuffled pairing stays near zero. At 8,000 training wells the exact-pair mean R² is only 0.0029, so predictive gain should be described with that modest absolute fit.

The control study aggregates additional measured batches and compares each aggregate with a fixed, disjoint batch set. Agreement improves across four contexts; HEK293 clone supplies a single-batch comparison only; the sampling unit is a batch, not an individual cell. This is a within-source measurement-design result. [All curves and split tables](../annex_measurement_design/README.md).

The [gallery](../gallery/README.md) supplies two genuine ZS13 five-channel microscopy crops linked by public compound ID to HEK293 RNA profiles. The image source does not document its cell line; those examples are compound-linked observations, not a same-well RNA/image pair. The separate same-well dataset supplies the direct pairing evidence above.

## Reuse in new analyses

Use the [data dictionary](DATA_DICTIONARY.md) for schemas and matrix alignment, [core methods](METHODS.md) for transformations, and [reproduction guide](REPRODUCTION.md) for original worked examples. The [case-study data guide](../annex_case_studies/DATA_GUIDE.md) links the featured figures to exact values and source hashes. The [plain-language guide](../annex_case_studies/CONCEPTS.md) explains the computational ideas.

Versioned IDs, response definitions and figure inputs let new analyses build on the same pilot objects. Upstream genetic-response reconstruction requires the additional inputs described in [ANALYSIS_ACCESS.md](ANALYSIS_ACCESS.md).
