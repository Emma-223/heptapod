In some cases, a limit calculation will require greater accuracy than what we get from the AsymptoticLimits method of Combine.
In this case, we generate a "grid" (a list of values) for the signal strength `r` and run Combine in the HybridNew method for each point on the grid.

This is computationally intensive and should be run as HTCondor computing jobs.
A typical workflow to produce the condor submit and executable files is detailed below:

1. Estimate the appropriate r ranges -> `InitializeRRanges` (run one time to obtain r range for all masses / quantiles). Note: this is usually based on a calculation of the Asymptotic Limits. If you don't have an asymptotic limits file, you will need to create one first, following the instructions in **`asymptoticLimits.md`**.
3. Now run a loop over all requested masses and quantiles as follows:
    a. Look up the range for r for this specific mass and quantile -> `LookupRRange`
    b. Divide the range from (2) into the number of points specified by the user and divide the points into condor jobs -> `GetGridPoints`
    c. Write a Combine command, determining `method_specific_options` according to the instructions in **`frequentistLimits.md`** -> `WriteCombineCommand`
    d. Write the HTCondor submit and executable files for this mass and quantile -> `WriteGridGenerationCondorFiles`