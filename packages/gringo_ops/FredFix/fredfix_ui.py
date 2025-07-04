

import streamlit as st
import os

from FredFix.wizard import wizard_logic, wizard_state

try:
    from streamlit_extras.switch_page_button import switch_page
except ImportError:
    def switch_page(page_name):
    
        """Placeholder docstring for switch_page."""        st.session_state["_rerun_target"] = page_name
        st.experimental_rerun()

# Set up page config
st.set_page_config(page_title="🛠️ FredFix", layout="wide")

# Initialize state
wizard_state.init_state()

# Sidebar
st.sidebar.title("🛠️ FredFix Toolkit")
st.sidebar.markdown("A prompt-to-code tool with logging and export.")
if st.sidebar.button("⬅️ Return to Dashboard"):
    switch_page("gringoops_dashboard.py")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Prompt", "📂 Output", "📜 Logs", "🧪 Unit Test", "📄 Export PDF"])

with tab1:
    st.subheader("💬 Prompt to Generate Code")
    prompt = st.text_area("Enter prompt to generate code", height=200)
    model = st.selectbox("Model", ["gpt-4", "gpt-4o", "gpt-3.5-turbo"])
    filename = st.text_input("Filename", value="fredfix_output.py")

    if st.button("🚀 Generate"):
        output = wizard_logic.generate_code(prompt, model)
        path = wizard_logic.save_code_to_file(output, filename, "generated")
        wizard_logic.log_prompt(prompt, filename)
        st.session_state.current_output = output
        st.session_state.prompt_history.append(prompt)
        st.session_state.generated_files.append(path)
        st.success(f"Generated and saved to: {path}")

with tab2:
    st.subheader("📂 Generated Code Output")
    st.code(st.session_state.current_output or "No output yet.", language="python")

with tab3:
    st.subheader("📜 Prompt Log")
    if st.session_state.prompt_history:
        for i, p in enumerate(st.session_state.prompt_history[::-1]):
            st.markdown(f"**Prompt {len(st.session_state.prompt_history) - i}:** {p}")
    else:
        st.info("No prompt history yet.")

with tab4:
    st.subheader("🧪 Unit Test Generator")
    if st.session_state.current_output:
        test_code = f'''
import unittest
from {filename.replace(".py", "")} import *

class TestFredFixModule(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
'''
        st.code(test_code, language="python")
        st.download_button("⬇️ Download Unit Test", data=test_code, file_name=f"test_{filename}")
    else:
        st.info("Generate code first to create unit tests.")


# Export PDF Tab
with tab5:
    st.subheader("📄 Export Summary as PDF")
    if st.button("Export to PDF"):
        prompt_history = st.session_state.get("prompt_history", [])
        full_html = f"""
        <html>
        <head><meta charset='UTF-8'><style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #2c3e50; }}
            code {{ background: #f4f4f4; padding: 5px; display: block; margin-bottom: 10px; }}
        </style></head>
        <body>
        <h1>FredFix Report</h1>
        <p><b>Generated Modules:</b> {len(prompt_history)}</p>
        <ul>
        """
        for i, prompt in enumerate(prompt_history[::-1]):
            full_html += f"<li><b>Prompt {len(prompt_history)-i}:</b><br><code>{prompt}</code></li>"

        full_html += """
        </ul>
        </body>
        </html>
        """

        with open("fredfix_summary.html", "w", encoding="utf-8") as f:
            f.write(full_html)

        import pdfkit
        pdfkit.from_file("fredfix_summary.html", "fredfix_summary.pdf")

        with open("fredfix_summary.pdf", "rb") as pdf_file:
            st.download_button("⬇️ Download PDF", data=pdf_file, file_name="fredfix_summary.pdf")