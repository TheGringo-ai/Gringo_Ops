import streamlit as st
import os
import subprocess
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import tempfile
import datetime
import shutil
from openai import OpenAI

st.set_page_config(page_title="🧠 GringoOps Hub", layout="wide")

webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"video": False, "audio": True},
)

@st.cache_resource
def load_whisper_model():

    """Placeholder docstring for load_whisper_model."""    import whisper
    return whisper.load_model("base")
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
    st.header("🚀 Tool Launcher")
    selected_tool = st.selectbox("Select a tool", list(TOOLS.keys()))
    if st.button("Launch"):
        tool_path = os.path.expanduser(TOOLS[selected_tool])
        if os.path.exists(tool_path):
            try:
                subprocess.Popen(["env", f"PYTHONPATH={os.getcwd()}", "streamlit", "run", tool_path])
                st.success(f"{selected_tool} launched!")
            except Exception as e:
                st.error(f"Failed to launch tool: {e}")
        else:
            st.error(f"Tool not found at: {tool_path}")

# === Voice Recorder Section ===
st.subheader("🎤 Voice Transcription with Whisper")

st.info("🎙️ Audio stream started via WebRTC — recording & transcription support coming soon.")

if False:
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

st.divider()
st.subheader("🛠️ FredFix Command Console")

fredfix_cmd = st.text_input("Enter FredFix command:")

if 'fredfix_memory' not in st.session_state:
    st.session_state.fredfix_memory = []

if fredfix_cmd:
    st.session_state.fredfix_memory.append({"timestamp": datetime.datetime.now().isoformat(), "command": fredfix_cmd})
    st.success(f"Command logged: {fredfix_cmd}")

    # Optionally, run FredFix with command (assuming a CLI or script interface)
    fredfix_path = os.path.expanduser("~/Projects/GringoOps/FredFix/main.py")
    if os.path.exists(fredfix_path):
        try:
            # Run FredFix with command as argument
            result = subprocess.run(["python3", fredfix_path, fredfix_cmd], capture_output=True, text=True, timeout=30)
            st.text_area("FredFix Output:", result.stdout + result.stderr, height=150)
        except Exception as e:
            st.error(f"Error running FredFix: {e}")
    else:
        st.error("FredFix tool not found.")

st.markdown("### FredFix Command Log")
for entry in st.session_state.fredfix_memory[-10:]:
    st.write(f"{entry['timestamp']}: {entry['command']}")

st.divider()
st.subheader("🤖 AI Chat Assistant")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chat_prompt = st.chat_input("Ask your dev assistant...")

if chat_prompt:
    with st.chat_message("user"):
        st.markdown(chat_prompt)
    with st.chat_message("assistant"):
        if client.api_key:
            with st.spinner("FredFix is thinking..."):
                try:
                    response = ""
                    container = st.empty()
                    completion = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": chat_prompt}],
                        stream=True,
                    )
                    for chunk in completion:
                        if chunk.choices and chunk.choices[0].delta.content:
                            delta = chunk.choices[0].delta.content
                            response += delta
                            container.markdown(response)
                except Exception as e:
                    st.error(f"OpenAI error: {e}")
        else:
            st.warning("Missing OpenAI API key in environment. Please set OPENAI_API_KEY.")