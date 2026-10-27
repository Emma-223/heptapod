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

    Do NOT run the output of WriteCombineCommand in a terminal. Instead, pass the combine_command output of WriteCombineCommand to the combine_command argument of RunCommand.

    Args:
        combine_method: The method of Combine to run. One of AsymptoticLimits, HybridNew, or MultiDimFit.
        mass: The signal mass hypothesis to use.
        seed: The seed to use for randomization. Use -1 unless the user requests a specific seed.
        method_specific_options: specific options for the chosen method.
        user_options: extra options provided by the user. Do not put anything in this argument unless the user gives you the specific option(s) to add.
        is_condor_job: Will the output of this tool be passed to WriteGridGenerationCondorFiles and run as an HTCondor job?
        rMin: The minimum value of r. Defaults to 0.
        rMax: The maximum value of r. Defaults to 20.

    Returns (JSON):
        {status: "ok", "combine_command": "<str>", combine_method: "<str>", mass: "<GeV>"}

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
    user_options: str = RuntimeField(
        default="",
        description="extra options provided by the user. Do not put anything in this argument unless the user gives you the specific option(s) to add."
    )
    is_condor_job: bool = RuntimeField(
        default = False,
        description = "Will the output of this tool be passed to WriteGridGenerationCondorFiles and run as an HTCondor job?"
    )
    rMin: float = RuntimeField(
        default=0.0,
        description="The minimum value of r. Defaults to 0."
    )
    rMax: float = RuntimeField(
        default = 20.0,
        description="The maximum value of r. Defaults to 20."
    )

    # ========== State fields ==========
    datacards_by_mass: str = StateField(
        description="json file which can be loaded into a python dict with masses as keys and absolute paths to datacards as values"
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
            
        with open(self.datacards_by_mass, 'r') as f:
            datacards_dict = json.load(f)
        datacard_file = datacards_dict[str(self.mass)]
        
        if not Path(datacard_file).exists():
            return self.format_error(
                error="File not found",
                reason="The datacard file does not exist. The provided path was likely incorrect.",
                context=f"datacard_file={datacard_file}",
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

        # combine -M [method] [datacard] [options]
        combine_command = f"combine -M {self.combine_method} {datacard_file} -m {self.mass} --seed {self.seed} --rMin {self.rMin} --rMax {self.rMax} "

        combine_command += " " + self.method_specific_options
        combine_command += " " + self.user_options

        # run in a container if one was provided, otherwise don't
        datacard_directory = Path(datacard_file).parent
        if (self.combine_container != "") and not self.is_condor_job:
            cmd_to_run = "apptainer exec --no-home -B " + self.base_directory + " -B " + str(datacard_directory) + " " + self.combine_container + " " + combine_command
        else:
            cmd_to_run = combine_command
                
        return json.dumps(
            {"status": "ok",
             "combine_command": cmd_to_run,
             "mass": self.mass,
             "combine_method": self.combine_method}
        )
        

class RunCombineCommandTool(BaseTool):
    """
    Runs a combine command in a terminal and records the name of the output file. 
    You create the command by calling WriteCombineCommand. 
    You MUST run ALL combine commands using this tool.
    If combine_method is HybridNew, the command may take 5 to 10 minutes to run.
    If the user requests that you save the results to a specific directory, use that as the root_file_directory option. Do not make the directory yourself, because the tool will do it for you.

    Args:
        combine_command: the command to run, output by WriteCombineCommand
        mass: the signal mass hypothesis

    Returns (JSON):
        {"status": "ok", "combine_command": "<str>", "output_root_file_name": "<name>", "output_root_file_directory": "<name>", "mass": "<GeV>", "combine_method": "<str>"}
    """

    #========== Runtime Fields ==========
    combine_command: str = RuntimeField(
        description = "the command to run, output by WriteCombineCommand"
    )
    mass: int = RuntimeField(
        description = "the signal mass hypothesis"
    )
    combine_method: str = RuntimeField(
        description = "the combine method being run"
    )

    #========== State Fields ==========
    base_directory: str = StateField(
        description="Working directory"
    )
    
    def _run(self) -> str:
        #Name the directory after the method used, store results in a sub-directory named for the mass
        output_dir = _safe_path(self.base_directory, f"{self.combine_method}/{self.mass}")
        if not Path(output_dir).is_dir():
            Path(output_dir).mkdir(parents=True)

        # save exact command that was run for later reference
        cmd_file = output_dir / "command_{}_{}.txt".format(self.combine_method,self.mass)
        cmd_file.write_text(self.combine_command)

        # run command in output_dir so the root file ends up there
        process = subprocess.run(self.combine_command.split(),capture_output=True,text=True,cwd=output_dir)

        # save stderr and stdout for later reference
        output_lines = process.stdout.split("\n")
        std_out_file = output_dir / "std_out_{}_{}.txt".format(self.combine_method,self.mass)
        std_err_file = output_dir / "std_err_{}_{}.txt".format(self.combine_method,self.mass)
        std_out_file.write_text(process.stdout)
        std_err_file.write_text(process.stderr)
        
        # the random seed is useful in making sure we get the right file
        seed = ""
        for line in output_lines:
            if "seed" in line:
                seed = line.split()[-1]

        # How the output file should look. We should find exactly one file that matches this pattern.
        output_pattern = "higgsCombine*"+self.combine_method+"*"+str(self.mass)+"*"+seed+"*"+".root"

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
            
        output_name = output_file[0].name

        return json.dumps(
            {
                "status": "ok",
                "combine_command": self.combine_command,
                "output_root_file_name": str(output_name),
                "output_directory": str(output_dir),
                "mass": self.mass,
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
        root_file_name: The name of root file produced by RunCommand when the Combine method is AsymptoticLimits or HybridNew. This file should already exist when you call this tool.
        root_file_directory: The directory in which root_file is stored, relative to the working directory.
        output_limits_file: File name to write the limit results to, relative to the working directory. This should be a json file. It is just a filename, not a path.
        combine_method: The combine method used to create root_file
        mass: The signal mass hypothesis that produced these limits.

    Returns (JSON):
        {"status": "ok", "output_file": "<name>"}

    """
    # ========== Runtime Fields ==========
    root_file_name: str = RuntimeField(
        description = "The name of root file produced by RunCommand when the Combine method is AsymptoticLimits or HybridNew. This file should already exist when you call this tool."
    )
    root_file_directory: str = RuntimeField(
        description = "The directory in which root_file_name is stored, relative to the working directory."
    )
    output_limit_file: str = RuntimeField(
        default = "limits.json",
        description = "File name to write the limit results to. This should be a json file. It is just a filename, not a path."
    )
    combine_method: str = RuntimeField(
        description = "The combine method used to create root_file_name"
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
        out_path = _safe_path(self.base_directory, Path(self.root_file_directory) / self.output_limit_file)
        root_file_with_dir = Path(self.root_file_directory) / self.root_file_name
        root_file_full = _safe_path(self.base_directory, root_file_with_dir)
        
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
            ) # agent kept wanting to make directories for this file to live in. We want to force it to live in the same directory as the other outputs

        # standard ROOT way of getting info from a tree. Makes a dict with quantiles as the keys and limits as the values. 
        limit_file = TFile.Open(str(root_file_full))
        limit_tree = limit_file.Get("limit")

        limit_dict = {}

        for quantile in limit_tree:
            quantStr = str(round(quantile.quantileExpected,3))
            limit_dict[quantStr] = quantile.limit

        # put the mass in too
        limit_dict["mass"] = self.mass

        out_path.write_text(json.dumps(limit_dict))

        return json.dumps({"status": "ok", "output_file_name": str(out_path.name), "output_directory": self.root_file_directory})

class CollectResultsTool(BaseTool):
    """
    Collects limit results from many json files and consolidates them into a single json file.

    If you have previously calculated limits for many masses and quantiles and the user is asking for a summary table or plot, this will be the first step.

    Args:
        individual_filenames: A comma separated list of the names of the json files containing results of individual limit calculations.
        root_file_directory: The directory where the output of the limit calculation is stored.
        all_limits_file: The name of the json file where you will write all of the limits, for example, limits_all.json.
        combine_method: The combine_method used to produce these limits.

    Returns (JSON):
        {"status": "ok", "output_file": "<name>", "limits_by_mass_and_quantile": "<dict>"}
    """

    # ========== Runtime Fields ==========
    individual_filenames: str = RuntimeField(
        description="A comma separated list of the names of the json files containing results of individual limit calculations."
    )
    root_file_directory: str = RuntimeField(
        description="The directory where the output of the limit calculation is stored"
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
        out_path = _safe_path(self.base_directory, self.root_file_directory+"/"+self.all_limits_file)
        file_list = self.individual_filenames.split(",")

        # check that files exist, replace names with full paths
        missing_files = []
        for i,f in enumerate(file_list):
            this_file_full = _safe_path(self.base_directory, self.root_file_directory+"/"+f.strip())
            if not Path(this_file_full).exists():
                missing_files.append(this_file_full)
            file_list[i] = this_file_full
                
        if len(missing_files) > 0:    
            return self.format_error(
                error="Files do not exist",
                reason="At least one of the input json files does not exist",
                context="missing_files= " + ", ".join(missing_files),
                suggestion="Check that the correct file names were used."
            )

        limit_dict = {}

        # HybridNew will have one file per mass per quantile. AsymptoticLimits will have all quantiles in one file per mass.
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
            {"status": "ok", "output_file": str(out_path), "limits_by_mass_and_quantile": limit_dict}
        )

class PlotTestStatsFromRootFileTool(BaseTool):
    """
    Reads a test_stat_distributions.root file and saves the plot of each test statistic distribution in the file as a png and/or pdf file. Returns the path to the directory containing the plot files. Returns a formatted error if test_stat_distributions.root does not exist at the provided path.

    Args:
    file_type: Type of image file for plots. 'png' for .png files, 'pdf' for .pdf files, or 'both' to produce one png and one pdf of each plot.
    path_to_root_file: The directory containing test_stat_distributions.root, relative to the working directory.
    plot_dir: Directory in which to save the plots, relative to the working directory.

    Returns (JSON):
    {"status": "ok", "plots_dir": <path>}
    """

    # ========== Runtime Fields ==========
    file_type: str = RuntimeField(
        default = "pdf",
        description = "Type of image file for plots. 'png' for .png files, 'pdf' for .pdf files, or 'both' to produce one png and one pdf of each plot."
    )
    path_to_root_file: str = RuntimeField(
        description = "The directory containing test_stat_distributions.root, relative to the working directory."
    )
    plot_dir: str = RuntimeField(
        default = "test_stat_plots",
        description = "Directory in which to save the plots, relative to the working directory."
    )

    # ========== State Fields ==========
    base_directory: str = StateField(
        description = "working directory"
    )

    def _run(self)-> str:
        root_file = _safe_path(self.base_directory, self.path_to_root_file +"/test_stat_distributions.root")
        if not root_file.exists:
            raise self.format_error(
                error="file does not exist",
                reason=f"no file test_stat_distributions.root found in {self.path_to_root_file}",
                suggestion="check that the provided path is correct and relative to the working directory"
            )
            
        tfile = TFile.Open(str(root_file))
        canvas_names = tfile.GetListOfKeys()
        
        plot_dir_path_relative = self.path_to_root_file +"/"+ self.plot_dir
        output_dir = _safe_path(self.base_directory, plot_dir_path_relative)
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
            
        for cname in canvas_names:
            print(cname.GetName())
            c = tfile.Get(cname.GetName())
            
            save_name = cname.GetName().replace("qmu","testStatPlot")
            save_path = str(output_dir / save_name)
            if "png" in self.file_type.lower():
                c.Print(save_path+".png")
            elif "pdf" in self.file_type.lower():
                c.Print(save_path+".pdf")
            elif "both" in self.file_type.lower():
                c.Print(save_path+".png")
                c.Print(save_path+".pdf")
            else:
                return self.format_error(
                    error="wrong file type specified",
                    reason="the file_type argument can be 'pdf', 'png', or 'both'.",
                    context=f"file_type={self.file_type}",
                    suggestion="use 'pdf' or 'png' in the file_type argument, or 'both' to make one of each."
                )

        return json.dumps({"status":"ok", "plots_dir": str(output_dir)})