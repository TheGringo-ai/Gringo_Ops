import streamlit as st
import os
import subprocess
from FredFix.core.CreatorAgent import CreatorAgent
from Agent.memory import save_memory

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

    if submitted and prompt and filename:
        agent = CreatorAgent()
        with st.spinner("🧠 Generating code..."):
            code = agent.create_module(prompt)
            path = agent.save_module(filename, code)

        save_memory("CreatorAgent", prompt, code, {"filename": filename})

        st.success(f"✅ Module saved to: {path}")
        st.code(code, language="python")

        with open(log_path, "a") as log:
            log.write(f"{filename}: {prompt.strip()}\n")

        st.download_button("⬇️ Download Module", code, file_name=filename)

        if st.checkbox("🧪 Auto-generate unit test"):
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

        if st.button("▶️ Run This Module"):
            try:
                with st.spinner("▶️ Running module..."):
                    result = subprocess.run(["python3", file_path], capture_output=True, text=True)
                    st.text_area("🖥 Output", result.stdout or "No output.")
                with open(log_path, "a") as log:
                    log.write(f"Ran {selected_file} with output:\n{result.stdout}\n")
            except Exception as e:
                st.error(f"Execution failed: {e}")
                with open(log_path, "a") as log:
                    log.write(f"Error running {selected_file}: {str(e)[:500]}\n")

with tabs[3]:  # 📜 History
    st.subheader("📜 History Log")
    if os.path.exists(log_path):
        with open(log_path, "r") as log:
            history = log.read()
        st.text_area("Log Contents", history, height=300)
        st.download_button("⬇️ Download Full Log", history, file_name="creator_agent_history.log")
    else:
        st.info("No history log found.")
with tabs[4]:  # 📊 Analytics
    st.subheader("📊 Generation Analytics (Mock)")
    st.write("Modules Generated:", len(files))
    st.line_chart([1, 3, 4, 7, 12])  # replace with real data later

# 🧠 God Mode (Developer/Commercial Panel)
with tabs[5]:  # 🧠 God Mode
    st.subheader("🧠 God Mode – Admin & Dev Tools")

    st.markdown("### 🔒 Licensing & Distribution")
    st.info("This version is Streamlit Cloud-friendly and ready for commercial packaging.")
    st.markdown("You may include licensing headers, author info, and bundle documentation.")

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
                save_memory("AnalyzerAgent", selected_file, analysis_result, {"source": "File Analyzer"})
            except Exception as e:
                st.error(f"Analysis failed: {e}")