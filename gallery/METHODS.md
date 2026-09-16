# Gallery selection and rendering methods

## Source and identity

The source is `ZS13.h5`, dataset `images`, with shape `(10661, 5, 340, 340)` and dtype `float32`. The crop row index joins to exported `fov_metadata.parquet` and `crop_marker_intensities.parquet`. Public compound IDs join to `core/recipes.parquet` and the row key for `core/usages/usages_zel024_hek293.npy`. The script checks all four available source component IDs against the corresponding core recipe positions. The source marker documentation contains no image-cell-line field; the public registry retains `source_image_cell_line: null`.

Two selected channel arrays were extracted without changing dtype or values. Their element values were compared exactly with the corresponding HDF5 slices during extraction. The [raw registry](data/raw_crop_registry.json) stores file SHA256 and C-order value SHA256 separately, the public compound, panel, dataset and crop index, plus source metadata hashes. The complete source image archive is not part of this small gallery; the two numerical arrays suffice to reproduce its rendering.

## Deterministic selection

All choices are specified in [config.json](config.json), which was written before the images were previewed.

1. Start with all 13,914 measured RNA rows in `zel024_hek293`. For each of 32 programs, subtract the context median and divide by the context standard deviation.
2. Define a source-valid crop as panel ZS13, non-control, uncensored, mapped to the compound master, with at least one segmented cell and finite nonnegative mean intensities for p21, phalloidin, DAPI and p62. Retain only rows joined to the RNA context with matching component IDs. This leaves 7,136 crops.
3. Enumerate each distinct component at each recipe position. An eligible family has at least 100 RNA-measured compounds and at least five candidate representatives with at least three valid crops each. The frozen rule yields 68 eligible families.
4. For each family, calculate the coordinate-wise median standardized 32-program vector and its Euclidean norm. Select the highest-norm eligible family. Select the lowest-norm other eligible family at the same position as comparator. Ties use position then public component ID.
5. Within each family, select the image-supported compound with the smallest Euclidean distance to that family's median vector. Break a tie by public compound ID. Family medians use all family compounds, including those without usable images.
6. For each selected compound, transform its valid crop marker means using `log1p`, divide each marker by its panel-wide interquartile range across valid joined crops, and select the crop nearest the coordinate-wise median of that compound's marker vectors. Break a tie by source crop index.

Thus family choice is RNA-guided, member choice measures proximity to a family response, and crop choice measures proximity to the member's typical marker profile. None of the choices is optimized for visual contrast. Marker values are used solely for representative display, not as predictors of a marker endpoint.

## Display transformations

Each numerical crop is loaded and verified before display. Within each channel, common lower and upper grayscale values are the configured 0.5th and 99.5th percentiles pooled across the two selected crops. Values outside those limits saturate only in the rendered figure; the `.npy` files retain all original values. No spatial crop, smoothing, per-row contrast adjustment, channel subtraction, segmentation-mask filtering or pixel correction is applied. Pixel size is not established by these input tables, so the figure has no micron scale bar.

The RNA plot shows selected-compound usage and family-median usage after the context standardization defined above. Both panels use the same y-axis scale. All 32 programs are shown, and no program was selected after viewing the result.

## Interpretation

Two representative images are a provenance-linked illustration, not a test of marker modulation. Component membership is observational and can be confounded by partner components. The gallery can motivate an experiment with additional compounds, matched recipes, and independent replicate imaging; it cannot supply target engagement or isolate the component's causal effect.
