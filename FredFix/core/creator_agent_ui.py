import streamlit as st
import os
import subprocess
from FredFix.core.CreatorAgent import CreatorAgent

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

tab1, tab2, tab3, tab4 = st.tabs(["🧠 Logic", "🛠️ Config", "📁 Files", "📜 History"])

with tab1:
    st.subheader("🔧 Generate a Python Module")

    with st.form("creator_agent_form"):
        prompt = st.text_area("Enter your prompt for module generation", height=200)
        filename = st.text_input("Filename to save (e.g. `new_module.py`)")
        submitted = st.form_submit_button("Generate & Save")

    if submitted and prompt and filename:
        agent = CreatorAgent()
        code = agent.create_module(prompt)
        path = agent.save_module(filename, code)

        st.success(f"✅ Module saved to: {path}")
        st.code(code, language="python")

        with open(log_path, "a") as log:
            log.write(f"{filename}: {prompt.strip()}\n")

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

with tab2:
    st.subheader("⚙️ Configuration")
    st.info("No configurable settings available yet.")

with tab3:
    st.subheader("📂 Browse Generated Modules")

    current_dir = os.path.dirname(__file__)
    files = [
        f for f in os.listdir(current_dir)
        if f.endswith(".py") and f != os.path.basename(__file__) and f != "CreatorAgent.py"
    ]

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
                result = subprocess.run(["python3", file_path], capture_output=True, text=True)
                st.text_area("🖥 Output", result.stdout or "No output.")
                with open(log_path, "a") as log:
                    log.write(f"Ran {selected_file} with output:\n{result.stdout}\n")
            except Exception as e:
                st.error(f"Execution failed: {e}")
                with open(log_path, "a") as log:
                    log.write(f"Error running {selected_file}: {e}\n")

with tab4:
    st.subheader("📜 History Log")
    if os.path.exists(log_path):
        with open(log_path, "r") as log:
            history = log.read()
        st.text_area("Log Contents", history, height=300)
    else:
        st.info("No history log found.")

tab5 = st.tabs(["📊 Analytics"])[0]
with tab5:
    st.subheader("📊 Generation Analytics (Mock)")
    st.write("Modules Generated:", len(os.listdir(current_dir)))
    st.line_chart([1, 3, 4, 7, 12])  # replace with real data later