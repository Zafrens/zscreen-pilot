# The computational ideas in plain language

## A recipe makes the chemistry comparable

Imagine testing combinations drawn from three lists of components. Many compounds share the first component but have different second and third components. Their measurements let you ask what tends to happen when that first component is present and how its partners change the outcome.

The public recipe records those choices with stable IDs. A component's chemical structure is not needed to group the recipes by identity. Structure information becomes useful for a different question: whether a previously untested chemical component might behave like a known one.

## A family profile combines evidence across related compounds

A building-block profile pools measurements from compounds sharing a component. It summarizes the response that appears across its partners. A pair profile narrows the question to two components together.

The [HSPA5 example](01_hspa5_building_block/README.md) checks agreement by dividing the member compounds into two groups and computing the RNA response from each group separately. Strong agreement means that the family pattern is shared across those different members. The halves share the same experiments. Their agreement measures family coherence; replication in new experiments is a separate test.

## A transcriptional program summarizes coordinated genes

A cellular response can change many genes together. A transcriptional program summarizes one recurring pattern of those changes. A program usage says how much that pattern contributes to one response.

The core release defines 32 shared patterns, allowing responses from different screens to be compared in the same coordinates. The gene-level profiles retain finer detail. A different RNA encoder can also produce 32 numbers, but those numbers only have meaning in the coordinate system that generated them.

## A genetic reference gives the search a biological objective

Perturbing a gene changes a cell's RNA response. That reference can be compared with responses to chemical interventions. A chemical profile may resemble the reference, oppose it, or share only part of it.

In the featured replay, the correspondence score is the quantity the search tries to increase. Functional assays can subsequently establish whether the response produces the biological outcome of interest.

## An interaction means that a component's effect depends on its partner

An additive model assumes that each component contributes its own effect independently. An interaction model allows a combination to behave differently from the sum of its parts.

The [partner example](02_partner_responses/README.md) illustrates this question through aggregate profiles. Its completed matched comparison leaves a causal switch unresolved. Matching the remaining recipe positions improves chemical comparability; measuring both partners together across balanced experimental blocks is needed to isolate the component change from measurement differences.

## A retrospective replay hides outcomes that have already been measured

The replay starts with an existing library but initially reveals only a small set of outcomes. A model chooses the next batch. The replay then reveals those recorded outcomes, updates the model, and repeats. Competing strategies can be compared using the same starting sample and measurement budget.

A frozen model keeps what it learned from the initial sample. An updating model learns again from the growing collection. Their difference measures the value of feedback within that experiment-selection procedure.

## Recovery and hit rate answer different questions

Recovery asks what fraction of a predefined desired set has been found. If the desired set contains 464 profiles and a strategy finds 46 of them, recovery is about 10%.

A hit rate instead divides the number of desired profiles found by the number tested. The [replay case study](03_adaptive_replay/README.md) reports recovery of the full library's highest-scoring 5%.

## Procedure improvement is a further learning loop

Model updating changes fitted parameters as observations arrive. Procedure improvement changes how the system learns or selects experiments—for example, which features it uses or how much it explores unfamiliar chemistry.

A useful test compares the revised procedure with its predecessor on fresh tasks that did not guide the revision. Prospective measurements then test whether that improvement helps discover useful new chemical interventions. These steps separate improvement in a computational procedure from validation in new experiments.
