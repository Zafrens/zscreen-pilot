# Reading the hypothesis tables

## Begin with the chemical unit

A building-block effect summarizes compounds sharing a component at a recipe position. A two-component series narrows that group. These are useful units for this combinatorial pilot; a family association is not a confirmed effect in every individual compound. Public IDs identify recipe relationships without assigning undisclosed chemical structures.

## Read the score with its comparison

Coherence measures agreement among the displayed profiles. Null statistics compare that agreement with the specified random sets. Rank identifies which reference is most similar within the tested panel. None of these statistics alone establishes a molecular target.

The gene-label permutation for level-to-control matching is permissive: 88–98% of levels match some control at p≤0.01. Read the matched control, response genes, depth composition and shared model structure together. Neighborhoods, clusters and building-block effect vectors can reuse the same ridge-derived profiles; agreement between them is not independent biological replication. A printed p=0.000 under a finite number of permutations does not mean zero probability.

## Keep the representations separate

- **AEC7/ZEL039:** inspect the size/depth-matched nulls and each candidate's depth-tier composition. Matching a broad tier does not remove every measurement difference.
- **HEK293/ZEL024 SAR:** `grammar_level` identifies recipe-backbone profiles with approximately zero individual own-data weight in that analysis. Coherence in those surfaces is evidence about the representation, not separate replication of each compound response.
- **ZEL028 contexts:** singleton measurements support pooled component-level reads; individual-compound confirmation requires further measurements.
- **Program labels:** the `program_atlas.csv` labels have their own namespace. Read [INTERPRETATION_NOTES.md](INTERPRETATION_NOTES.md) before joining them to core P01–P32 coordinates.

## Read external correspondence by method and context

[annex_phenomimicry](../annex_phenomimicry/README.md) contains cosine/consensus and ensemble results against external perturbation references. Its query rows reuse controls and reference datasets. They are not independent cells or experiments, and the ledger’s signed-rank scores are not interchangeable with these cosine/consensus or ensemble scores.

Read [control target annotations](../annotations/README.md) together with
the notes keyed by `hypothesis_id` in [interpretation_notes.json](interpretation_notes.json).

## Use the proposed experiment as the next decision

`kill_confirm_experiment` records a proposed follow-up, not completed validation. Tiers A/B/C and labels such as `hypothesis_anchor_validated` describe table prioritization and supporting evidence; they are not claims of molecular target validation. The present package supports response-family and mechanism hypotheses; target engagement, therapeutic activity and clinical claims need their own evidence.

Full upstream reconstruction is separate from this processed annex. [Methods and input access](../docs/ANALYSIS_ACCESS.md) · [Reference sources](../docs/REFERENCE_SOURCES.md).
