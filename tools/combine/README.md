# combine

A toolkit to automate the running of CMS Combine.

| Tool | What it does |
|---|---|
|`WriteCombineCommand`| Writes a command to be run
|`RunCommand`| Runs a command made with WriteCombineCommand
|`ReadLimitOutput`| Reads the expected and/or observed limits from a root file output by combine
|---|---|

There is also a Combine SKILL.md file which defines some common terms, details the command line options for different methods, and outlines a typical Combine workflow.

Supported methods are `HybridNew` (simple models) and `AsymptoticLimits`.

## Configuration

The tools assume that you have your datacards named as a function of mass hypothesis and that every datacard for your analysis is stored in the same directory.

The following two `tb config` commands are required:

`tb config set heptapod datacard_directory [path/to/datacards] #the directory where you store datacards`

`tb config set heptapod base_directory [path/to/output] #the directory where output is to be stored`

If you are running Combine in a container (i.e. outside of `CMSSW`), you will also need to set the path to the `.sif` file:

`tb config set heptapod combine_container [path/to/combine_container.sif]`

## Usage

Example of a short prompt to run the asymptotic limits for the datacard corresponding to a mass hypothesis of 500 GeV:

```
Run Combine to calculate the asymptotic limits for a mass hypothesis of 500 GeV. Show me the results as a table of the limit for each quantile.
```

The tools/skill also support the addition of extra options if you have something analysis-specific. Suppose you have a parameter specific to your analysis called `analysis_specific_parameter` that you want to set and freeze to 1.0:

```
Run Combine to calculate the asymptotic limits for a mass hypothesis of 500 GeV. Show me the results as a table of the limit for each quantile. Add the options --setParameters analysis_specific_parameter=1.0 --freezeParameters analysis_specific_parameter
```

For a longer calculation, such as looping over many masses to obtain limit as a function of mass, see the file in `combine_examples`