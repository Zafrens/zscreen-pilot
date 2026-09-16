# Analysis methods and data access

The download contains processed Z-Screen measurements, public chemical recipes, reference models, four notebooks, and selected analysis tables/figures. Core loaders, model inference, package verification, atlas centroid checks and microscopy-gallery generation use included inputs. Each annex identifies its observation unit, representation and result definitions.

## Chemical–genetic correspondence

1. Construct an RNA-response signature for a genetic perturbation using the source study's controls and quality filters.
2. Construct chemical response signatures and align the gene axes for the selected chemical/genetic contexts.
3. Calculate correspondence with the method stated for that result. The multi-reference consensus method in the [phenomimicry annex](../annex_phenomimicry/README.md) differs from the signed top-gene overlap used in the [family and selection examples](../annex_case_studies/README.md).
4. For retrospective selection, learn a fixed correspondence score from recipes, reveal observations in equal-sized batches, and compare Updating model, Frozen model and Random selection at equal budgets.

In plain language, genetic perturbations supply reference RNA patterns, chemical measurements supply observed responses, and recurring recipe components help a model rank combinations. The match provides a biological hypothesis. Direct target engagement or a prospective discovery rate requires additional experiments.

## Representations and input coverage

The core RNA surface is a device-centered, harmonized **6,000-gene panel**. The signed top-gene family/selection comparisons use count-derived signatures aligned over **36,591 genes for AEC7** and **25,375 for HEK293**. Substituting the core panel changes the score. The full count-derived chemical signatures and original genetic-reference matrices are not distributed here; the package supplies the processed results and their definitions. The four core notebooks and reference model do not require those upstream inputs.

The family/selection examples use the original studies listed in [Public reference studies](REFERENCE_SOURCES.md). Use **AEC7** for Zafrens chemical measurements and **teloHAEC** for the endothelial genetic reference; the HEK chemical and HEK293T genetic contexts also remain distinct.

## Request additional inputs

For raw Z-Screen measurements, additional analysis inputs, chemical structures or collaboration enquiries, contact [hello@zafrens.com](mailto:hello@zafrens.com). Identify the context, public compound IDs or analysis, package version and intended use. Obtain external genetic datasets from their original providers under their terms.

[Data dictionary](DATA_DICTIONARY.md) · [Worked reproduction examples](REPRODUCTION.md) · [Licenses](../LICENSE.md).
