import os
import json
from datetime import datetime

class MemoryManager:
    def __init__(self, agent_name, memory_dir="FredFix/data/memory", shared=False):
        self.agent_name = "shared_memory" if shared else agent_name
        self.memory_dir = memory_dir
        self.memory_path = os.path.join(self.memory_dir, f"{self.agent_name}_memory.json")
        os.makedirs(self.memory_dir, exist_ok=True)
        self.memory_entries = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, "r") as f:
                return json.load(f)
        return []

    def _save_memory(self):
        with open(self.memory_path, "w") as f:
            json.dump(self.memory_entries, f, indent=2)

    def _get_current_session_id(self):
        return datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    def log_interaction(self, user_input, agent_response, tags=None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self._get_current_session_id(),
            "user_input": user_input,
            "agent_response": agent_response,
            "tags": tags or []
        }
        self.memory_entries.append(entry)
        self._save_memory()

    def get_recent(self, limit=5):
        return self.memory_entries[-limit:]

    def search(self, keyword):
        keyword = keyword.lower()
        return [
            e for e in self.memory_entries
            if keyword in e["user_input"].lower() or keyword in e["agent_response"].lower()
        ]

    def clear(self):
        self.memory_entries = []
        if os.path.exists(self.memory_path):
            os.remove(self.memory_path)

    def summarize_recent(self, limit=5):
        return "\n".join([
            f"{e['timestamp']} | {e['user_input']} → {e['agent_response']}"
            for e in self.get_recent(limit)
        ])

    def export(self, export_path):
        with open(export_path, "w") as f:
            json.dump(self.memory_entries, f, indent=2)

    def import_memory(self, import_path):
        if os.path.exists(import_path):
            with open(import_path, "r") as f:
                imported = json.load(f)
                self.memory_entries.extend(imported)
                self._save_memory()

    def get_by_tag(self, tag):
        return [e for e in self.memory_entries if tag in e["tags"]]

    def compact_summary(self, limit=10):
        return [
            {"q": e["user_input"], "a": e["agent_response"]}
            for e in self.get_recent(limit)
        ]

    def sync_to_cloud(self):
        pass  # TODO: Push memory_entries to Firebase