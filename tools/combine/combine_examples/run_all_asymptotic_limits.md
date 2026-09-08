---
description: Run the asymptotic limits for all masses in the leptoquark search analysis
---

The leptoquark search analysis considers mass hypotheses from 300 GeV to 2000 GeV in 100 GeV increments, so 300, 400, 500, etc. ending with 2000.
For each mass hypothesis, you should run Combine to produce the asymptotic limits. 
The results should be saved to a directory named AsymptoticLimits_300To2000.

Complete all steps through reading the results for one mass before you move on to the next mass.

You will need to add the following additional options to each Combine command: 

`--setParameters signalScaleParam=[scale_factor] --freezeParameters signalScaleParam`

The appropriate value of scale_factor for each mass is given in the table below. For example, a mass hypothesis of 500 GeV would need the options `--setParameters signalScaleParam=0.0018309999722987413 --freezeParameters signalScaleParam`

---
| 300 | 0.0013160000089555979 |
| 400 | 0.0015450000064447522 |
| 500 | 0.0018309999722987413 |
| 600 | 0.0026889999862760305 |
| 700 | 0.004176999907940626 |
| 800 | 0.007724999915808439 |
| 900 | 0.010815000161528587 |
| 1000 | 0.01750900037586689 |
| 1100 | 0.029868999496102333 |
| 1200 | 0.047835998237133026 |
| 1300 | 0.09109500050544739 |
| 1400 | 0.13824500143527985 |
| 1500 | 0.24536100029945374 | 
| 1600 | 0.4266360104084015 |
| 1700 | 0.6884769797325134 |
| 1800 | 1.2158199548721313 |
| 1900 | 2.153320074081421 |
| 2000 | 3.632812023162842 |
---

When you are done running over all masses, print a summary of the median (0.5 quantile) expected limit and the observed limit for each mass.