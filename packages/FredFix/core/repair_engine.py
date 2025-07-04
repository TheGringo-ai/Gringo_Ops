import subprocess
import json


def repair_file(file_path):
    """
    Runs pylint on a single file and returns the results as a JSON string.
    """
    try:
        # Run pylint on the specified file
        result = subprocess.run(
            [
                "pylint",
                file_path,
                "-f",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        # Pylint exits with a non-zero status code for even minor issues,
        # so we check the output directly.
        if result.stdout:
            return json.loads(result.stdout)
        else:
            return {"status": f"No issues found in {file_path}."}

    except FileNotFoundError:
        return {"error": "pylint is not installed or not in the system's PATH."}
    except json.JSONDecodeError:
        return {"error": f"Failed to parse pylint output for {file_path}.", "raw_output": result.stdout}
    except Exception as e:
        return {"error": f"An unexpected error occurred while processing {file_path}: {e}"}
