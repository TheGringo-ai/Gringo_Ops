from typing import Optional, Tuple

def prepare_metadata_for_build_editable(metadata_directory: str) -> Optional[Tuple[str, str, str]]:
    """Prepares metadata for editable builds.

    Args:
        metadata_directory: The directory containing the metadata.

    Returns:
        A tuple containing (dist-info directory, egg-info directory, record file path)
        or None if an error occurs.
    """
    try:
        distinfo_dir = "some_distinfo_dir"  # Replace with actual logic
        joined_path = os.path.join(metadata_directory, distinfo_dir)

        # Further processing of joined_path (e.g., checking for files)

        record_file = "some_record_file"  # Replace with actual logic
        egg_info_dir = "some_egg_info_dir"  # Replace with actual logic
        return joined_path, egg_info_dir, record_file

    except FileNotFoundError:
        print(f"Error: Directory not found: {metadata_directory} or {distinfo_dir}")
        return None
    except PermissionError:
        print(f"Error: Permission denied accessing: {joined_path}")
        return None
    except OSError as e:
        print(f"An unexpected OS error occurred: {e}")
        return None