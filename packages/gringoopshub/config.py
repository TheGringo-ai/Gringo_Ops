import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.translation import translate_text
try:
    from utils.quiz_generator import generate_quiz
except ModuleNotFoundError:
    def generate_quiz(*args, **kwargs):
        st.warning("Quiz generation is not available. Please ensure utils/quiz_generator.py exists.")
        return []
try:
    from utils.pdf_exporter import export_training_pdf
except ModuleNotFoundError:
    def export_training_pdf(*args, **kwargs):
        st.warning("PDF export is not available. Please ensure utils/pdf_exporter.py exists.")
        return b""
try:
    from utils.logger import log_training_event
except ModuleNotFoundError:
    def log_training_event(*args, **kwargs):
        st.warning("Training event logging is not available. Please ensure utils/logger.py exists.")

st.set_page_config(page_title="LineSmart Technician Hub", layout="wide")

st.title("🛠️ LineSmart Technician Dashboard")

# Language Toggle
lang = st.selectbox("🌐 Language", ["English", "Spanish"])
translate = lambda text: translate_text(text, lang)

# Technician Info
with st.expander("📋 Technician Information"):
    name = st.text_input(translate("Technician Name"))
    department = st.text_input(translate("Department"))
    equipment = st.text_input(translate("Assigned Equipment"))

# Document Upload
with st.expander("📄 Upload Training Material"):
    uploaded_file = st.file_uploader(translate("Upload a source document"), type=["pdf", "docx", "txt"])
    file_text = None
    if uploaded_file:
        st.success(translate("Document uploaded successfully."))
        if uploaded_file.type == "application/pdf":
            try:
                import fitz  # PyMuPDF
                uploaded_file.seek(0)
                with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                    file_text = "".join([page.get_text() for page in doc])
            except Exception as e:
                st.warning(f"PDF extraction failed: {e}")
        else:
            try:
                uploaded_file.seek(0)
                file_text = uploaded_file.read().decode("utf-8")
            except Exception as e:
                st.warning(f"File read failed: {e}")

# Quiz Generator
with st.expander("🧠 Generate Training Quiz"):
    if uploaded_file and file_text:
        if st.button(translate("Generate Quiz")):
            questions = generate_quiz(file_text)
            for q in questions:
                st.markdown(f"**Q:** {q['question']}")
                for option in q['options']:
                    st.markdown(f"- {option}")
    else:
        st.info(translate("Please upload a document to generate a quiz."))

# Export Training as PDF
with st.expander("📥 Export Training Summary as PDF"):
    if uploaded_file and name:
        if st.button(translate("Export Training PDF")):
            uploaded_file.seek(0)
            pdf_bytes = export_training_pdf(name, department, equipment, uploaded_file.read())
            st.download_button(
                label=translate("Download Training PDF"),
                data=pdf_bytes,
                file_name=f"{name}_training_summary.pdf",
                mime="application/pdf"
            )

# Log Training Completion
with st.expander("✅ Log Technician Training"):
    if name and uploaded_file:
        if st.button(translate("Log Training Completion")):
            log_training_event(name, equipment)
            st.success(translate("Training logged successfully."))
    else:
        st.warning(translate("Technician name and training document required."))
