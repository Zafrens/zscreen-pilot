# Package overview figures

- [platform_overview.png](platform_overview.png) and [SVG](platform_overview.svg): conceptual route from recurring chemical recipes to measurements and experimental choices. This is an overview, not a performance result.
- [platform_counts.json](platform_counts.json): the data counts used in the overview (162,914 public compounds; 190,699 compound-context profiles; eight contexts; 6,000 genes; 32 programs).
- [measured_and_nominal_design_space.csv](measured_and_nominal_design_space.csv): one row per context; observed compounds, observed per-position vocabulary counts, their independent product, and observed/product fraction.
- [Design-space PNG](measured_and_nominal_design_space.png) and [SVG](measured_and_nominal_design_space.svg): plots of that per-context table.

Zero vocabulary count means an unoccupied position and contributes a factor of one to the nominal product. The grid does not guarantee synthesis feasibility or response measurement. The total here is 2,079,661 nominal states; the alternative library-union calculation is 2,095,149. [Exact arithmetic and scope](../docs/PILOT_RESULTS_REFERENCE.md#combinatorial-design-arithmetic).
