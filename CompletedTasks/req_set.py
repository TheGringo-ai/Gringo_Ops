1. The import statement `from pip._internal.req.req_install import InstallRequirement` is not part of the standard library and could cause problems when running the code in different environments. Consider replacing it with a more generic library or moving the import to the place where it is used.

2. Add appropriate type hints for the attributes and functions in the class `RequirementSet` to enhance readability and maintainability.

3. The use of `assert` statements in the methods `add_unnamed_requirement` and `add_named_requirement` could lead to unexpected behavior. It's recommended to use proper exception handling mechanisms instead.

4. The `check_supported_wheels` parameter in the `RequirementSet` constructor is not used in the class. Consider removing it if it's not needed.

5. The `warn_legacy_versions_and_specifiers` method could be improved by providing more context in the deprecation messages.

6. Add docstrings to explain the purpose and usage of each method in the `RequirementSet` class for better documentation.