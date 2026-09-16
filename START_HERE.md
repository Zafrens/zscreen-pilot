# Start here

Use Z-Screen to connect a public chemical recipe with a measured cellular response. This pilot package contains the processed data and reference model needed for the core examples below.

## 1. Load RNA responses and recipes

Run from the full package root:

```bash
python -m pip install -e .
```

```python
from zscreen_program_package import data

usages, compounds = data.load_usages("zel024_hek293")
surface, surface_ids = data.load_surface("zel024_hek293")
basis = data.load_basis(k=32)
genes = data.panel_genes()
recipes = data.load_recipes()

assert compounds.equals(surface_ids)
linked = compounds.merge(recipes, on="public_compound_id", validate="one_to_one")
print(usages.shape, surface.shape, basis.shape)
# (13914, 32) (13914, 6000) (32, 6000)
```

Row *i* of each matrix matches row *i* of its supplied compound table. The gene panel supplies column labels. Helpers accept `root=` when called outside the package. [Notebook 1](examples/01_quickstart_usages.ipynb) · [Data dictionary](docs/DATA_DICTIONARY.md).

## 2. Run the reference model

```bash
python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[model]"
python models/predict.py --check-golden
python models/predict.py --context zel028_a549 --bb1 BB_0510191033 --bb2 BB_3460866978 --bb3 BB_1895570180 --bb4 BB_8135509566
```

The model predicts 32 program coordinates from a recipe and context. It returns standardized model output and the corresponding usage units. The `--check-golden` command compares predictions for 20 fixed recipes with the supplied values. CPU execution is sufficient. [Model requirements and methods](models/README.md).

The shared basis and reference model were fit with **fold 0 held out**. Use the released compound fold assignments when evaluating a new model; recipe reuse means a compound split and an unseen-building-block split answer different questions. [Benchmark definitions](core/benchmark/README.md).

## 3. Choose a worked notebook

| Notebook | Task |
|---|---|
| [01 — Quickstart](examples/01_quickstart_usages.ipynb) | Load and align core responses and inspect program genes |
| [02 — Benchmark](examples/02_reproduce_benchmark.ipynb) | Check fold assignments and the scale of the reported permutation null |
| [03 — Hypotheses](examples/03_browse_hypotheses.ipynb) | Browse annotated hypotheses and their evidence tiers |
| [04 — Imaging](examples/04_join_imaging.ipynb) | Join imaging features to RNA and check a saved prediction score |

Notebook execution requires `python -m pip install -e ".[notebooks]"`. [Reproduction guide](docs/REPRODUCTION.md) gives the corresponding short code examples and distinguishes checks of distributed objects from reconstruction of upstream research analyses.

## Explore the atlas

| Start with… | Open… | Ask… |
|---|---|---|
| A chemical building block | [Recipes](core/recipes.parquet), [component effects](annex_chemistry/README.md) | Which measured partners and contexts share its response? |
| A cellular response family | [Original members and centroids](atlas/original_clusters/README.md) | Which compounds and pathways characterize the group? |
| An annotated program or hypothesis | [Hypothesis guide](annex_hypotheses/README.md) | What evidence and follow-up experiments support it? |
| A familiar reference compound | [Control measurements](annex_controls/README.md) | How does the response vary across contexts and batches? |
| A genetic-response comparison | [Processed phenomimicry results](annex_phenomimicry/README.md) | Which RNA patterns resemble the reference, under the stated scoring method? |
| Images or markers | [Imaging](annex_imaging/README.md), [microscopy gallery](gallery/README.md) | Which features are linked at the compound or observation level? |
| Directly paired measurements | [Same-well data](annex_same_well/README.md) | How do image and RNA features relate in the same well? |

[All annexes and their limits](docs/ANNEX_INDEX.md) · [Scientific overview](docs/SCIENTIFIC_OVERVIEW.md).

## Read a compact example

The [HSPA5-associated family](annex_case_studies/01_hspa5_building_block/README.md) illustrates a coherent aggregate response. Its [partner comparison](annex_case_studies/02_partner_responses/README.md) is exploratory, and its [retrospective selection curves](annex_case_studies/03_adaptive_replay/README.md) illustrate selection against a fixed RNA-response score. The [case-study data guide](annex_case_studies/DATA_GUIDE.md) identifies the values behind each figure.

## Keep the representations distinct

- A **recipe** lists building blocks at occupied positions `bb0`–`bb4`; structures are not included.
- A **context** is a library–cell-line combination. Keep `context` when comparing profiles, and join compounds using `public_compound_id`.
- Core **program usages** `P01`–`P32` refer to the pinned [shared basis](core/basis/basis_registry.json). Program annotation labels may require the mapping documented in the relevant annex.
- The same-well key is **(`batch_id`, `well_id`)**. Its native RNA coordinates `D00`–`D31` are a separate representation from core programs.
- A **genetic-response match** compares RNA patterns. Its target label is a mechanism hypothesis, not a direct binding result.

[Plain-language concepts](annex_case_studies/CONCEPTS.md) · [Normalization and models](docs/METHODS.md).

## Additional inputs and reuse

Core examples run with the distributed inputs. Additional upstream analyses require their corresponding raw/reference data. For raw Z-Screen data and related analysis inputs, contact [hello@zafrens.com](mailto:hello@zafrens.com); obtain external genetic datasets from their original providers. [Analysis and access note](docs/ANALYSIS_ACCESS.md) · [Component terms](LICENSE.md).
