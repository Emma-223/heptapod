from orchestral.tools import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField
from pathlib import Path
import subprocess
import json
from ROOT import TFile, TTree

def _safe_path(base_directory: str, filename: str) -> Path:
    """Resolve a file name inside base_directory, and refuse to escape it."""
    root = Path(base_directory).resolve()
    full = (root / filename).resolve()
    if root not in full.parents and full != root:
        raise ValueError(f"path escapes the working directory: {filename}")
    return full

class WriteCombineCommandTool(BaseTool):
    """
    Writes a command for CMS Combine given a signal mass hypothesis.

    Do NOT run the output of WriteCombineCommand in a terminal. Instead, call RunCommand with the output of WriteCombineCommand.

    Args:
        combine_method: The method of Combine to run. One of AsymptoticLimits, HybridNew, or MultiDimFit.
        mass: The signal mass hypothesis to use.
        seed: The seed to use for randomization. Use -1 unless the user requests a specific seed.
        method_specific_options: specific options for the chosen method.
        other_options: extra options provided by the user. Do not put anything in this argument unless the user gives you the specific option(s) to add.

    Returns (JSON):
        {status: "ok", random_seed: "<int>", combine_method: "<str>", mass: "<GeV>", "quantile": "<str>"}

    Errors:
        Returns a formatted error if the datacard is missing
    """
    
    # =========== Runtime fields ==========
    combine_method: str = RuntimeField(
        description="The method of Combine to run. One of AsymptoticLimits, HybridNew, or MultiDimFit."
    )
    mass: int = RuntimeField(
        description="The signal mass hypothesis to use"
    )
    seed: int = RuntimeField(
        deafult=-1,
        description="The seed to use for randomization. Use -1 unless the user requests a specific seed."
    )
    method_specific_options: str = RuntimeField(
        default="",
        description="specific options for the chosen method."
    )
    other_options: str = RuntimeField(
        default="",
        description="extra options provided by the user. Do not put anything in this argument unless the user gives you the specific option(s) to add."
    )
    #limit_style: str = RuntimeField(
    #    default = "",
    #    description="Which test statistic to use in the HybridNew method. Can be one of LEP, TEV or LHC."
    #)
    #quantile_expected: str = RuntimeField(
    #    default = "NA",
    #    description = "Which quantile to run when calculating expected limits in the HybridNew method. Can be one of 0.025, 0.016, 0.5, 0.84, 0.975 or -1 if combine_method is HybridNew. Must be 'all' if combine_method is AsymptoticLimits. Otherwise, it is 'NA' (short for 'not applicable')."
    #)

    # ========== State fields ==========
    datacard_directory: str = StateField(
        description="directory where datacards are stored"
    )
    base_directory: str = StateField(
        description="Working directory"
    )
    combine_container: str = StateField(
        default = "",
        description = "The singularity container to run in, if using"
    )
    #===================================

    def _run(self) -> str:
            
        #datacard_file = self.datacard_filename_template.format(self.mass)
        #print("using datacard:",datacard_file)
        datacard_file = list(Path(self.datacard_directory).glob("*M{}.txt".format(self.mass)))[0]
        #print(datacard_file)
        if not datacard_file.exists():
            return self.format_error(
                error="File not found",
                reason="The datacard file does not exist. The provided path was likely incorrect",
                suggestion="Check that the path to the datacards is correct and is an absolute path"
            )
        if self.combine_container != "":
            if not Path(self.combine_container).exists():
                return self.format_error(
                    error="Container does not exist",
                    reason="A path to a container was provided, but the file does not exist",
                    context=f"combine_container={self.combine_container}",
                    suggestion="Check combine_container when constructing the tool"
                )
        combine_command = "combine " + "-M " + self.combine_method+ " "+ str(datacard_file) + " -m " + str(self.mass) + " --seed " + str(self.seed)

        #if self.combine_method == "HybridNew":
        #    combine_command += " --LHCmode LHC-limits "

        #if self.combine_method == "HybridNew" and self.quantile_expected != "-1":
        #    combine_command += " --expectedFromGrid={} ".format(self.quantile_expected)
        print(self.method_specific_options)
        combine_command += " " + self.method_specific_options
        combine_command += " " + self.other_options
        #print("the combine command will be:", " ".join(combine_command))

        if self.combine_container != "":
            cmd_to_run = "apptainer exec --no-home -B " + self.base_directory + " -B " + self.datacard_directory + " " + self.combine_container + " " + combine_command
        else:
            cmd_to_run = combine_command

        #print("The command that will run is:", " ".join(cmd_to_run))
        #if self.combine_method == "AsymptoticLimits":
        #    quantile = "all"
        #elif self.combine_method == "HybridNew":
        #    if self.quantile_expected == "-1":
        #        quantile = "observed"
        #    else:
        #        quantile = self.quantile_expected
        #else:
        #    quantile = "Not applicable"
                
        return json.dumps(
            {"status": "ok",
             "combine_command": cmd_to_run,
             "mass": self.mass,
             "combine_method": self.combine_method}
             #"quantile": self.quantile_expected}
        )
        

