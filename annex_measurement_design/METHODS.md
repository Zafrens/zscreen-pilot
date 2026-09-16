# Measurement-design methods

The paired-well analysis uses [same_well_wells.parquet](../annex_same_well/same_well_wells.parquet). Batch accumulation uses the control pseudobulk metadata and count arrays in [annex_controls](../annex_controls/README.md). Result tables, sample selections and batch partitions are listed in the [data guide](DATA_GUIDE.md). Exact numerical settings are in [analysis_settings.json](analysis_settings.json).

## Exact pairing versus matched shuffling

The 11,435 paired wells are split within 70 control-by-batch strata into 9,148 training-pool wells and 2,287 held-out test wells. The split seed is 20260915. At training sizes 350, 1,000, 3,000 and 8,000, three proportional stratified samples are selected without replacement. Each stratum contributes at least one well.

Within each training sample, image and RNA values are centered by the training control/batch mean, then divided by training residual standard deviations. Those fitted means and scales are applied to the held-out wells. A ridge model uses penalty 100 and no additional intercept to predict the 32 native RNA coordinates D00–D31 from the 448 image coordinates.

Each exact-pair fit is compared with five fits that permute residual RNA rows within its training control/batch strata. The training well identities and correctly paired test wells stay fixed. The primary endpoint averages Pearson correlation across the 32 held-out RNA coordinates. The secondary endpoint averages per-coordinate R² with the test-mean denominator. These endpoints concern native RNA coordinates; they are distinct from the core gene-program basis.

## Accumulating control batches

Counts are normalized as `log1p(count / total_umis * 10000)`, using each pseudobulk's full-axis UMI total. Within each context, the control population is the intersection present in every batch; that same population centers each batch. Acquisition and held-out profiles use equal batch weights.

Half the batches are held out for reference. For each acquisition size, subsets of acquisition batches are compared with that disjoint reference. Up to 120 possible subsets are all enumerated; otherwise 100 subsets are sampled. The primary endpoint is the median control-profile Pearson correlation across the 6,000-gene panel. The program endpoint uses least-squares projections onto the shared 32-program basis. Summary tables average the endpoint across the subsets at each size.

The main figure and table use split seed 20260915. Partition sensitivity uses seeds 20260915–20260934. The random seed for each context adds 100,000 times its zero-based position in the declared context list. [Saved partitions](evidence/batch_partitions.csv) and [subsets](evidence/batch_subsets.csv) identify the batches used in every comparison.

## What these comparisons establish

Pairing changes image-to-RNA correspondence at a fixed training size. Accumulation changes the number of acquisition batches while keeping the reference batches disjoint. The sample-size curve changes the total number of wells used in cross-validation. These are different questions; none should be substituted for another. Overlapping partitions and resampled training starts are not independent biological experiments.
