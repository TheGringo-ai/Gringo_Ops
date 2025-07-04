import difflib
import shutil
import os
from pathlib import Path

class PatchWriter:
    """
    Applies generated code patches to files, with safety features like
    snapshotting, validation, and rollback.
    """
    def __init__(self, fixes, memory=None):
        """Initializes the PatchWriter with a dictionary of fixes and an optional memory object."""
        self.fixes = fixes
        self.memory = memory

    def apply_patches(self, dry_run=True, interactive=False):
        """
        Applies the patches to the files.

        Args:
            dry_run (bool): If True, prints the changes without writing to disk.
            interactive (bool): If True, asks for user confirmation before applying each patch.
        
        Returns:
            tuple: A tuple containing two dictionaries: successful_patches and failed_patches.
        """
        successful_patches = {}
        failed_patches = {}

        for file_path, file_fixes in self.fixes.items():
            if not file_fixes:
                continue

            print(f"--- Patching file: {file_path} ---")
            
            # Filter out patches that have previously failed
            if self.memory:
                original_fix_count = len(file_fixes)
                file_fixes = [fix for fix in file_fixes if self.memory.was_patch_successful(file_path, fix['original_issue'])]
                if len(file_fixes) < original_fix_count:
                    print(f"[Memory] Skipped {original_fix_count - len(file_fixes)} previously failed patches.")

            if not file_fixes:
                continue

            if dry_run:
                self._apply_dry_run(file_path, file_fixes)
                successful_patches[file_path] = file_fixes
            else:
                was_applied = self._apply_for_real(file_path, file_fixes, interactive)
                if was_applied:
                    successful_patches[file_path] = file_fixes
                else:
                    failed_patches[file_path] = [fix['original_issue'] for fix in file_fixes]

            print("-------------------------------------")
        
        return successful_patches, failed_patches

    def _apply_dry_run(self, file_path, file_fixes):
        """
        Prints the intended changes for a single file as a diff.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            
            modified_lines = self._generate_modified_lines(original_lines, file_fixes)

            diff = difflib.unified_diff(original_lines, modified_lines, fromfile=f'{file_path} (original)', tofile=f'{file_path} (patched)')
            for line in diff:
                print(line, end='')

        except Exception as e:
            print(f"[PatchWriter] Error generating diff for {file_path}: {e}")

    def _apply_for_real(self, file_path, file_fixes, interactive):
        """
        Applies the changes to a single file with snapshot and rollback.
        """
        backup_path = Path(f"{file_path}.bak")
        try:
            shutil.copyfile(file_path, backup_path)

            if interactive:
                self._apply_dry_run(file_path, file_fixes)
                response = input(f"Apply this patch to {file_path}? [y/N] ")
                if response.lower() != 'y':
                    print("Skipping patch.")
                    backup_path.unlink()
                    return False

            with open(file_path, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()

            modified_lines = self._generate_modified_lines(original_lines, file_fixes)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(modified_lines)
            
            print(f"Successfully patched {len(file_fixes)} issues in {file_path}")
            backup_path.unlink() # Clean up backup file on success
            return True

        except Exception as e:
            print(f"[PatchWriter] Error applying patch to {file_path}: {e}")
            if backup_path.exists():
                print(f"[PatchWriter] Rolling back changes from {backup_path}")
                shutil.move(str(backup_path), file_path)
            return False

    def _generate_modified_lines(self, original_lines, file_fixes):
        """
        Generates the modified file content based on the fixes.
        """
        modified_lines = original_lines[:]
        # Sort fixes by line number in reverse to handle insertions correctly without shifting indices.
        sorted_fixes = sorted(file_fixes, key=lambda x: x['line_number'], reverse=True)

        for fix in sorted_fixes:
            line_num = fix['line_number']
            # Adjust for 0-based indexing
            line_idx = line_num - 1

            if fix['type'] == 'INSERT_BEFORE':
                modified_lines.insert(line_idx, fix['new_code'])
            elif fix['type'] == 'INSERT_AFTER':
                modified_lines.insert(line_idx + 1, fix['new_code'])
            # Add other fix types here if needed, e.g., 'REPLACE'

        return modified_lines
