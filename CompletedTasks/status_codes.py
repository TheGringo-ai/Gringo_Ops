from enum import Enum

class StatusCode(Enum):
    """Status codes for the application."""

    SUCCESS = 0
    """Operation completed successfully."""

    ERROR = 1
    """An unspecified error occurred."""

    UNKNOWN_ERROR = 2
    """An unknown error occurred."""

    VIRTUAL_ENVIRONMENT_NOT_FOUND = 3
    """The required virtual environment was not found."""

    PREVIOUS_BUILD_DIRECTORY_EXISTS = 4
    """A previous build directory already exists."""

    NO_MATCHES_FOUND = 23
    """No matching items were found during the search."""
    # Add more status codes as needed