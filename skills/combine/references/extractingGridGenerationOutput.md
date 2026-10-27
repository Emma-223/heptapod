Once we have generated a grid as in **`references/gridGeneration.md`**, we need to extract the limit output from the grid.
Use `WriteExtractLimitOutputCondorFiles` to write the necessary condor.sub and condor.sh files for this step. 

IMPORTANT: The file `gridGen/[mass]/[quantile]/expected_output_files.json` MUST exist and ALL of the output files listed in `expected_output_files.json` MUST exist. You can check this by calling `CheckJobOutput` with the appropriate mass and quantile, and `output_directory=gridGen`.

For the combine command, the method should be `HybridNew`. The method specific options will be as follows:

- You MUST include `--LHCmode LHC-limits`
  
- If the quantile is >0, you MUST include `--expectedFromGrid=[quantile]`
  
- Example (0.5 quantile): `method_specific_options="--LHCmode LHC-limits --expectedFromGrid=0.5"`
  
- Example (observed, coded as -1 quantile): `method_specific_options="--LHCmode LHC-limits"`

This tool has options to save two additional outputs which can be useful for debugging:

1. A plot of CLs vs r (called a 'scan range' plot, as it shows the range of r values that we scanned over). Use `make_plot=True` to save this plot.
2. The distributions of the test statistic for each value of r that we scanned over. Use `save_test_stats=True` to save these plots.