import subprocess
import os

def get_flake8_violations():
    """
    Runs flake8 on the entire project and returns a list of files with violations.
    """
    try:
        result = subprocess.run(
            [
                "flake8",
                ".",
                "--format=%(path)s",
                "--exit-zero", # Never exit with a non-zero code
            ],
            capture_output=True,
            text=True,
        )
        
        if result.stdout:
            # The output will be a list of file paths, one per line
            return list(set(result.stdout.strip().split('\n')))
        else:
            return []

    except FileNotFoundError:
        print("Error: flake8 is not installed or not in the system's PATH.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while running flake8: {e}")
        return []

if __name__ == "__main__":
    violations = get_flake8_violations()
    if violations:
        print("❌ Found flake8 violations in the following files:")
        for file in violations:
            print(f"  - {file}")
    else:
        print("✅ No flake8 violations found.")
