# Task: Add more specific exception handling in the `build_wheel_legacy` function to catch specific exceptions like `subprocess.CalledProcessError` to provide more context in case of failures.
# Task: Use `os.path.join(tempd, filename)` instead of `os.path.join(tempd, names[0])` to create the wheel_path in the `get_legacy_build_wheel_path` function for better path concatenation.
# Task: Add more logging statements to provide detailed information about the build process for debugging purposes.
# Task: Consider using Python's `pathlib` module for handling file paths instead of `os.path`.