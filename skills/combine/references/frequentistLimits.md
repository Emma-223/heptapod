## Limits with toys

    - Set the method argument to HybridNew
    - method specific options:
        - You MUST include the option --LHCmode LHC-limits
        - Specify the number of toys with -T [number]
        - If you are asked for expected limits, specify the quantile with --expectedFromGrid=[quantile].
        - If the user asks for the expected limit but does not specify a quantile, assume it is 0.5.
        - If you are asked for observed limits, do not use the --expectedFromGrid={} option.
        - example for observed limits with 10 toys: method_specific_options = `--LHCmode LHC-limits -T 10`
        - example for expected limits, 0.16 quantile, with 10 toys: method_specific_options =  `--LHCmode LHC-limits -T 10 --expectedFromGrid=0.16`