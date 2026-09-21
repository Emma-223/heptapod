from orchestral.tools import BaseTool
from orchestral.tools.base.field_utils import RuntimeField, StateField
from pathlib import Path
import subprocess
import json
import numpy as np
import math

from .combine_tools import _safe_path

class GetGridPointsTool(BaseTool):
    """
    Divides a range rMin to rMax into n_points evenly spaced points.
    Then divides those points up among HTCondor jobs with n_points_per_job in each job and saves the job splitting to a json file.

    Args:
    rMin: The minimum value of r
    rMax: the maximum value of r
    n_points: the total number of points to divide the range rMin - rMax into
    n_points_per_job: the number of points to run in each HTCondor job
    output_filename: the name of the json file where the job splitting data will be saved, e.g. "grid_points.json"

    Returns (JSON):
    {"status":"ok", "output_file":<name>}
    """

    # ========== Runtime Fields ==========
    rMin: float = RuntimeField(
        default = 0.0,
        description = "The minimum value of r"
    )
    rMax: float = RuntimeField(
        default = 20,
        description = "The maximum value of r"
    )
    n_points: int = RuntimeField(
        default = 50,
        description = "the total number of points to divide the range rMin - rMax into"
    )
    n_points_per_job: int = RuntimeField(
        default = 10,
        description = "the number of points to run in each HTCondor job"
    )
    output_filename: str = RuntimeField(
        default = "grid_points.json",
        description = "the name of the json file where the job splitting data will be saved, e.g. grid_points.json"
    )

    # ========== State Fields ==========
    base_directory: str = StateField(
        description="Working directory"
    )
    #===================================

    def _run(self) -> str:
        output_file = _safe_path(self.base_directory, self.output_filename)

        r_list = np.linspace(self.rMin,self.rMax,self.n_points,endpoint=True).tolist()
        n_jobs = math.ceil(self.n_points/self.n_points_per_job)
        rValuesPerJob = {}
        for i in range(n_jobs):
            rValuesPerJob[f"job_{i}"] = r_list[i*self.n_points_per_job:(i+1)*self.n_points_per_job]

        output_dict = {}
        output_dict["rMin"] = self.rMin
        output_dict["rMax"] = self.rMax
        output_dict["nPoints"] = self.n_points
        output_dict["nPointsPerJob"] = self.n_points_per_job
        output_dict["grid"] = rValuesPerJob

        with open(output_file, 'w') as f:
            json.dump(output_dict, f)

        return json.dumps({
            "status": "ok",
            "output_file": str(output_file)
        })

