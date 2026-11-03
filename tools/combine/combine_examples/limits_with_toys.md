# Example prompts to run limits with toys

This follows the procedure in the Combine documentation here: [https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/part3/commonstatsmethods/#complex-models](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/part3/commonstatsmethods/#complex-models)

The tools use an LHC style test statistic (i.e. they add the options `--LHCmode LHC-limits`)

## Comment about logging

If you are going to loop over many masses and quantiles, it can be helpful to instruct the agent to keep a log of what it has done and where the output files are located for each mass/quantile.

In addition to the files output by Combine, the tools force the following output to be saved for each mass/quantile:

- The exact Combine command that was used in this step
- For condor jobs, a list of expected output files
- For grid generation, the list of grid points that were scanned

## Generate grid of test statistic distributions

Assuming you have a file `r_ranges.json` with the range you wish to scan over for each mass, this prompt should generate the condor.sub and condor.sh files to generate a grid of test statistic distributions for the specified number of r points in the provided range:

```
For masses 1500, 1600, 1700, 1800 and 1900, use the r ranges in `r_ranges.json` to determine the grid points, then write the HTCondor submit and executable files for grid generation. Keep a log in GridGenLog.md with the location of all condor.sub and condor.sh files for each mass.

This step are HTCondor jobs. I want 25 points total with 5 points in each job.

I only want the 0.5 and observed (-1) quantiles.

Use 1000 toys

I want the options --rAbsAcc 0.001 --setParameters signalScaleParam=[scale_factor] --freezeParameters signalScaleParam --fullBToys
Where scale_factor depends on the mass and is read from signalScaleFactorsByMass.json.
```

The r range, number of points, and job splitting have default values:

- r from 0 to 20
- 50 points
- 10 points run in each HTCondor job

## Extract limit output

We can generate a new set of condor files to extract the limit output and plot the test statistic distributions:

```
I have previously generated a grid, and now I need you to write the condor submit and executable files to extract the output. Keep a log in extractLimitsLog.md with the locations of the condor files for each mass.

This will run as condor jobs.

I want masses 1500, 1600, 1700, 1800 and 1900. For each mass, I want the 0.5 and observed (-1) quantiles.

I want to add the options --rAbsAcc 1e-05 --rRelAcc 0.005 --setParameters signalScaleParam=[scale_factor] --freezeParameters signalScaleParam
Where scale_factor depends on the mass and is read from signalScaleFactorsByMass.json.

I want to make the scan range plot and save the test statistic distributions.
```

The `ReadLimitOutputTool` and `CollectResultsTool` work for both asymptotic limits and limits with toys, so we can collect results like:

```
Read the limit results from the jobs. Then, collect the results into a single json file and print a table of the limit results for all masses and quantiles that we calculated
```

## Plots

See [https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/part3/commonstatsmethods/#plotting](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/part3/commonstatsmethods/#plotting)

- We save the limit scan plot by default.
- If the user requests to save the test statistic distributions, we add the command for this to the condor.sh file for extracting the limit results, and an extra `test_stat_distributions.root` file is included in the job output.

If you choose to save the test statistic distirbutions, there is a tool to print plots of the test statistic distributions for a given mass/quantile *after* the condor job finishes running. It can save plots as pdfs, pngs, or both.

```
Plot the test statistic distributions for mass 1500, quantile 0.5. I need them as PDF files.
```