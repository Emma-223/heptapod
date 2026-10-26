For short tasks, such as calculating asymptotic limits, we can run Combine interactively.
In general, the workflow will be as follows:

1. Determine the appropriate command line options based on the task you were asked to perform. 
2. Run the command from step 1, which will produce a root file. You MUST use the provided `RunCombineCommand` tool to run commands interactively.
3. Read the output from the root file using `ReadLimitOutput`.
4. If you have been asked to run over multiple mass points and/or quantiles, repeat steps 1, 2 and 3 for each combination of mass and quantile the user requested.
5. If you have run over many masses and/or quantiles, collect the limit results into a single json file.