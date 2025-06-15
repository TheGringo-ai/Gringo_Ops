import streamlit as st
from utils.translation import translate_text
from utils.quiz_generator import generate_quiz
from utils.pdf_exporter import export_training_pdf
from utils.logger import log_training_event

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
    if uploaded_file:
        st.success(translate("Document uploaded successfully."))

# Quiz Generator
with st.expander("🧠 Generate Training Quiz"):
    if uploaded_file:
        if st.button(translate("Generate Quiz")):
            questions = generate_quiz(uploaded_file.read().decode("utf-8"))
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
