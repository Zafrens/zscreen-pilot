# Annex index

The core RNA matrices, recipes and reference model are the main reusable objects. These annexes provide complementary measurements and selected analyses. A reported correspondence or model output has a different meaning from a directly measured response.

| Annex | Inputs and result type | Question it helps answer | Interpretation limit |
|---|---|---|---|
| [Controls](../annex_controls/README.md) | Named-control measurements; batch metadata; processed RNA and program profiles | How repeatable and context-dependent are familiar responses? | Each profile is a control-by-batch aggregate; repeated partitions of the same batches are sensitivity checks |
| [Imaging](../annex_imaging/README.md) | Image embeddings, markers, detection features and saved held-out predictions | What do morphology and markers add to RNA/recipe analyses? | Read observation unit, panel and pairing metadata before joining; marker pixels can already be present in embeddings |
| [Same-well](../annex_same_well/README.md) | Directly paired image and native RNA features; processed evaluations | What information do the two measurements share in one well? | Two batches and 35 controls; native RNA coordinates differ from core programs |
| [Chemistry](../annex_chemistry/README.md) | Measured or recipe-level component/series summaries and model attribution | Which recurring chemical choices are associated with response? | Evidence level varies by context and support; pooled effects do not validate each compound |
| [Clusters](../annex_clusters/README.md) and [members/centroids](../atlas/original_clusters/README.md) | Chemistry-constrained response families, pathway census and explicit membership | Which compounds form related response families? | Graph construction uses chemistry as well as response; target/pathway annotations are interpretations |
| [Hypotheses](../annex_hypotheses/README.md) | Annotated programs, selected leads and the broader hypothesis ledger | Which follow-up questions does the pilot motivate? | Evidence tiers and program-label namespaces must be read with the rows |
| [Phenomimicry](../annex_phenomimicry/README.md) | Processed chemical–genetic correspondence and calibration tables | Which RNA responses resemble genetic references or lie in the opposing standardized-score tail? | Hypothesis-generating; source contexts, nulls, annotations and source terms remain relevant |
| [Case studies](../annex_case_studies/README.md) | Selected family/partner summaries and retrospective selection results | How can recurring chemistry and observations guide exploration? | Family coherence, partner association and retrospective score recovery are distinct claims |
| [Measurement design](../annex_measurement_design/README.md) | Exact-pair/shuffled-pair and batch-accumulation results, sample indices and figures | What can pairing and measurement support contribute? | Modest absolute prediction fit; within-source experiments do not establish universal scaling laws |
| [Microscopy gallery](../gallery/README.md) | Two original five-channel crops, selection inputs and compound-linked RNA coordinates | What do identified observations look like? | Image source cell line is unspecified; RNA is linked by compound/library, not by the same well |

## Cross-cutting documentation and figure inputs

| Resource | Contents | Interpretation |
|---|---|---|
| [Annotations](../annotations/README.md) | Current control targets, mechanisms and primary citations | MSC1094308 is annotated to VCP/p97 and VPS4B; response correspondence alone does not establish direct targeting |
| [Overview figures](../figures/README.md) | Platform count JSON, per-context nominal-design CSV, PNG/SVG figures | Nominal independent combinations are distinct from measured coverage and synthesis feasibility |
| [Quantitative results](PILOT_RESULTS_REFERENCE.md) | Table selectors and arithmetic for benchmark, imaging and design results | Evaluation splits, model choices and measurement units must accompany reported values |

Core objects can be loaded and the reference model run directly. Selected annexes provide processed evidence rather than all upstream research workflows. [Reproduction guide](REPRODUCTION.md) · [Additional inputs and source access](ANALYSIS_ACCESS.md).
