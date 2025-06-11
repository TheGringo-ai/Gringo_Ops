# __init__.py

# Importing submodules or specific attributes
from .module1 import classA, function_x
from .module2 import classB

# Initialize package-level data or configurations
DEFAULT_SETTING = "some_value"

# Define __all__ for controlled imports using *
__all__ = ["module1", "classA", "function_x"]

# Execute initialization code upon package import
import logging
logging.basicConfig(level=logging.INFO)