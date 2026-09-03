---
name: combine
bundle: combine
description: Run CMS Combine to perform statistical analysis tasks and plot results.
---

# Common terminology

- Limits: Boundaries on some parameter of interest. See below section "Limits".
- Mass hypothesis: the mass of a particle which has not been observed experimentally. We often set limits as a function of mass hypothesis.
- Signal strength: A fraction of the event yield for the signal process. For example, if the signal prediction is 10 events, a signal strength of 0.5 would correspond to 5 events and a signal strength of 1.5 would correspond to 15 events.

# Limits
One of the most common tasks in CMS Combine is setting limits on possible values for a parameter of interest.
Usually, this parameter is the signal strength, called `r`.

When we search for a new particle, we set an upper limit on `r`.
That is, our calculation returns that `r` must be less than some value.

There are two varieties of limits: expected and observed.

- The observed limit is one number.
- The expected limits are one number for each quantile and the median: 0.025, 0.016, 0.5, 0.84, and 0.975. 0.5 is usually called the median expected limit.
- In Combine, sometimes the observed limit is coded internally as the quantile -1. 

Typically, we calculate limits for several different values of some physical quantity, such as signal mass hypothesis. 

# Building a command in CMS Combine

All commands in CMS Combine follow a common format:

`combine -d [datacard] -M [method] -m [mass] --seed [seed] [method specific options] [other options]`

From the user input, you need to determine method, mass, seed, method specific options and other options.

Method: dictates which task Combine will run. For example, will it produce limits, or run a significance calculation, or do a likelihood scan? This can be one of:
    - AsymptoticLimits
    - HybridNew
    - MultiDimFit

Mass: the signal mass hypothesis for the physics process being studied. If you include this argument, Combine will put the mass in the name of the output root file. This is useful for keeping your files organized.

Seed: the seed Combine will use for randomization. Use -1 unless the user tells you to use a specific seed.

Method specific options: An option or combination of options specific to a given Combine method. Put these options into a single string to give to WriteCombineCommand.

Other options: In some cases, the user may specify additional options they want you to use. Put these options into a single string to give to WriteCombineCommand. 

Below are details on how to perform specific tasks.

## Asymptotic Limits

    - Set the method argument to AsymptoticLimits. 
    - No other options are reuqired unless the user specifies them.
    - It is important to know that this calculates all quantiles of expected limits and the observed limit.

## Frequentist Limits (also called limits with toys) - simple models

    - Set the method argument to HybridNew
    - method specific options:
        - You must include the option --LHCmode LHC-limits
        - Specify the number of toys with -T [number]
        - If you are asked for expected limits, specify the quantile with --expectedFromGrid=[quantile].
        - If the user asks for the expected limit but does not specify a quantile, assume it is 0.5.
        - If you are asked for observed limits, do not use the --expectedFromGrid={} option.
        - example for observed limits with 10 toys: method specific options will be `--LHCmode LHC-limits -T 10`
        - example for expected limits, 0.16 quantile, with 10 toys: method specific options will be `--LHCmode LHC-limits -T 10 --expectedFromGrid=0.16`
    - It is important to know that this calculates either the expected limit for a single quantile OR the observed limit.

# Typical CMS Combine workflow

In general, the workflow will be as follows:

1. Determine the appropriate command line options based on the task you were asked to perform. Refer to the above section "Building a command in CMS Combine". 
2. Run the command from step 1, which will produce a root file. A RunCommand tool is provided to run commands. You must use this tool to run ALL Combine commands.
3. Read the output from the root file.
4. If you have been asked to run over multiple mass points and/or quantiles, repeat steps 1, 2 and 3 for each combination of mass and quantile the user requested.
5. If you have run over many masses and/or quantiles, collect the limit results into a single json file.
6. Format the results. You should print a summary for the user. If requested, make results into a table or plot.