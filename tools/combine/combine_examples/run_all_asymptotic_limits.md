---
description: Run the asymptotic limits for all masses in the leptoquark search analysis
---

# General information and overview of the task

The leptoquark search analysis considers mass hypotheses from 300 GeV to 1000 GeV in 100 GeV increments, so 300, 400, 500, etc. ending with 1000. The user wants you to calculate the asymptotic limits for each mass hypothesis by following the steps detailed below, then show them a summary of the results. This is a complex, multi-step task which you should run autonomously with @general. Remember that if a tool is available, you should always use the tool.

# Steps

For each mass hypothesis:

1. Write a Combine command to run the asymptotic limits for this mass. You will need to include the additional options detailed below in the section "Required additional options to Combine commands".
2. Run the command from step 1, saving the results to a directory named AsymptoticLimits_300To1000_test4.
3. Read the output for this mass (in other words, read the root file produced in step 2).
4. When you have finished steps 1, 2 and 3, proceed to the next mass.

When you are done running over all masses, collect the limit results into a single json file. Then print a summary table of the observed and median expected limits for each mass.

# Required additional options to Combine commands

When you write the Combine command, you will need to add the following additional options: 

`--setParameters signalScaleParam=[scale_factor] --freezeParameters signalScaleParam`

The appropriate value of scale_factor for each mass is given in the table below. For example, a mass hypothesis of 500 GeV would need the options `--setParameters signalScaleParam=0.0018309999722987413 --freezeParameters signalScaleParam`

| mass | scale_factor |
| --- | --- |
| 300 | 0.0013160000089555979 |
| 400 | 0.0015450000064447522 |
| 500 | 0.0018309999722987413 |
| 600 | 0.0026889999862760305 |
| 700 | 0.004176999907940626 |
| 800 | 0.007724999915808439 |
| 900 | 0.010815000161528587 |
| 1000 | 0.01750900037586689 |
---