import streamlit as st
from backend import vision_agent
from PIL import Image
import io
from frontend.auth_utils import enforce_auth

# --- Page Config and Auth ---
st.set_page_config(layout="wide", page_title="Vision AI Agent")
st.title("👁️ Vision AI Agent")

enforce_auth()
# --- End Auth ---

st.markdown("""
Upload an image of a part, a serial number, or a document. The Vision Agent will analyze it and provide information.
""")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)

    st.subheader("Analysis")
    with st.spinner("Analyzing image..."):
        try:
            # Convert uploaded file to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format)
            img_bytes = img_byte_arr.getvalue()

            # --- Text Recognition (OCR) ---
            st.write("**Extracted Text (OCR):**")
            text_result = vision_agent.extract_text_from_image(img_bytes)
            if text_result:
                st.code(text_result, language=None)
            else:
                st.info("No text detected.")

            # --- Part Recognition ---
            st.write("**Object & Part Recognition:**")
            objects_result = vision_agent.identify_parts_in_image(img_bytes)
            if objects_result:
                for obj in objects_result:
                    st.markdown(f"- **{obj['name']}** (Confidence: {obj['score']:.2%})")
            else:
                st.info("No specific parts or objects recognized.")

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
