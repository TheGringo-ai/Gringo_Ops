import streamlit as st

def extract_pdf_text(uploaded_file):
    """Extracts text from an uploaded PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        # Ensure the file pointer is at the beginning
        uploaded_file.seek(0)
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    except ImportError:
        st.error("PyMuPDF is not installed. Please run 'pip install PyMuPDF' to enable PDF processing.")
        return ""
    except Exception as e:
        st.warning(f"PDF extraction failed: {e}")
        return ""