class WriteGridGenerationCondorFilesTool(BaseTool):
    """
    Writes the submit and executable files to run grid generation with CMS Combine as HTCondor jobs for a given mass hypothesis and quantile.

    Args:
    mass: The signal mass hypothesis to consider
    quantile: the quantile to consider. One of 0.025, 0.16, 0.5, 0.84, 0.975 or -1, where -1 is the observed limit.
    combine_command: The combine command output by WriteCombineCommand for this mass and quantile
    grid_points_file: The json file output by GetGridPoints for this mass and quantile, containing the list of r values to consider.
    output_directory: The output directory for the calculation, e.g. gridGen

    Returns (JSON):
    {"status": "ok", "submit_file": <name>, "executable_file": <name>}
    """

    # ========== Runtime Fields ==========
    mass: int = RuntimeField(
        description = "The signal mass hypothesis to consider"
    )
    quantile: float = RuntimeField(
        default = -1,
        description = "the quantile to consider. One of 0.025, 0.16, 0.5, 0.84, 0.975 or -1, where -1 is the observed limit."
    )
    combine_command: str = RuntimeField(
        description = "The combine command output by WriteCombineCommand for this mass and quantile"
    )
    grid_points_file: str = RuntimeField(
        description = "The json file output by GetGridPoints for this mass and quantile, containing the list of r values to consider."
    )
    output_directory: str = RuntimeField(
        default = "gridGen",
        description = "The output directory for the calculation, e.g. gridGen"
    )

    # =========== State Fields ===========
    datacards_by_mass: str = StateField(
        description="json file which can be loaded into a python dict with masses as keys and absolute paths to datacards as values"
    )
    base_directory: str = StateField(
        description="Working directory"
    )

    def _run(self) -> str:

        output_path_relative = self.output_directory + f"/{self.mass}/{self.quantile}".replace(".","p")
        output_path_full = _safe_path(self.base_directory, output_path_relative)

        if not output_path_full.exists():
            output_path_full.mkdir(parents=True, exist_ok=True)

        grid_file = _safe_path(self.base_directory, self.grid_points_file)
        if not grid_file.exists():
            return self.format_error(
                error="File not found",
                reason="The file containing the grid points does not exist",
                context=f"grid_points_file={self.grid_points_file}",
                suggestion="Check that the provided path is correct. Otherwise, run GetGridPoints to generate the file."
            )

        if not "HybridNew" in self.combine_command:
            return self.format_error(
                error="wrong combine method used",
                reason="Grid generation can only be done with the HybridNew method of Combine",
                suggestion="Rerun WriteCombineCommand with combine_method=HybridNew"
            )

        # Write condor.sh
        with open(grid_file,'r') as f:
            grid_points_data = json.load(f)

        expected_output_files = []
        executable_path = output_path_full / "condor.sh"
        with executable_path.open('w') as f:
            f.writelines([
                "#!/bin/sh \n",
                "ulimit -s unlimited \n",
                "set -e \n",
                f"if [ -f {str(output_path_full)}/higgsCombineTotalOutput_jobId$1.root ]; then",
                f"echo \"the output file {str(output_path_full)}/higgsCombineTotalOutput_jobId$1.root already exists, cancelling job\"",
                "exit 0"
            ])
            for job_id in grid_points_data["grid"].keys():
                rVals = grid_points_data["grid"][job_id]
                id_no = str(job_id).split("_")[-1]
                f.write(f"if [[ $1 -eq {id_no} ]]; then \n")
                f.write("rVals='" + " ".join(str(r) for r in rVals)+"' \n")
                f.write("fi \n\n")
                expected_output_files.append(f"higgsCombineTotalOutput_jobId{id_no}.root")

            f.write("for rval in $rVals; do\n")
            cmd = self.combine_command + " --singlePoint $rval -n .POINT.$rval \n"
            f.write(cmd)
            f.write("done\n\n")

            f.writelines([
                "hadd -fk207 higgsCombineTotalOutput_jobId$1.root higgsCombine.*POINT.*.root\n",
                "rm higgsCombine.*POINT.*root"
            ])

        # write condor.sub - only thing that changes is output file path and queue number
        submit_path = output_path_full / "condor.sub"

        text = Path("template_condor_sub.txt").read_text()
        nJobs = len(list(grid_points_data["grid"].keys()))
        submit_path.write_text(text.format(output_path=output_path_relative, nJobs = nJobs))

        # Write json with expected output
        json_path = output_path_full / "expected_output_files.json"
        with json_path.open("w") as f:
            json.dump({
                "file_list": expected_output_files
            },f)
        
        return json.dumps({
            "status":"ok",
            "submit_file":str(submit_path),
            "executable_file":str(executable_path)
        })

class CheckJobOutputTool(BaseTool):
    """
    Checks that the actual output of an HTCondor job submission matches the expected output determined in WriteGridGenerationCondorFiles.

    Args:
    mass: The signal mass hypothesis being considered
    quantile: "the quantile to consider. One of 0.025, 0.16, 0.5, 0.84, 0.975 or -1, where -1 is the observed limit."
    output_directory: the directory in which output is stored, e.g. gridGen or limits

    Returns (JSON):
    {"status": "ok", "all_files_exist": True}
    """

    # ========== Runtime Fields ==========
    mass: int = RuntimeField(
        description = "The signal mass hypothesis being considered"
    )
    quantile: float = RuntimeField(
        description = "the quantile to consider. One of 0.025, 0.16, 0.5, 0.84, 0.975 or -1, where -1 is the observed limit."
    )
    output_directory: str = RuntimeField(
        description = "the directory in which output is stored, e.g. gridGen or limits"
    )

    # ========== State Fields ==========
    base_directory: str = StateField(
        description = "working directory"
    )

    def _run(self) -> str:
        base_path = Path(self.base_directory + f"/{self.output_directory}/{self.mass}/{self.quantile}".replace(".","p"))
        file_to_read = base_path / "expected_output_files.json"
        if not file_to_read.exists():
            return self.format_error(
                error = "file not found",
                reason = "the file containing the list of expected output filenames does not exist",
                context=f"file path={file_to_read}",
                suggestion="check that the provided output directory is correct"
            )

        with file_to_read.open("r") as f:
            file_contents = json.load(f)

        file_list = file_contents["file_list"]

        missing_files = []
        for filename in file_list:
            path_to_check = base_path / filename
            if not path_to_check.exists():
                missing_files.append(str(path_to_check))

        if len(missing_files)>0:
            return self.format_error(
                error = "missing output files",
                reason = f"{len(missing_files)} files are missing from the output of the condor submission for mass {self.mass} GeV, quantile {self.quantile}",
                context = f"missing files={", ".join(missing_files)}",
                suggestion = f"Check that the provided output directory is correct. If the output directory is correct, the job most likely had a problem. Check the contents of the condor*.out and condor*.err files in the directory {base_path}"
            )

        return json.dumps(
            {"status": "ok",
             "all_files_exist": True}
        )