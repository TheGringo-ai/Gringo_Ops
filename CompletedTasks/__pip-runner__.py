import runpy
import sys

def run_my_module(module_name):
    try:
        runpy.run_module(module_name)
    except ImportError as e:
        print(f"Error importing module {module_name}: {e}")
    except Exception as e:
        print(f"An error occurred while running module {module_name}: {e}")

if __name__ == "__main__":
    module_name = "mymodule"
    run_my_module(module_name)