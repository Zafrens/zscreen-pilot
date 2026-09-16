# Chemical families and biological hypotheses

This annex organizes response patterns into candidates for follow-up: chemical components, related recipe series, program annotations and reference-control similarities. Start with the 16 curated entries in [anchor_leads.csv](anchor_leads.csv), using the [interpretation notes](INTERPRETATION_NOTES.md) for score definitions and separate program-label namespaces.

## Three useful examples

**A heat-shock family linked to a measured control — ZSH-0001.** In AEC7, 2,294 compounds carrying `bb0:BB_2085420374` support an HSF1/heat-shock pattern. The separately measured HTH-01-015 control is the reported rank-1 response match (cosine 0.631). Neighborhood, clustering and building-block effect summaries share a ridge-model basis; they are related views of the same family evidence, rather than three independent biological validations. The control's heat-shock response does not establish the library compounds' molecular targets.

**A genetic-reference calibration example — ZSH-3760.** The signed-rank analysis reports positive METTL3 correspondence for STM2457 and STC-15. Its z values belong to that scoring method. Cosine/consensus and ensemble scores are separate comparisons and need their own calibration. Retain this as a reference-response hypothesis, not a validated METTL3 mechanism for unnamed library compounds. [Processed correspondence tables](../annex_phenomimicry/README.md).

**A UPR-associated series with a local chemistry cliff — ZSH-3757.** On `bb0:BB_2371372935`, the 53-member `bb1:BB_8930974984` series has phenotype coherence 0.793 and nearest-neighbor correlation −0.328. Its deep-measurement fraction is 0.774. The other named series, 47 members with `bb1:BB_7908408907`, has coherence 0.961 but positive neighbor correlation +0.658, cliff percentile 0.18 and no deep-tier members. These are distinct observations; the latter is not a second replication of the former's cliff. [Exact series and cliff tables](../annex_chemistry/README.md).

## Tables and keys

| File | Rows | Use |
|---|---:|---|
| [anchor_leads.csv](anchor_leads.csv) | 16 | Curated entry points, public components, evidence summaries and proposed confirming experiments; join the current reading notes by `hypothesis_id`. |
| [program_atlas.csv](program_atlas.csv) | 26 | Response groups, gene themes, driving components, control/reference links and measurement-support diagnostics. Use `program_group_id`; its atlas P labels are not current basis row indices. |
| [sharp_sar_candidates.csv](sharp_sar_candidates.csv) | 133 | Shortlist of two-component series, small clusters and single-component groups. |
| [hypothesis_ledger_full.csv](hypothesis_ledger_full.csv) | 1,027 | Response-family hypotheses with stable IDs, evidence, control similarities and prioritization fields. Tier and status labels are not evidence of molecular target validation. |
| [interpretation_notes.json](interpretation_notes.json) | 3 | Interpretation of ZSH-0001, ZSH-3757 and ZSH-3760, keyed by stable hypothesis ID. |
| [program_label_namespaces.json](program_label_namespaces.json) | 26 groups | Explicit namespace for atlas program labels; no inferred mapping to the current shared basis. |

[Interpretation and label notes](INTERPRETATION_NOTES.md) explain the
score definitions and program namespaces. AEC7/ZEL039 measurements support
response-family interpretation; HEK293/ZEL024 SAR surfaces are largely
recipe-backbone estimates, so their series statistics describe that
representation. [Control annotations](../annotations/README.md) provide
primary-source pharmacology for interpreting control similarities.

[How to read the evidence](HOW_TO_READ.md) · [Methods and input access](../docs/ANALYSIS_ACCESS.md) · [External reference sources](../docs/REFERENCE_SOURCES.md).
