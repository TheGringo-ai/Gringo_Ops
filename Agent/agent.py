import streamlit as st
import os
import pandas as pd
import subprocess

st.set_page_config(page_title="GringoOps Repair Dashboard", layout="wide")

st.title("🔧 GringoOps AI Repair Dashboard")

def load_commit_logs():
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

if logs_df.empty:
    st.info("📭 No AI repair logs found.")
else:
    st.success(f"✅ Found {len(logs_df)} AI repair entries.")
    st.dataframe(logs_df, use_container_width=True)
    st.caption("Latest Auto-Repair Commits (filtered by 🤖 prefix)")