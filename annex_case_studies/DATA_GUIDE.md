# Data behind the case studies

These small tables expose the exact values behind the three featured stories. All chemical coordinates use public building-block IDs. The package schemas are in the [data dictionary](../docs/DATA_DICTIONARY.md).

## 1. HSPA5-associated family

[series_summary.csv](01_hspa5_building_block/data/series_summary.csv) has one row for `bb0:BB_2371372935` in `zel039_aec7`.

| Fields | Meaning |
|---|---|
| `context`, `unit_id` | Context and recipe-defined group |
| `position`, `public_building_block_id` | The recurring component defining the group |
| `n_member_compounds`, `n_retained_cells` | Support after the retained-measurement filters |
| `member_split_pearson` | Gene-response correlation between two disjoint sets of member compounds |
| `genetic_reference_target`, `score_method`, `reference_match_score`, `raw_target_rank` | Genetic correspondence with the external reference named in the example |

The 1,512-member aggregate is a filtered measurement group. Selecting `bb0 == 'BB_2371372935'` in [core recipes](../core/recipes.parquet) returns 2,267 distinct compounds. This annex ships the filtered summary, not the complete filtered member list or the measurement inputs needed to reconstruct its membership from recipes alone.

## 2. Partner responses

| Table | Rows | Key and contents |
|---|---:|---|
| [recipe_coordinates.csv](02_partner_responses/data/recipe_coordinates.csv) | 4 | `coordinate`; maps S, S2, P1 and P2 to position and public building-block ID |
| [response_scores.csv](02_partner_responses/data/response_scores.csv) | 12 | (`context`, `core`, `partner`, `part`); HSPA5 and TRAF2 scores, their difference, retained cells and full-group membership |
| [group_support.csv](02_partner_responses/data/group_support.csv) | 4 | (`core`, `partner`); full/half retained cells, strata, distinct `bb2` values and profile correlation |
| [partner_contrasts.csv](02_partner_responses/data/partner_contrasts.csv) | 3 | `part`; P2-minus-P1 scores within S and S2 and their difference |
| [matched_endpoint_summary.csv](02_partner_responses/data/matched_endpoint_summary.csv) | 6 | Completed primary pair, scaffold-interaction and common-stratum endpoints; P1-minus-P2 orientation, sample sizes, intervals and sign-flip p values |

`part` is `full`, `h1`, or `h2`. The halves are disjoint sets of member compounds. `cells` refers to the displayed part; `members_full` always refers to the entire group, including on half rows. `profile_split_r` compares the two member-half gene-response profiles and is repeated for convenience.

The signed response score measures top-gene correspondence with a genetic perturbation reference. `HSPA5_minus_TRAF2` is the difference between its two genetic-reference scores. Positive values favor HSPA5; negative values favor TRAF2. Scores describe the complete groups or their recorded halves. A matched-coordinate reconstruction has a different input definition.

## 3. Adaptive replay

| Table | Rows | Key and contents |
|---|---:|---|
| [selection_curves.csv](03_adaptive_replay/data/selection_curves.csv) | 126 | (`campaign`, `feature_arm`, `acq_arm`, `seed`, `round`); cumulative selections and high-score recall |
| [selection_endpoints.csv](03_adaptive_replay/data/selection_endpoints.csv) | 6 | (`campaign`, `feature_arm`, `acq_arm`); mean/min/max final recall over three starts |
| [replay_definition.json](03_adaptive_replay/data/replay_definition.json) | Two tasks | Budget, starts, universe/test counts, denominator and source-result scope |

`round=0` is the initial 200-compound sample; rounds 1–6 add 200 each. `mains` uses component features and `pairs` adds pair features. Strategy labels map to these CSV keys and `policy_label` values:

| Display label | `acq_arm` | `policy_label` | Meaning |
|---|---|---|---|
| Updating model | `greedy` | `Update each batch` | Refit after each acquired batch |
| Frozen model | `static` | `Freeze initial model` | Keep the initial fit |
| Random selection | `random` | `Random` | Select randomly |

`cum_top5pct_capture` and the endpoint `*_recall_fraction` values lie on a 0–1 scale; multiply by 100 for percentages. The denominator is the highest-scoring 5% of the full recipe-available universe, including reserved test compounds. The test rows cannot be selected or used in supervised fitting.

The HSPA5 case uses `pairs`; the METTL3 case uses `mains`. The curve table records each policy's measured recovery over rounds. It supports plotting and endpoint comparisons; it is not a table of every per-compound acquisition score.

## Interpretation of matched results

The six rows in [matched_endpoint_summary.csv](02_partner_responses/data/matched_endpoint_summary.csv) describe pair, interaction and common-stratum comparisons. Their 95% intervals describe coordinate resampling in the measured set. The common-stratum subset and complete set answer different coverage questions. The summarized tables do not include all cell-level inputs needed to reconstruct the full-gene profiles.
