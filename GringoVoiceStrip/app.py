import streamlit as st
import whisper
import tempfile
import io
from pydub import AudioSegment
from streamlit_audio_recorder import audio_recorder

st.set_page_config(page_title="🎙️ Gringo Voice Strip", layout="centered")
st.title("🎙️ Gringo Voice Strip")
st.markdown("Speak your mind. Let GringoOps convert it to action.")

model = whisper.load_model("base")

tab1, tab2 = st.tabs(["📤 Upload Audio", "🎤 Record From Mic"])

with tab1:
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        with st.spinner("Transcribing uploaded file..."):
            result = model.transcribe(tmp_path)
            st.success("Done!")
            st.text_area("📝 Transcript", result["text"], height=300)
            st.markdown(f"""
                <script>
                var msg = new SpeechSynthesisUtterance("{result['text']}");
                window.speechSynthesis.speak(msg);
                </script>
            """, unsafe_allow_html=True)

with tab2:
    audio_bytes = audio_recorder()
    if audio_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="wav")
            audio.export(tmp_file.name, format="wav")
            tmp_path = tmp_file.name

        with st.spinner("Transcribing mic recording..."):
            result = model.transcribe(tmp_path)
            st.success("Done!")
            st.text_area("📝 Transcript", result["text"], height=300)
            st.markdown(f"""
                <script>
                var msg = new SpeechSynthesisUtterance("{result['text']}");
                window.speechSynthesis.speak(msg);
                </script>
            """, unsafe_allow_html=True)