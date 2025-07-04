import json
from pathlib import Path
import logging
from abc import ABC, abstractmethod
import os

# Try to import firestore, but don't fail if it's not installed
try:
    from google.cloud import firestore
    from google.oauth2 import service_account
except ImportError:
    firestore = None
    service_account = None

logger = logging.getLogger(__name__)

class MemoryBackend(ABC):
    """Abstract base class for different memory storage backends."""

    @abstractmethod
    def get_error_files(self) -> list:
        """Gets a list of files that have previously caused errors."""
        pass

    @abstractmethod
    def add_error_file(self, file_path: str):
        """Adds a file to the list of error-prone files."""
        pass

    @abstractmethod
    def record_failed_patch(self, file_path: str, issue_description: str):
        """Records a patch that failed validation."""
        pass

    @abstractmethod
    def was_patch_successful(self, file_path: str, issue_description: str) -> bool:
        """Checks if a patch for a given issue has previously failed."""
        pass

    @abstractmethod
    def clear(self):
        """Clears the entire memory for the current scope."""
        pass

class JsonMemoryBackend(MemoryBackend):
    """Handles the agent's memory, persisting it to a local JSON file."""
    def __init__(self, project_root: Path):
        """Placeholder docstring for __init__."""        """Placeholder docstring for __init__."""        """Placeholder docstring for __init__."""        self.memory_path = project_root / ".agent_memory.json"
        self.memory = self._load()

    def _load(self) -> dict:
        """Placeholder docstring for _load."""        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    logger.info(f"[JsonMemory] Loading memory from {self.memory_path}")
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"[JsonMemory] Could not load memory file: {e}")
                return self._get_default_memory()
        return self._get_default_memory()

    def _save(self):
        """Placeholder docstring for _save."""        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=4)
                logger.info(f"[JsonMemory] Saved memory to {self.memory_path}")
        except IOError as e:
            logger.error(f"[JsonMemory] Could not save memory file: {e}")

    def _get_default_memory(self) -> dict:
        """Placeholder docstring for _get_default_memory."""        return {"version": "1.0", "error_files": [], "failed_patches": {}}

    def get_error_files(self) -> list:
        """Placeholder docstring for get_error_files."""        """Placeholder docstring for get_error_files."""        """Placeholder docstring for get_error_files."""        return self.memory.get("error_files", [])

    def add_error_file(self, file_path: str):
        """Placeholder docstring for add_error_file."""        """Placeholder docstring for add_error_file."""        """Placeholder docstring for add_error_file."""        if file_path not in self.memory["error_files"]:
            self.memory["error_files"].append(file_path)
            self._save()
            logger.warning(f"[JsonMemory] Added {file_path} to error files.")

    def record_failed_patch(self, file_path: str, issue_description: str):
        """Placeholder docstring for record_failed_patch."""        """Placeholder docstring for record_failed_patch."""        """Placeholder docstring for record_failed_patch."""        if file_path not in self.memory["failed_patches"]:
            self.memory["failed_patches"][file_path] = []
        if issue_description not in self.memory["failed_patches"][file_path]:
            self.memory["failed_patches"][file_path].append(issue_description)
            self._save()
            logger.warning(f"[JsonMemory] Recorded failed patch for '{issue_description}' in {file_path}.")

    def was_patch_successful(self, file_path: str, issue_description: str) -> bool:
        """Placeholder docstring for was_patch_successful."""        """Placeholder docstring for was_patch_successful."""        """Placeholder docstring for was_patch_successful."""        failed_for_file = self.memory["failed_patches"].get(file_path, [])
        return issue_description not in failed_for_file
    
    def clear(self):
        """Placeholder docstring for clear."""        """Placeholder docstring for clear."""        """Placeholder docstring for clear."""        self.memory = self._get_default_memory()
        self._save()
        logger.info("[JsonMemory] Cleared local memory file.")