class RunCommandTool(BaseTool):
    """
    Runs a combine command in a terminal and records the name of the output file. 
    You create the command by calling WriteCombineCommand. 
    You MUST run ALL combine commands using this tool.
    If combine_method is HybridNew, the command may take 5 to 10 minutes to run.
    If the user requests that you save the results to a specific directory, use that as the root_file_directory option.

    Args:
        combine_command: the command to run, output by WriteCombineCommand
        mass: the signal mass hypothesis
        root_file_directory: the name of the directory for storing output root files"

    Returns (JSON):
        {"status": "ok", "output_root_file": "<name>", "mass": "<GeV>", "quantile": "<str>"}
    """

    #========== Runtime Fields ==========
    combine_command: str = RuntimeField(
        description = "the command to run, output by WriteCombineCommand"
    )
    mass: int = RuntimeField(
        description = "the signal mass hypothesis"
    )
    #quantile: str = RuntimeField(
    #    description = "the quantile being considered"
    #)
    combine_method: str = RuntimeField(
        description = "the combine method being run"
    )
    root_file_directory: str = RuntimeField(
        description = "the name of the directory for storing output root files"
    )

    #========== State Fields ==========
    base_directory: str = StateField(
        description="Working directory"
    )
    #root_file_directory: str = StateField(
    #    description="The directory for output root files"
    #)
    
    def _run(self) -> str:
        #output_dir = self.base_directory + "/" + self.root_file_directory
        output_dir = _safe_path(self.base_directory, self.root_file_directory)
        if not Path(output_dir).is_dir():
            Path(output_dir).mkdir(parents=True)
            
        process = subprocess.run(self.combine_command.split(),capture_output=True,text=True,cwd=output_dir)
        output_lines = process.stdout.split("\n")
        #print(process.stdout)
        #print(process.stderr)
        std_out_file = output_dir / "std_out_{}_{}.txt".format(self.combine_method,self.mass)
        std_err_file = output_dir / "std_err_{}_{}.txt".format(self.combine_method,self.mass)
        std_out_file.write_text(process.stdout)
        std_err_file.write_text(process.stderr)
        
        seed = ""
        for line in output_lines:
            if "seed" in line:
                seed = line.split()[-1]

        output_pattern = "higgsCombine*"+self.combine_method+"*"+str(self.mass)+"*"+seed+"*"+".root"
        #print(output_pattern)
        output_file = list(Path(output_dir).glob(output_pattern))
        if len(output_file) == 0:
            return self.format_error(
                error="No output file produced",
                reason="The command did not produce a root file following the expected pattern: "+output_pattern,
                suggestion="Check the contents of: "+str(std_err_file)
            )
        if len(output_file) > 1:
            return self.format_error(
                error="Found too many files",
                reason="Found more than one root file matching the expected pattern: "+output_pattern,
                suggestion="Check that the output of each command is being saved to a separate directory"
            )
            
        output_name = output_file[0]#.resolve()#.name

        return json.dumps(
            {
                "status": "ok",
                "combine_command": self.combine_command,
                "output_root_file": str(output_name),
                "mass": self.mass,
                #"quantile": self.quantile,
                "combine_method": self.combine_method
            }
        )


