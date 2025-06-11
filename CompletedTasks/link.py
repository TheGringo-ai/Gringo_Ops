The code provided is well structured and documented. Here are some suggestions and improvements that can be applied:

1. **Type Annotations**: The type annotations are well-defined and clear. However, it is recommended to provide more specific types where possible. For example, in functions like `supported_hashes`, you could specify the exact types of the dictionary keys and values.

2. **Consistency in Comments**: In the `_CleanResult` class, the comment explaining the purpose of the class is quite detailed. It would be good to maintain this level of detail in other comments throughout the code.

3. **Constants**: The `_SUPPORTED_HASHES` list is being used in multiple places. It might be a good idea to define this as a constant at the beginning of the file to make it more visible and easier to update if needed.

4. **Error Handling**: In the `find_hash_url_fragment` method of the `LinkHash` class, it might be beneficial to log a warning or error message if an invalid hash name is encountered.

5. **Code Optimization**: The `_clean_url_path` function can be optimized for readability by using list comprehension instead of the `for` loop to clean the parts.

6. **Consistency in Property Naming**: The property names like `hash` and `hash_name` in the `Link` class can be made consistent with other property names by adding the `property` decorator.

7. **Use of `pathlib`**: Instead of using `posixpath` or `os.path` for path manipulation, you could consider using `pathlib` which provides a more object-oriented approach to working with paths.

8. **Error Handling**: In the `clean_func` selection within the `_clean_url_path` function, it would be good to include error handling in case the `is_local_path` parameter is neither `True` nor `False`.

These are general suggestions to further enhance the code. Make sure to test the code after applying the changes.