"""
Configuration file for pytest.

This file is automatically discovered by pytest and is used to define fixtures
and perform setup for the entire test suite.
"""
import sys
import os
from unittest.mock import MagicMock

# 1. Mock the Streamlit library
# This must be done BEFORE any of the application's frontend modules are imported.
# We create a fake 'streamlit' module and add it to sys.modules.
class MockStreamlit:
    def __init__(self):
    
        """Placeholder docstring for __init__."""        self.session_state = {}
        self.stop = MagicMock(side_effect=SystemExit) # Make stop raise an exception
        self.rerun = MagicMock()
        self.switch_page = MagicMock()
        self.warning = MagicMock()
        self.error = MagicMock()
        self.success = MagicMock()

sys.modules['streamlit'] = MockStreamlit()

# 2. Add the project's root directory to the Python path
# This allows pytest to find and import modules from the `backend` and `frontend`
# directories using standard import statements (e.g., `from frontend.auth_utils ...`).
chatterfix_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, chatterfix_root)

# 3. Firebase Emulator Fixtures
import pytest
from google.cloud import firestore
from google.auth.credentials import AnonymousCredentials
import grpc
import time
import subprocess

@pytest.fixture(scope="session")
def firestore_emulator():
    """
    Fixture to start and stop the Firebase Firestore emulator for the test session.
    Checks if the emulator is already running before starting.
    """
    host = "localhost:8686"
    os.environ["FIRESTORE_EMULATOR_HOST"] = host
    
    # Check if emulator is already running
    try:
        # Use a simple gRPC health check or a dummy request
        channel = grpc.insecure_channel(host)
        # This is a low-level way to check. A dummy read is more reliable.
        credentials = AnonymousCredentials()
        db = firestore.Client(project="chatterfix-test", credentials=credentials)
        db.collection("emulator-health-check").document("ping").get(timeout=1)
        print("Firestore emulator already running.")
        yield
        return
    except Exception:
        print("Emulator not found, starting a new one...")

    emulator_command = "firebase emulators:start --only firestore"
    
    try:
        subprocess.run(["java", "-version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.fail("Java is not installed or not in PATH. The Firestore emulator requires Java.")

    emulator_process = subprocess.Popen(emulator_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the emulator to be ready
    time.sleep(10) 
    
    yield
    
    print("Stopping Firestore emulator...")
    emulator_process.terminate()
    emulator_process.wait()

@pytest.fixture(scope="function")
def firestore_client(firestore_emulator):
    """
    Fixture to provide a Firestore client connected to the emulator.
    """
    host = os.environ.get("FIRESTORE_EMULATOR_HOST", "localhost:8686")
    credentials = AnonymousCredentials()
    
    max_retries = 5
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            db = firestore.Client(project="chatterfix-test", credentials=credentials)
            # Test connection
            db.collection("test-connection").document("test").set({"status": "ok"})
            print("Firestore client connected to emulator.")
            return db
        except Exception as e:
            print(f"Connection attempt {attempt + 1} to emulator failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                pytest.fail("Could not connect to Firestore emulator after multiple retries.")
    
    pytest.fail("Failed to initialize Firestore client.")
