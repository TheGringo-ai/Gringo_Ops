import subprocess
import json


def repair_all_code():
    """
    Runs pylint on the entire project and returns the results as a JSON string.
    """
    try:
        # Run pylint, capturing the output as JSON
        result = subprocess.run(
            [
                "pylint",
                "--recursive=y",
                ".",
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
            return {"status": "No issues found."}

    except FileNotFoundError:
        return {"error": "pylint is not installed or not in the system's PATH."}
    except json.JSONDecodeError:
        return {"error": "Failed to parse pylint output.", "raw_output": result.stdout}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
