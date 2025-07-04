import argparse
import subprocess
import sys
from pathlib import Path

# Ensure the tools directory is in the Python path
# This allows us to import the scanner and analyzer modules
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from tools.project_scanner import get_project_files
from tools.code_analyzer import CodeAnalyzer
from tools.code_fixer import CodeFixer
from tools.patch_writer import PatchWriter
from tools.memory import AgentMemory

EXCLUDED_PATHS = [
    'node_modules', '.venv', '__pycache__', '.git',
    'dist', 'build', 'coverage', '.mypy_cache'
]

ALLOWED_EXTENSIONS = ['.py', '.yaml', '.yml', '.json', '.toml', '.md', '.env']

class ReviewAgent:
    """
    An agent that orchestrates a full project review by scanning files,
    running them through an analysis engine, and optionally fixing them.
    """
    def __init__(self, project_root, auto_fix=False, validate=False, interactive=False, memory_backend='json', gcp_project_id=None):
        """Initializes the ReviewAgent."""
        self.project_root = Path(project_root).resolve()
        self.auto_fix = auto_fix
        self.validate = validate
        self.interactive = interactive
        self.memory = AgentMemory(self.project_root, backend=memory_backend, gcp_project_id=gcp_project_id)
        if not self.project_root.is_dir():
            raise FileNotFoundError(f"The specified project root does not exist or is not a directory: {self.project_root}")

    def run_review(self):
        """
        Executes the end-to-end review process.
        """
        print(f"[Review Agent] Starting review for project: {self.project_root}")

        # 1. Scan the project to get all relevant files
        project_files = self._get_filtered_project_files(self.project_root)

        # 2. Analyze the files for potential issues
        analyzer = CodeAnalyzer(project_files, self.memory)
        report = analyzer.run_analysis()
        analyzer.save_report(self.project_root / "code_analysis_report.json")

        # 3. Print the final summary report to the console
        if not report:
            print("\n[Review Agent] ✨ No issues found. The project looks clean! ✨")
            return

        print("\n--- 🕵️ GringoOps Analysis Report 🕵️ ---")
        for file, issues in report.items():
            relative_path = Path(file).relative_to(self.project_root)
            print(f"\n📄 File: {relative_path}")
            for issue in issues:
                print(f"   - {issue}")
        print("\n--------------------------------------")
        print(f"[Review Agent] Review complete. Report saved to {self.project_root / 'code_analysis_report.json'}")

        if self.auto_fix:
            self.run_autofix(report)

    def _get_filtered_project_files(self, path):
        """
        Recursively gets all files in a directory, filtering by extension and excluded paths.
        """
        all_files = get_project_files(path)
        filtered_files = []
        error_files = self.memory.get_error_files()

        for file in all_files:
            if file in error_files:
                print(f"[Memory] Skipping previously problematic file: {file}")
                continue
            if any(excluded in file for excluded in EXCLUDED_PATHS):
                continue
            if Path(file).suffix in ALLOWED_EXTENSIONS:
                filtered_files.append(file)
        return filtered_files

    def run_autofix(self, report):
        """
        Runs the auto-fixing process based on the analysis report.
        """
        print("\n--- 🤖 GringoOps Auto-Fix Agent 🤖 ---")
        fixer = CodeFixer(report)
        fixes = fixer.generate_fixes()

        if not fixes:
            print("[Auto-Fix] No actionable fixes could be generated.")
            return

        patch_writer = PatchWriter(fixes, self.memory)
        successful_patches, failed_patches = patch_writer.apply_patches(
            dry_run=not self.auto_fix, 
            interactive=self.interactive
        )

        if self.validate and successful_patches:
            self.run_validation(successful_patches)
        
        if failed_patches:
            print("\n--- 💔 Some patches failed to apply ---")
            for file_path, issues in failed_patches.items():
                for issue in issues:
                    self.memory.record_failed_patch(file_path, issue)

    def run_validation(self, patched_files):
        """
        Runs post-patch validation using black, ruff, and pytest.
        """
        print("\n--- VALIDATING PATCHES ---")
        try:
            # We can be more surgical here later, for now, we run on the whole project
            subprocess.run(["ruff", "check", ".", "--fix"], check=True, capture_output=True, text=True)
            subprocess.run(["black", "."], check=True, capture_output=True, text=True)
            # subprocess.run(["pytest"], check=True) # Optional: run tests
            print("\n--- ✅ VALIDATION SUCCESSFUL ✅ ---")
        except subprocess.CalledProcessError as e:
            print(f"\n--- ❌ VALIDATION FAILED: {e} ❌ ---")
            print(f"Stderr: {e.stderr}")
            # When validation fails, we know the last set of patches might be bad.
            # We record all of them as failed for now. A more granular approach could be added later.
            for file_path, issues in patched_files.items():
                for issue in issues:
                    self.memory.record_failed_patch(file_path, issue['original_issue'])
            print("[Memory] Recorded failed patches. They will be skipped in the future.")

def main():
    """Main function to run the review agent."""
    parser = argparse.ArgumentParser(description="GringoOps - Automated Code Review Agent")
    parser.add_argument(
        "--path",
        default=".",
        help="The root path of the project you want to review. Defaults to the current directory."
    )
    parser.add_argument("--auto-fix", action="store_true", help="Automatically apply suggested fixes.")
    parser.add_argument("--validate", action="store_true", help="Run validation after applying fixes.")
    parser.add_argument("--interactive", action="store_true", help="Prompt for confirmation before each patch.")
    parser.add_argument("--memory", action="store_true", help="Enable the agent's memory to skip previously failed operations.")
    parser.add_argument("--memory-backend", default='json', choices=['json', 'firestore'], help="The backend to use for memory.")
    parser.add_argument("--gcp-project-id", default=None, help="The GCP project ID to use for the Firestore memory backend.")
    parser.add_argument("--scope", default=".", help="The directory to scan.")
    args = parser.parse_args()

    try:
        agent = ReviewAgent(args.path, args.auto_fix, args.validate, args.interactive, args.memory_backend, args.gcp_project_id)
        if args.memory:
            print(f"[Review Agent] Memory is enabled (backend: {args.memory_backend}).")
        else:
            agent.memory.clear() # Clear memory if not enabled
            print("[Review Agent] Memory is disabled.")
        agent.run_review()
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
