import streamlit as st
from pathlib import Path
from FredFix.tools.apply_patch import lint_file, lint_folder
from FredFix.tools.summarize_script import summarize_code
from FredFix.tools.refactor_script import refactor_with_llm
from FredFix.tools.generate_unittests import generate_unittests
from FredFix.tools.generate_readme import generate_readme
from FredFix.core.memory import MemoryManager
memory = MemoryManager(shared=True)

def render_dev_tools_ui():
    memory.log_event("Dev Tools UI loaded")
    st.markdown("### 🛠️ Developer Tools")
    selected_tool = st.selectbox("Choose a tool", ["lint", "lint_folder", "summarize", "refactor", "generate_unittests", "generate_readme"])
    selected_file = st.text_input("Target file or folder")
    model_override = st.text_input("Model override (optional)", "")

    if st.button("Run Dev Tool"):
        try:
            model = model_override.strip() or "mistral"
            memory.log_event("Dev tool run", {
                "tool": selected_tool,
                "target": selected_file,
                "model": model
            })
            result = ""

            if selected_tool == "lint":
                result = lint_file(selected_file)
            elif selected_tool == "lint_folder":
                result = lint_folder(selected_file)
            elif selected_tool == "summarize":
                code = Path(selected_file).read_text()
                result = summarize_code(code, model)
            elif selected_tool == "refactor":
                code = Path(selected_file).read_text()
                result = refactor_with_llm(code, model)
            elif selected_tool == "generate_unittests":
                code = Path(selected_file).read_text()
                result = generate_unittests(code, model)
            elif selected_tool == "generate_readme":
                code = Path(selected_file).read_text()
                result = generate_readme(code, model)

            st.code(result)
        except Exception as e:
            st.error(f"❌ Tool execution failed: {e}")
            memory.log_event("Dev tool error", {"error": str(e)})
