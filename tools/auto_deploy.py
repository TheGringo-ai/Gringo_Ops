import subprocess
import sys
from pathlib import Path

# Add project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from tools.gringo_checkpoint import log

def run_gated_deploy():
    """
    Runs the test suite and, if it passes, deploys to Firebase.
    """
    log("🚀 Starting gated deployment process...")
    
    # 1. Run tests
    print("--- 🧪 Running Tests ---")
    try:
        test_result = subprocess.run(["pytest"], capture_output=True, text=True, check=True)
        log("✅ All tests passed. Proceeding to deployment.")
        print(test_result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        log(f"❌ Tests failed. Deployment aborted. Reason: {e}")
        print("--- ❌ Tests FAILED ---")
        if hasattr(e, 'stdout'):
            print(e.stdout)
        if hasattr(e, 'stderr'):
            print(e.stderr)
        sys.exit(1) # Exit with a non-zero code to fail the CI job

    # 2. Deploy to Firebase
    print("\n--- 🚀 Deploying to Firebase Hosting ---")
    try:
        deploy_result = subprocess.run(
            ["firebase", "deploy", "--only", "hosting", "--project", "chatterfix-ui"],
            capture_output=True,
            text=True,
            check=True
        )
        log("✅ Deployment to Firebase Hosting successful.")
        print(deploy_result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        log(f"❌ Firebase deployment FAILED. Reason: {e}")
        print("--- ❌ Firebase Deployment FAILED ---")
        if hasattr(e, 'stdout'):
            print(e.stdout)
        if hasattr(e, 'stderr'):
            print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_gated_deploy()
