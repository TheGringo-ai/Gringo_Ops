import streamlit as st
import os
import subprocess
from FredFix.core.CreatorAgent import CreatorAgent
from FredFix.core.memory_manager import MemoryManager
from FredFix.core.config_loader import load_config
import json

st.set_page_config(page_title="CreatorAgent UI", layout="wide")

theme_choice = st.sidebar.selectbox("🎨 Theme", ["GringoOps", "Dark", "Light"])
logo_map = {
    "GringoOps": "https://raw.githubusercontent.com/TheGringo-ai/GringoOps/main/assets/logo.png",
    "Dark": "https://raw.githubusercontent.com/TheGringo-ai/GringoOps/main/assets/logo_dark.png",
    "Light": "https://raw.githubusercontent.com/TheGringo-ai/GringoOps/main/assets/logo_light.png",
}
logo_url = logo_map.get(theme_choice, logo_map["GringoOps"])
st.sidebar.image(logo_url, width=200)

st.sidebar.markdown("⬅️ [Back to Dashboard](gringoops_dashboard.py)")

os.makedirs("logs", exist_ok=True)
log_path = "logs/creator_agent_history.log"

config = load_config()
memory = MemoryManager()

# Add toggle controls for agents registered via config in sidebar
agents_config = config.get("agents", {})
agent_toggles = {}
for agent_name in agents_config.keys():
    agent_toggles[agent_name] = st.sidebar.checkbox(f"Enable {agent_name}", value=True)

enable_creator = agent_toggles.get("CreatorAgent", True)

st.title("🧠 CreatorAgent Interface")

current_dir = os.path.dirname(__file__)
files = [
    f for f in os.listdir(current_dir)
    if f.endswith(".py") and f != os.path.basename(__file__) and f != "CreatorAgent.py"
]

tabs = st.tabs([
    "📥 Prompt Builder",
    "⚙️ Config",
    "📁 Files",
    "📜 History",
    "📊 Analytics",
    "🧠 God Mode",
    "📎 File Analyzer"
])

with tabs[0]:  # 📥 Prompt Builder
    st.subheader("📥 Prompt Builder & Generator")

    with st.form("creator_agent_form"):
        prompt = st.text_area("Enter your prompt for module generation", height=200)
        filename = st.text_input("Filename to save (e.g. `new_module.py`)")
        submitted = st.form_submit_button("Generate & Save")

    if enable_creator and submitted and prompt and filename:
        agent = CreatorAgent()
        code = agent.create_module(prompt)
        path = agent.save_module(filename, code)

        st.success(f"✅ Module saved to: {path}")
        st.code(code, language="python")

        with open(log_path, "a") as log:
            log.write(f"{filename}: {prompt.strip()}\n")

        memory.append({
            "agent": "CreatorAgent",
            "action": "generate_module",
            "prompt": prompt,
            "filename": filename,
            "path": path
        })

        st.download_button("⬇️ Download Module", code, file_name=filename)

        if st.button("🧪 Generate Unit Test"):
            test_code = f'''
import unittest
from {filename.replace(".py", "")} import *

class TestGeneratedModule(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
'''
            st.download_button("⬇️ Download test_" + filename, test_code, file_name="test_" + filename)

with tabs[1]:  # ⚙️ Config
    st.subheader("⚙️ Configuration")
    st.info("No configurable settings available yet.")

with tabs[2]:  # 📁 Files
    st.subheader("📂 Browse Generated Modules")

    selected_file = st.selectbox("Choose a file to view/edit", options=files)

    if selected_file:
        file_path = os.path.join(current_dir, selected_file)

        with open(file_path, "r") as f:
            code = f.read()

        edited_code = st.text_area("✏️ Edit Code", value=code, height=300)

        if st.button("💾 Save Changes"):
            with open(file_path, "w") as f:
                f.write(edited_code)
            st.success("Changes saved.")
            memory.append({
                "agent": "CreatorAgent",
                "action": "edit_file",
                "filename": selected_file,
                "content": edited_code[:200]  # log only first 200 chars
            })

        if st.button("▶️ Run This Module"):
            try:
                result = subprocess.run(["python3", file_path], capture_output=True, text=True)
                st.text_area("🖥 Output", result.stdout or "No output.")
                with open(log_path, "a") as log:
                    log.write(f"Ran {selected_file} with output:\n{result.stdout}\n")
            except Exception as e:
                st.error(f"Execution failed: {e}")
                with open(log_path, "a") as log:
                    log.write(f"Error running {selected_file}: {e}\n")

with tabs[3]:  # 📜 History
    st.subheader("📜 History Log")
    if os.path.exists(log_path):
        with open(log_path, "r") as log:
            history = log.read()
        st.text_area("Log Contents", history, height=300)
    else:
        st.info("No history log found.")