class FirestoreMemoryBackend(MemoryBackend):
    """
    Handles the agent's memory, persisting it to Google Firestore.
    This enables a global, shared memory across different agents and projects.
    """
    def __init__(self, project_id: str, collection_name: str = "gringoops_agent_memory"):
        if firestore is None:
            raise ImportError("google-cloud-firestore is not installed.")

        credentials = None
        gcp_key_json = os.environ.get('GCP_SERVICE_ACCOUNT_KEY')

        if gcp_key_json:
            if service_account is None:
                raise ImportError("google-auth library is not installed, which is required for service account authentication.")
            try:
                credentials_info = json.loads(gcp_key_json)
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                logger.info("[FirestoreMemory] Authenticating using GCP_SERVICE_ACCOUNT_KEY environment variable.")
            except json.JSONDecodeError:
                logger.error("[FirestoreMemory] Failed to parse GCP_SERVICE_ACCOUNT_KEY. Is it a valid JSON? Falling back to default credentials.")
        
        if credentials:
            self.db = firestore.Client(project=project_id, credentials=credentials)
        else:
            logger.info("[FirestoreMemory] Authenticating using Application Default Credentials.")
            self.db = firestore.Client(project=project_id)

        self.collection = self.db.collection(collection_name)
        self.project_doc_ref = self.collection.document(project_id) # One document per project
        logger.info(f"[FirestoreMemory] Initialized for project '{project_id}'.")

    def _get_memory_doc(self):
        """Placeholder docstring for _get_memory_doc."""        doc = self.project_doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {"error_files": [], "failed_patches": {}}

    def get_error_files(self) -> list:
        return self._get_memory_doc().get("error_files", [])

    def add_error_file(self, file_path: str):
        self.project_doc_ref.update({"error_files": firestore.ArrayUnion([file_path])})
        logger.warning(f"[FirestoreMemory] Added {file_path} to error files.")

    def record_failed_patch(self, file_path: str, issue_description: str):
        # Firestore cannot have '.' in field names, so we replace it.
        safe_file_path = file_path.replace('.', '_')
        patch_key = f"failed_patches.{safe_file_path}"
        self.project_doc_ref.update({patch_key: firestore.ArrayUnion([issue_description])})
        logger.warning(f"[FirestoreMemory] Recorded failed patch for '{issue_description}' in {file_path}.")

    def was_patch_successful(self, file_path: str, issue_description: str) -> bool:
        memory = self._get_memory_doc()
        safe_file_path = file_path.replace('.', '_')
        failed_for_file = memory.get("failed_patches", {}).get(safe_file_path, [])
        return issue_description not in failed_for_file

    def clear(self):
        self.project_doc_ref.set({"error_files": [], "failed_patches": {}})
        logger.info("[FirestoreMemory] Cleared Firestore memory for this project.")


class AgentMemory:
    """
    A factory and facade for the agent's memory.
    It can be configured to use different backends like local JSON or Firestore.
    """
    def __init__(self, project_root: Path, backend: str = 'json', gcp_project_id: str = None):
        backend_env = os.environ.get('AGENT_MEMORY_BACKEND', backend)
        
        if backend_env == 'firestore':
            project_id = gcp_project_id or os.environ.get('GCP_PROJECT_ID')
            if not project_id:
                raise ValueError("GCP_PROJECT_ID must be set via env var or passed to use the firestore backend.")
            self.backend = FirestoreMemoryBackend(project_id)
        elif backend_env == 'json':
            self.backend = JsonMemoryBackend(project_root)
        else:
            raise ValueError(f"Unknown memory backend: {backend_env}")

    def get_error_files(self) -> list:
        return self.backend.get_error_files()

    def add_error_file(self, file_path: str):
        self.backend.add_error_file(file_path)

    def record_failed_patch(self, file_path: str, issue_description: str):
        self.backend.record_failed_patch(file_path, issue_description)

    def was_patch_successful(self, file_path: str, issue_description: str) -> bool:
        return self.backend.was_patch_successful(file_path, issue_description)

    def clear(self):
        self.backend.clear()
