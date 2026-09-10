# combine

A toolkit to automate the running of CMS Combine.

| Tool | What it does |
|---|---|
|`WriteCombineCommand`| Writes a CMS Combine command to be run. Handles modifying the command to run in a container if necessary.
|`RunCommand`| Runs a command made with WriteCombineCommand.
|`ReadLimitOutput`| Reads the expected and/or observed limits from a root file output by combine
|`CollectResults` | Collects results from multiple masses into a single json file
---

There is also a Combine SKILL.md file which defines some common terms, details the command line options for different methods, and outlines a typical Combine workflow.

Currently supported methods are `HybridNew` (simple models) and `AsymptoticLimits`.

## Configuration

The tools assume that you have your datacards in a json file with masses as the keys and absolute paths to datacards as the values. They also assume that you have exactly one datacard per mass.

The following two `tb config` commands are required:

`tb config set heptapod datacards_by_mass [path/to/file-with-datacard-paths.json]`

`tb config set heptapod base_directory [path/to/output] #the directory where output is to be stored`

If you are running Combine in a container, you will also need to set the path to the `.sif` file:

`tb config set heptapod combine_container [path/to/combine_container.sif]`

If `combine_container` is set, the tools will wrap the Combine command in an `apptainer exec` command which binds to `base_directory` and to the directory where the relevant datacard is stored.
If you are running in a `CMSSW` environment, you should not set `combine_container`. 

## Usage

Example of a short prompt to run the asymptotic limits for the datacard corresponding to a mass hypothesis of 500 GeV:

```
Run Combine to calculate the asymptotic limits for a mass hypothesis of 500 GeV.
```

The tools/skill also support the addition of extra options if you have something analysis-specific. Suppose you have a parameter specific to your analysis called `analysis_specific_parameter` that you want to set and freeze to 1.0:

```
Run Combine to calculate the asymptotic limits for a mass hypothesis of 500 GeV. Add the options --setParameters analysis_specific_parameter=1.0 --freezeParameters analysis_specific_parameter
```

For a longer calculation, such as looping over many masses to obtain limit as a function of mass, see the file in `combine_examples`