class ReadLimitOutputTool(BaseTool):
    """
    Reads from a root file to get the output of a limit calculation performed with combine. 

    Use this when you have a file of the type "higgsCombine.[method].*.root", 
    where "method" is one of AsymptoticLimits or HybridNew, 
    and you want the limits on the signal strength r.

    Args: 
        root_file: The root file produced by RunCommand when the Combine method is AsymptoticLimits or HybridNew. This file should already exist when you call this tool.
        output_limits_file: File name to write the limit results to, relative to the working directory. This should be a json file. It is just a filename, not a path.
        combine_method: The combine method used to create root_file
        mass: The signal mass hypothesis that produced these limits.

    Returns (JSON):
        {"status": "ok", "output_file": "<name>"}

    """
    # ========== Runtime Fields ==========
    root_file: str = RuntimeField(
        description = "A root file output by combine with the method AsymptoticLimits or HybridNew."
    )
    output_limit_file: str = RuntimeField(
        default = "limits.json",
        description = "File name to write the limit results to, relative to the working directory. This should be a json file. It is just a filename, not a path."
    )
    combine_method: str = RuntimeField(
        description = "The combine method used to create root_file"
    )
    mass: int = RuntimeField(
        description = "The signal mass hypothesis that produced these limits"
    )
    
    # ========== State Fields ==========
    base_directory: str = StateField(
        description = "working directory for file output"
    )
    
    # ========== run ==========
        
    def _run(self) -> str:
        out_path = _safe_path(self.base_directory, Path(self.root_file).parent / self.output_limit_file)
        root_file_full = Path(self.base_directory) / self.root_file
        print(self.root_file)
        print(root_file_full)
        if not root_file_full.exists():
            return self.format_error(
                error="File not found",
                reason="the root file containing the limits does not exist",
                suggestion="Run WriteCombineCommand and RunCommand to run Combine and create the root file"
            )
        if "/" in self.output_limit_file:
            return self.format_error(
                error="Invalid filename",
                reason="The name provided for the output limit json file is a path, not a plan filename.",
                suggestion="Use a plain filename such as 'limits_[mass].json"
            )
        limit_file = TFile.Open(str(root_file_full))
        limit_tree = limit_file.Get("limit")

        limit_dict = {}

        for quantile in limit_tree:
            quantStr = str(round(quantile.quantileExpected,3))
            limit_dict[quantStr] = quantile.limit
            #print(limit_dict)
        limit_dict["mass"] = self.mass
        print(limit_dict)
        out_path.write_text(json.dumps(limit_dict))
        limit_dict["status"] = "ok"
        limit_dict["output_file"] = str(out_path)

        return json.dumps(limit_dict)

class CollectResultsTool(BaseTool):
    """
    Collects limit results from many json files and consolidates them into a single json file.

    If you have previously calculated limits for many masses and quantiles and the user is asking for a summary table or plot, this will be the first step.

    Args:
        individual_filenames: A comma separated list of the json file names containing results of individual limit calculations. These can be found in the output of the calls to ReadLimitOutput. 
        all_limits_file: The name of the json file where you will write all of the limits, for example, limits_all.json.
        combine_method: The combine_method used to produce these limits.

    Returns (JSON):
        {"status": "ok", "output_file": "<name>"}
    """

    # ========== Runtime Fields ==========
    individual_filenames: str = RuntimeField(
        description="A comma separated list of the json file names containing results of individual limit calculations. These can be found in the output of the calls to ReadLimitOutput."
    )
    all_limits_file: str = RuntimeField(
        default="limits_all.json",
        description="The name of the json file where you will write all of the limits, for example, limits_all.json."
    )
    combine_method: str = RuntimeField(
        description="The combine_method used to produce these limits."
    )

    # ========== State Fields ==========
    base_directory: str = StateField(
        description = "working directory for file output"
    )

    # ========== run ==========
        
    def _run(self) -> str:
        print(self.base_directory)
        out_path = _safe_path(self.base_directory, self.all_limits_file)
        file_list = self.individual_filenames.split(",")
        missing_files = []
        for i,f in enumerate(file_list):
            file_list[i] = self.base_directory+"/"+ f.strip()
            if not Path(self.base_directory+"/"+f.strip()).exists():
                missing_files.append(f.strip())
                
        if len(missing_files) > 0:    
            return self.format_error(
                error="Files do not exist",
                reason="At least one of the input json files does not exist",
                context="missing_files= " + ", ".join(missing_files),
                suggestion="Check that the correct file names were used."
            )

        limit_dict = {}

        #HybridNew will have one file per mass per quantile. AsymptoticLimits will have all quantiles in one file per mass.
        for filename in file_list:
            with open(filename,'r') as this_file:
                dict_this_file = json.load(this_file)

            mass = dict_this_file["mass"]
            if not mass in limit_dict.keys():
                limit_dict[mass] = {}
                
            quantiles = dict_this_file.keys()
            for q in quantiles:
                if q=="mass":
                    continue
                limit_dict[mass][q] = dict_this_file[q]

        out_path.write_text(json.dumps(limit_dict))

        return json.dumps(
            {"status": "ok", "output_file": str(out_path)}
        )