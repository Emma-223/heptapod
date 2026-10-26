In some cases, a limit calculation will require greater accuracy than what we get from the AsymptoticLimits method of Combine.
In this case, we generate a "grid" (a list of values) for the signal strength `r` and run Combine in the HybridNew method for each point on the grid.

This is computationally intensive and should be run as HTCondor computing jobs.
A typical workflow to produce the condor submit and executable files is detailed below:

1. Estimate the appropriate r ranges -> `InitializeRRanges` (run one time to obtain r range for all masses / quantiles). Note: this is usually based on a calculation of the Asymptotic Limits. If you don't have an asymptotic limits file, you will need to create one first, following the instructions in **`asymptoticLimits.md`**.
2. Now run a loop over all requested masses and quantiles as follows:
    a. Look up the range for r for this specific mass and quantile -> `LookupRRange`
    b. Divide the range from (2) into the number of points specified by the user and divide the points into condor jobs -> `GetGridPoints`
    c. Write a Combine command. The method will be `HybridNew`, and the method specific options will be as follows:
       - You MUST include `--LHCmode LHC-limits --saveHybridResult --saveToys`
       - You should specify the number of toys as `-T [number]`
       - IF the quantile is >0, you MUST include `--expectedFromGrid=[quantile]`
       - example (0.16 quantile): `method_specific_options="--LHCmode LHC-limits --saveHybridResult --saveToys -T 30000 --expectedFromGrid=0.16"`
       - example (observed, coded as -1 quantile): `method_specific_options="--LHCmode LHC-limits --saveHybridResult --saveToys -T 10000"`
    d. Write the HTCondor submit and executable files for this mass and quantile -> `WriteGridGenerationCondorFiles`