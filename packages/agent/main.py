import streamlit as st
import os
import pandas as pd
import subprocess
import openai

st.set_page_config(page_title="GringoOps Repair Dashboard", layout="wide")


st.title("🔧 GringoOps AI Repair Dashboard")

# --- Audio Transcription Section ---
with st.container():
    st.markdown("---")
    st.subheader("🎤 Voice to Task")
    audio_file = st.file_uploader("Upload an audio file for transcription", type=["mp3", "wav", "m4a"])

    if audio_file is not None:
        if st.button("🧠 Transcribe and Generate Task"):
            with st.spinner("Transcribing..."):
                transcript = transcribe_with_openai(audio_file)
                st.success("✅ Transcription complete")
                st.text_area("📝 Transcribed Text", value=transcript, height=150)

                # Placeholder for future AI task generation
                if transcript:
                    st.info("⚙️ This transcript can now be fed into your AI task engine (e.g. FredFix)")
    st.markdown("---")

def transcribe_with_openai(audio_file):
    """Placeholder docstring for transcribe_with_openai."""
    try:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        result = openai.Audio.transcribe("whisper-1", audio_file)
        return result["text"]
    except Exception as e:
        st.error(f"❌ Transcription failed: {e}")
        return ""

def load_commit_logs():
    """Placeholder docstring for load_commit_logs."""
    if not os.path.exists(".git"):
        st.warning("⚠️ This is not a Git repository. Attempting fallback log...")
        if os.path.exists("repair_history.log"):
            with open("repair_history.log", "r") as f:
                lines = [line.strip().split("|") for line in f if "|" in line]
                if lines:
                    return pd.DataFrame(lines, columns=["Commit", "Author", "When", "Message"])
        else:
            # Create a test log entry if none exists
            with open("repair_history.log", "w") as f:
                f.write("07828e2|TheGringo-ai|Just now|🤖 Auto-repair: test repair log entry\n")
            with open("repair_history.log", "r") as f:
                lines = [line.strip().split("|") for line in f if "|" in line]
                if lines:
                    return pd.DataFrame(lines, columns=["Commit", "Author", "When", "Message"])
        return pd.DataFrame()

    try:
        subprocess.run(["git", "pull"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logs = os.popen(
            'git log --pretty=format:"%h|%an|%ar|%s" --grep="repair" --regexp-ignore-case'
        ).read().strip().split("\n")
        parsed = [line.split("|") for line in logs if "|" in line]
        df = pd.DataFrame(parsed, columns=["Commit", "Author", "When", "Message"])
        return df
    except Exception as e:
        st.error(f"❌ Error loading logs: {e}")
        return pd.DataFrame()

REFRESH_BUTTON = st.button("🔁 Refresh Log")

if REFRESH_BUTTON or 'logs_df' not in st.session_state:
    st.session_state.logs_df = load_commit_logs()

logs_df = st.session_state.logs_df

# --- Repair Logs Section ---
with st.container():
    st.subheader("🛠️ AI Repair Logs")
    if logs_df.empty:
        st.info("📭 No AI repair logs found.")
    else:
        st.success(f"✅ Found {len(logs_df)} AI repair entries.")
        st.dataframe(logs_df, use_container_width=True)
        st.caption("Latest Auto-Repair Commits (filtered by 🤖 prefix)")

st.caption("🎙 Whisper transcription is powered by the OpenAI Whisper API.")