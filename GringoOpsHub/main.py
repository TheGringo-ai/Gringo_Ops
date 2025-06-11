@st.cache_resource
def load_whisper_model():
    import whisper
    return whisper.load_model("base")


import streamlit as st
import os
import subprocess
from streamlit_audio_recorder import audio_recorder
import tempfile
import datetime
import shutil

st.set_page_config(page_title="🧠 GringoOps Hub", layout="wide")
st.title("🧠 GringoOps Productivity Hub")
st.markdown("Launch tools or record audio for Whisper-based transcription.")

# === Tool Launcher Section ===
TOOLS = {
    "🎙️ Gringo Voice Strip": "~/Projects/GringoOps/GringoVoiceStrip/main.py",
    "📋 LineSmart Trainer": "~/Projects/GringoOps/LineSmart/main.py",
    "🛠️ ChatterFix CMMS": "~/Projects/GringoOps/ChatterFix/main.py",
    "🧬 Agent": "~/Projects/GringoOps/Agent/main.py",
    "🔧 FredFix Dev Agent": "~/Projects/GringoOps/FredFix/main.py",
    "🚄 Bullet Train": "~/Projects/GringoOps/BulletTrain/main.py"
}

with st.sidebar:
    st.header("🚀 Launch Tool")
    selected_tool = st.selectbox("Select a tool", list(TOOLS.keys()))
    if st.button("Launch"):
        tool_path = os.path.expanduser(TOOLS[selected_tool])
        if os.path.exists(tool_path):
            subprocess.Popen(["streamlit", "run", tool_path])
            st.success(f"{selected_tool} launched!")
        else:
            st.error(f"Tool not found at: {tool_path}")

# === Voice Recorder Section ===
st.subheader("🎤 Quick Voice Transcription")

audio_bytes = audio_recorder(pause_threshold=3.0, sample_rate=44100)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        temp_audio_path = f.name

    # Move to GringoVoiceStrip if needed
    permanent_path = os.path.expanduser("~/Projects/GringoOps/GringoVoiceStrip/recorded.wav")
    shutil.move(temp_audio_path, permanent_path)
    st.success("✅ Audio saved for transcription.")

    # Optionally: Trigger transcription here
    if st.button("🧠 Transcribe"):
        try:
            model = load_whisper_model()
            result = model.transcribe(permanent_path)
            st.markdown("**📝 Transcription:**")
            st.write(result["text"])
        except Exception as e:
            st.error(f"Failed to transcribe audio: {e}")