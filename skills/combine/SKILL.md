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

The WriteCombineCommand tool takes 7 inputs: method, mass, seed, rMin, rMax, method specific options and user options.
You need to determine the correct inputs.
Details about each input are provided below:

Method: dictates which task Combine will run. For example, will it produce limits, or run a significance calculation, or do a likelihood scan? This can be one of:
    - AsymptoticLimits
    - HybridNew

Mass: the signal mass hypothesis for the physics process being studied. If you include this argument, Combine will put the mass in the name of the output root file. This is useful for keeping your files organized.

Seed: the seed Combine will use for randomization. Use -1 unless the user tells you to use a specific seed.

rMin: the minimum value of r

rMax: the maximum value of r

Method specific options: An option or combination of options specific to a given Combine method. Put these options into a single string to give to WriteCombineCommand.

User options: In some cases, the user may specify additional options they want you to use. Put these options into a single string to give to WriteCombineCommand. These are IN ADDITION TO the method specific options and DO NOT replace them.

Below are references for how to determine the combine_method and method_specific_options arguments.

## Asymptotic Limits

For instructions on determining the method-specific options for asymptotic limits, see **`references/asymptoticLimits.md`**

## Limits with toys

For instructions on running this interactively, see **`references/frequentistLimits.md`**.

Often, this calculation split up over many computing jobs. This is called "grid generation". For instructions on grid generation, see **`references/gridGeneration.md`**. Once the grid is generated, the output is extracted following **`references/extractingGridGenerationOutput.md`**. The final result is a set of root files which can be read with `ReadLimitOutput`.

# Running

For tasks you run interactively (i.e. NOT as HTCondor jobs), see **`references/runningInteractively.md`**.

# More Information

For more information about options that can be passed to Combine, see the Combine help menu in **`references/combine_help.txt`**.