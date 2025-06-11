# File: exceptions.py

class ExternallyManagedEnvironment:
    def __init__(self, error):
        self.error = error

    @classmethod
    def from_config(cls, config_section):
        error = config_section.get("error_message")
        if error is None:
            raise MissingErrorKey("Error message key not found in config")
        return cls(error)

class ConfigurationFileCouldNotBeLoaded:
    def __init__(self, error):
        self.error = error

class MissingErrorKey(Exception):
    pass