with tabs[4]:  # 📊 Analytics
    st.subheader("📊 Generation Analytics (Mock)")

    # Calculate live counters from memory
    mem_data = memory.export()
    try:
        mem_json = json.loads(mem_data) if isinstance(mem_data, str) else json.loads(mem_data.decode())
    except Exception:
        mem_json = []

    prompt_generations = sum(1 for entry in mem_json if entry.get("action") == "generate_module")
    test_creations = sum(1 for entry in mem_json if entry.get("action") == "generate_test")
    file_edits = sum(1 for entry in mem_json if entry.get("action") == "edit_file")

    st.metric("Modules Generated", prompt_generations)
    st.metric("Unit Tests Created", test_creations)
    st.metric("Files Edited", file_edits)

    st.write("Modules Generated (file count):", len(files))
    st.line_chart([1, 3, 4, 7, 12])  # replace with real data later

# 🧠 God Mode (Developer/Commercial Panel)
with tabs[5]:  # 🧠 God Mode
    st.subheader("🧠 God Mode – Admin & Dev Tools")

    st.markdown("### 🔒 Licensing & Distribution")
    st.info("This version is Streamlit Cloud-friendly and ready for commercial packaging.")
    st.markdown("You may include licensing headers, author info, and bundle documentation.")

    st.markdown("### 📦 Export / Import Memory")
    if st.button("📤 Export Memory"):
        mem_export = memory.export()
        if isinstance(mem_export, (dict, list)):
            mem_export = json.dumps(mem_export)
        st.download_button("⬇️ Download memory.json", mem_export, file_name="memory.json")

    uploaded_file = st.file_uploader("📥 Import Memory JSON", type=["json"])
    if uploaded_file is not None:
        try:
            data = uploaded_file.read()
            if isinstance(data, bytes):
                data = data.decode()
            memory.load(data)
            st.success("Memory imported successfully.")
        except Exception as e:
            st.error(f"Failed to import memory: {e}")

    if st.button("🧹 Clear Memory"):
        memory.clear()
        st.success("Memory cleared.")

    st.markdown("### 📦 Export for Reuse")
    if st.button("📁 Bundle Project for Distribution"):
        try:
            os.system("zip -r GringoOps_Commercial_Package.zip . -x '*.venv*' '*.git*'")
            st.success("📦 Exported as GringoOps_Commercial_Package.zip")
            with open("GringoOps_Commercial_Package.zip", "rb") as f:
                st.download_button("⬇️ Download Bundle", f, file_name="GringoOps_Commercial_Package.zip")
        except Exception as e:
            st.error(f"❌ Failed to export: {e}")

    st.markdown("### 🛠 Dev Diagnostics")
    try:
        mem_usage = os.popen("ps -o rss= -p " + str(os.getpid())).read().strip()
        mem_mb = round(int(mem_usage)/1024, 2)
        st.metric(label="🔍 Current Memory Usage", value=f"{mem_mb} MB", delta=None)
    except:
        st.warning("Could not fetch memory usage stats.")

    st.markdown("### 🧠 Memory Tools")
    # Memory export and clear handled above

with tabs[6]:  # 📎 File Analyzer
    st.subheader("📎 File Analyzer")

    selected_file = st.selectbox("Choose a file to analyze", options=files, key="analyzer_file_select")

    if selected_file:
        file_path = os.path.join(current_dir, selected_file)

        with open(file_path, "r") as f:
            code = f.read()

        st.text_area("📄 File Contents", code, height=300)

        if st.button("🔍 Analyze File"):
            try:
                from FredFix.core.AnalyzerAgent import AnalyzerAgent
                analyzer = AnalyzerAgent()
                analysis_result = analyzer.analyze_file(file_path)
                st.text_area("📝 Analysis Result", analysis_result, height=300)
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# 🧠 Unified Memory Sync - new section below God Mode tab
with st.expander("🧠 Unified Memory Sync"):
    auto_load = st.checkbox("🔄 Auto-load last session", value=False)
    if auto_load:
        try:
            last_mem = memory.export()
            if last_mem:
                memory.load(last_mem)
                st.success("Last session loaded from memory.")
        except Exception as e:
            st.error(f"Failed to auto-load last session: {e}")

    # Editable context summary linked to memory key "summary"
    summary = memory.get("summary", "")
    new_summary = st.text_area("📝 Context Summary", value=summary, height=150)
    if new_summary != summary:
        memory.set("summary", new_summary)

    # Optional Firebase sync placeholder
    if st.button("📡 Sync to Firebase"):
        st.info("Firebase sync not implemented yet.")