# File: misc.py

import os
import shutil
from typing import List

def create_directory(path: str) -> None:
    """
    Create a directory at the specified path.
    
    Args:
        path (str): The path of the directory to be created.
    """
    os.makedirs(path, exist_ok=True)

def delete_directory(path: str) -> None:
    """
    Delete a directory at the specified path.
    
    Args:
        path (str): The path of the directory to be deleted.
    """
    shutil.rmtree(path, onerror=handle_remove_readonly)

def handle_remove_readonly(func, path, exc_info):
    """
    Error handling function for shutil.rmtree to handle read-only files.
    
    Args:
        func: The function causing the error.
        path (str): The path of the file causing the error.
        exc_info: Exception information.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def generate_random_string(length: int) -> str:
    """
    Generate a random string of the specified length.
    
    Args:
        length (int): The length of the random string to generate.
        
    Returns:
        str: The randomly generated string.
    """
    # Implementation of the random string generation function

# Other utility functions...

# Remaining code in misc.py