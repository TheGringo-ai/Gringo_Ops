# 🚫 NOTE: Open Source Only Mode Enabled – No proprietary APIs (OpenAI/Gemini) will be used
import streamlit as st
import os
import pandas as pd
import json
import subprocess
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))  # Adds GringoOps root to PYTHONPATH

# --- MemoryManager import and instantiation moved to top for global availability ---
try:
    from FredFix.core.memory_manager import MemoryManager
except ImportError:
    class MemoryManager:
        def log_event(self, event, data=None):
            print(f"[Memory] {event} → {data or ''}")
        def save(self):
            print("[Memory] Saved")

try:
    memory = MemoryManager()
except Exception as mem_init_err:
    print(f"[MemoryManager Instantiation Failed] {mem_init_err}")
    class DummyMemory:
        def log_event(self, event, data=None):
            print(f"[Memory] {event} → {data or ''}")
        def save(self):
            print("[Memory] Saved")
    memory = DummyMemory()


st.set_page_config(page_title="GringoOps Repair Dashboard", layout="wide")

# --- Mission file loading, offline fallback ---
mission_path = "FredFix/core/mission.json"
if not os.path.exists(mission_path):
    # Auto-create with placeholder content
    os.makedirs(os.path.dirname(mission_path), exist_ok=True)
    with open(mission_path, "w") as mf:
        json.dump({"mission": "Define your GringoOps mission here."}, mf, indent=2)
    memory.log_event("Mission file auto-created", {"path": mission_path})

try:
    with open(mission_path) as mf:
        mission_data = json.load(mf)
        memory.log_event("Mission loaded", mission_data)
        st.session_state["mission_data"] = mission_data
except Exception as e:
    st.warning("⚠️ Could not load mission.json")
    memory.log_event("Mission load failed", {"error": str(e)})

# Load last session's selected chain if exists
try:
    with open("FredFix/core/last_chain.json", "r") as f:
        chain_data = json.load(f)
        st.session_state["selected_chain"] = chain_data.get("selected_chain", "")
except Exception:
    pass

st.sidebar.markdown("## ⚙️ Global Settings")
# Open Source Only: restrict model dropdown
available_models = ["mistral", "codellama", "llama2", "phi", "tinyllama"]
global_model = st.sidebar.selectbox("🧠 Default Model", available_models, key="global_model_selector")

def stream_model_response(prompt: str, model: str = None):
    if model is None:
        model = st.session_state.get("global_model_selector", "mistral")
    from subprocess import Popen, PIPE
    # Only allow open source models
    assert model in available_models, "Only open source models allowed"
    process = Popen(["ollama", "run", model], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, bufsize=1)
    process.stdin.write(prompt)
    process.stdin.close()
    for line in iter(process.stdout.readline, ''):
        yield line.strip()

try:
    memory.log_event("GringoOps AI Repair Dashboard launched")
except Exception as mem_err:
    print(f"[Memory Logging Failed] {mem_err}")
from FredFix.core.agent import run_agent

def transcribe_with_local_whisper(audio_file):
    try:
        temp_input = "temp_audio.m4a"
        with open(temp_input, "wb") as f:
            f.write(audio_file.read())

        # Call Whisper via subprocess (assumes whisper installed locally)
        result = subprocess.run(["whisper", temp_input, "--model", "base", "--language", "en", "--output_format", "txt"], capture_output=True, text=True)

        transcript_file = temp_input.replace(".m4a", ".txt")
        if os.path.exists(transcript_file):
            with open(transcript_file, "r") as f:
                return f.read()
        else:
            st.error("⚠️ Whisper did not produce a transcription file.")
            return ""
    except Exception as e:
        st.error(f"❌ Local Whisper failed: {e}")
        return ""


st.title("🔧 GringoOps AI Repair Dashboard")

with st.expander("🚀 System Autopilot Chain", expanded=False):
    autopilot_path = os.path.expanduser("~/Projects/GringoOps/FredFix/core/chains/system_autopilot.json")
    if os.path.exists(autopilot_path):
        if st.button("🧠 Run Autopilot"):
            try:
                process = subprocess.Popen(["python3", "agent.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                chain_input = f"10\n{autopilot_path}\n"
                process.stdin.write(chain_input)
                process.stdin.flush()
                output = process.communicate(timeout=30)[0]
                st.text_area("📋 Autopilot Output", value=output, height=200)
                memory.log_event("System Autopilot executed")
            except Exception as e:
                st.error(f"Autopilot failed: {e}")
    else:
        st.warning("Autopilot chain file not found.")


agent_choice = st.sidebar.selectbox("🤖 Select Agent", ["FredFix"], key="agent_selector")
st.session_state.selected_agent = agent_choice
st.sidebar.markdown(f"Current agent: **{agent_choice}**")
st.sidebar.markdown(f"📌 Persisted agent: **{st.session_state.get('selected_agent', 'None')}**")
st.sidebar.markdown("🔀 Automatically switch chains based on context")
auto_switch_enabled = st.sidebar.checkbox("Enable Chain Switching", value=True)
memory.log_event("Agent selected", {"agent": agent_choice})

# Mission context in sidebar
if "mission_data" in st.session_state:
    st.sidebar.markdown("📌 **Mission:**")
    st.sidebar.markdown(st.session_state["mission_data"].get("mission", "Not available."))

# --- Agent runner selection logic (Open Source Only) ---
def get_agent_runner(agent_name):
    # Only route to open source handler
    return run_agent

agent_runner = get_agent_runner(agent_choice)


# --- AI Command Prompt ---
with st.expander("💬 Direct AI Command Prompt", expanded=False):
    st.markdown("Ask your AI anything or give it a command:")
    # --- Shortcut buttons for common commands ---
    if st.button("🧪 Test: Summarize Logs"):
        st.session_state["user_prompt"] = "summarize_log"
    if st.button("⚙️ Test: Run Autopilot Chain"):
        st.session_state["user_prompt"] = "run_chain system_autopilot.json"

    user_prompt = st.text_area(
        "🧠 Enter a prompt or command",
        value=st.session_state.get("user_prompt", ""),
        placeholder="E.g., 'Summarize the latest repair log'"
    )
    if st.button("🚀 Send to Agent"):
        parsed = user_prompt.strip().lower()
        if parsed.startswith("run_chain "):
            chain_name = parsed.replace("run_chain ", "").strip()
            chain_path = os.path.expanduser(f"~/Projects/GringoOps/FredFix/core/chains/{chain_name}")
            if os.path.exists(chain_path):
                subprocess.run(["python3", "agent.py"], input=f"10\n{chain_path}\n", text=True)
                st.success(f"✅ Chain '{chain_name}' executed.")
                memory.log_event("Command run_chain", {"chain": chain_name})
            else:
                st.error(f"Chain '{chain_name}' not found.")
        elif parsed.startswith("summarize_log"):
            with st.spinner("Summarizing memory log..."):
                summary_prompt = f"Summarize this memory log:\n\n{user_prompt}"
                model = st.session_state.get("global_model_selector", "mistral")
                response = agent_runner(summary_prompt, model=model)
                st.text_area("📝 Summary", value=response, height=200)
                memory.log_event("Prompt command executed", {
                    "prompt": summary_prompt,
                    "response_snippet": response[:200],
                    "agent": agent_choice
                })
        else:
            model = st.session_state.get("global_model_selector", "mistral")
            response = agent_runner(user_prompt, model=model)
            st.text_area("📝 Agent Response", value=response, height=200)
            memory.log_event("Prompt command executed", {
                "prompt": user_prompt,
                "response_snippet": response[:200],
                "agent": agent_choice
            })

# --- Restore session-persisted selected chain if available ---
if "selected_chain" in st.session_state:
    st.sidebar.markdown(f"📂 Last Chain Used: `{st.session_state.selected_chain}`")

# --- Show currently synced chain in sidebar if available
if "selected_chain" in st.session_state:
    st.sidebar.markdown(f"🔄 Currently synced chain: `{st.session_state['selected_chain']}`")

# --- Audio Transcription Section ---
with st.container():
    st.markdown("---")
    st.subheader("🎤 Voice to Task")
    audio_file = st.file_uploader("Upload an audio file for transcription", type=["mp3", "wav", "m4a"])

    if audio_file is not None:
        transcript = ""
        if st.button("🧠 Transcribe and Generate Task"):
            with st.spinner("Transcribing..."):
                transcript = transcribe_with_local_whisper(audio_file)
                st.success("✅ Transcription complete")
                st.text_area("📝 Transcribed Text", value=transcript, height=150)

                # Run agent if transcript exists
                if transcript:
                    st.success(f"⚙️ Feeding transcript into {agent_choice} Agent...")
        # Only run agent if transcript is present (prevents crash)
        if transcript:
            model = st.session_state.get("global_model_selector", "mistral")
            agent_output = agent_runner(transcript, model=model)
            st.text_area("📋 AI Task Output", value=agent_output, height=200)
            memory.log_event("AI task generated", data={
                                "transcript_snippet": transcript[:100],
                                "agent_output_snippet": agent_output[:150]
                            })
        st.markdown("---")

def load_commit_logs():
    if not os.path.exists(".git"):
        st.warning("⚠️ This is not a Git repository. Attempting fallback log...")
        if os.path.exists("repair_history.log"):
            with open("repair_history.log", "r") as f:
                lines = [line.strip().split("|") for line in f if "|" in line]
                if lines:
                    df = pd.DataFrame(lines, columns=["Commit", "Author", "When", "Message"])
                    memory.log_event("Loaded AI repair logs", data={"count": len(df)})
                    return df
        else:
            # Create a test log entry if none exists
            with open("repair_history.log", "w") as f:
                f.write("07828e2|TheGringo-ai|Just now|🤖 Auto-repair: test repair log entry\n")
            with open("repair_history.log", "r") as f:
                lines = [line.strip().split("|") for line in f if "|" in line]
                if lines:
                    df = pd.DataFrame(lines, columns=["Commit", "Author", "When", "Message"])
                    memory.log_event("Loaded AI repair logs", data={"count": len(df)})
                    return df
        return pd.DataFrame()

    try:
        subprocess.run(["git", "pull"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logs = os.popen(
            'git log --pretty=format:"%h|%an|%ar|%s" --grep="repair" --regexp-ignore-case'
        ).read().strip().split("\n")
        parsed = [line.split("|") for line in logs if "|" in line]
        df = pd.DataFrame(parsed, columns=["Commit", "Author", "When", "Message"])
        memory.log_event("Loaded AI repair logs", data={"count": len(df)})
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

st.caption("🎙 Transcription powered by local Whisper (optional OpenAI fallback available).")

# --- Agent Chain Runner ---
# (os and subprocess already imported above)
with st.expander("🧠 Run Agent Chain"):
    chain_dir = os.path.expanduser("~/Projects/GringoOps/FredFix/core/chains")
    if not os.path.exists(chain_dir):
        st.warning("No chains/ directory found.")
    else:
        # --- Enhancement 1: File uploader for new chain JSON ---
        uploaded_chain = st.file_uploader("📤 Upload a new chain JSON", type=["json"])
        if uploaded_chain is not None:
            with open(os.path.join(chain_dir, uploaded_chain.name), "wb") as f:
                f.write(uploaded_chain.getbuffer())
            st.success(f"Uploaded: {uploaded_chain.name}")
            st.experimental_rerun()

        chain_files = [f for f in os.listdir(chain_dir) if f.endswith(".json")]
        if not chain_files:
            st.info("No chain JSON files found in /chains.")
        else:
            st.markdown("### ➕ Create New Chain")
            new_chain_name = st.text_input("New chain filename", value="new_chain.json")
            if st.button("🆕 Create Empty Chain"):
                new_path = os.path.join(chain_dir, new_chain_name)
                if not os.path.exists(new_path):
                    with open(new_path, "w") as f:
                        json.dump([{"name": "Step 1", "prompt": "{input}", "model": "mistral"}], f, indent=2)
                    st.success(f"Created new chain: {new_chain_name}")
                    st.experimental_rerun()
                else:
                    st.warning("Chain file already exists.")

            selected_chain = st.selectbox("📂 Select a chain to run", chain_files)
            st.session_state.selected_chain = selected_chain
            # Persist selected_chain to a file for session persistence
            import json as _json
            try:
                with open("FredFix/core/last_chain.json", "w") as f:
                    _json.dump({"selected_chain": selected_chain}, f)
            except Exception:
                pass
            full_path = os.path.join(chain_dir, selected_chain)

            # --- Chain Preview & Editor ---
            st.markdown("📝 Chain Preview & Editor")
            with open(full_path, "r") as f:
                chain_text = f.read()
            edited_chain_text = st.text_area("✍️ Edit Chain JSON", value=chain_text, height=250, key="chain_editor")

            if st.button("💾 Save Edited Chain"):
                try:
                    json.loads(edited_chain_text)  # validate
                    with open(full_path, "w") as f:
                        f.write(edited_chain_text)
                    st.success("✅ Chain saved.")
                    st.experimental_rerun()
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")

            # Show steps if valid JSON
            try:
                steps = json.loads(edited_chain_text)
                st.markdown("### 🔗 Chain Steps")
                for step in steps:
                    st.write(f"**{step.get('name', 'Unnamed')}** — Model: `{step.get('model', global_model)}`")
            except Exception:
                st.error("Invalid JSON in chain file.")

            # --- Enhancement 2: Manual input for {input} placeholder ---
            manual_input = st.text_area("✍️ Optional Input (replaces {input})", placeholder="Paste content or leave blank...")

            available_models = ["mistral", "codellama", "llama2", "phi", "tinyllama"]
            selected_model = st.selectbox("🧠 Override model for all steps (optional)", ["(keep per-step model)"] + available_models)

            # --- Enhancement 3: Real-time logging and status tracking ---
            if st.button("🚀 Run Chain Now"):
                status_placeholder = st.empty()
                with st.spinner("Running agent chain..."):
                    try:
                        # Load memory dict
                        memory_path = os.path.join("FredFix", "core", "agent_memory.json")
                        with open(memory_path, "r") as mf:
                            memory_dict = json.load(mf) if os.path.getsize(mf.name) > 0 else {}

                        TOOL_DIR = os.path.join(Path(__file__).resolve().parent.parent, "FredFix", "tools")

                        # --- Chain run log setup ---
                        full_log_path = os.path.join("FredFix", "core", "chain_run.log")
                        def append_to_chain_log(text):
                            with open(full_log_path, "a") as lf:
                                lf.write(text + "\n")

                        # Compose chain execution logic with per-step handling
                        output_lines = []
                        status = "⏳ Running..."
                        status_placeholder.info(status)
                        log_area = st.empty()
                        log_text = ""

                        for step in steps:
                            if selected_model != "(keep per-step model)":
                                step["model"] = selected_model
                            # Substitute {memory[key]} placeholders
                            if "prompt" in step and "{memory[" in step["prompt"]:
                                for key in memory_dict:
                                    placeholder = f"{{memory[{key}]}}"
                                    if placeholder in step["prompt"]:
                                        step["prompt"] = step["prompt"].replace(placeholder, str(memory_dict[key]))

                            # --- Inject mission context if available ---
                            if "mission_data" in st.session_state:
                                mission_summary = json.dumps(st.session_state["mission_data"])
                                step["prompt"] = f"[PROJECT MISSION CONTEXT]\n{mission_summary}\n\n" + step["prompt"]

                            # Tool execution support
                            if "tool" in step:
                                tool_path = os.path.join(TOOL_DIR, step["tool"])
                                args = step.get("args", "").split()
                                result = subprocess.run(["python3", tool_path] + args, capture_output=True, text=True)
                                memory.log_event("Tool step executed", {"tool": step["tool"], "stdout": result.stdout})
                                log_text += f"--- Tool: {step['tool']} ---\n{result.stdout}\n"
                                # Inject mission context into tool logs
                                if "mission_data" in st.session_state:
                                    log_text += f"\n--- Mission Context ---\n{json.dumps(st.session_state['mission_data'])}\n"
                                    append_to_chain_log(log_text)
                                    log_area.text(log_text[-2000:])
                                else:
                                    append_to_chain_log(log_text)
                                    log_area.text(log_text[-2000:])
                                # --- Dynamic Tool Insertion ---
                                if "insert_tool" in result.stdout:
                                    try:
                                        tool_name = result.stdout.split("insert_tool:")[1].strip().split()[0]
                                        tool_path_dyn = os.path.join(TOOL_DIR, tool_name)
                                        if os.path.exists(tool_path_dyn):
                                            result_dyn = subprocess.run(["python3", tool_path_dyn], capture_output=True, text=True)
                                            memory.log_event("Dynamically inserted tool executed", {"tool": tool_name, "stdout": result_dyn.stdout})
                                            log_text += f"\n--- Dynamic Tool: {tool_name} ---\n{result_dyn.stdout}\n"
                                            # Inject mission context into dynamic tool logs
                                            if "mission_data" in st.session_state:
                                                log_text += f"\n--- Mission Context ---\n{json.dumps(st.session_state['mission_data'])}\n"
                                                append_to_chain_log(log_text)
                                                log_area.text(log_text[-2000:])
                                            else:
                                                append_to_chain_log(log_text)
                                                log_area.text(log_text[-2000:])
                                    except Exception as e:
                                        st.error(f"⚠️ Failed to run dynamically inserted tool: {e}")
                                continue

                            # Agent execution (agent_runner)
                            prompt = step.get("prompt", "")
                            # Replace {input} with manual_input if present
                            if "{input}" in prompt:
                                prompt = prompt.replace("{input}", manual_input if manual_input.strip() != "" else "10")
                            # Use live model override
                            model = step.get("model", st.session_state.get("global_model_selector", "mistral"))
                            agent_output = agent_runner(prompt, model=model)
                            log_text += f"--- Step: {step.get('name','Unnamed')} ---\n{agent_output}\n"
                            append_to_chain_log(log_text)
                            log_area.text(log_text[-2000:])
                            memory.log_event("Chain step executed", {
                                "step": step.get("name", "Unnamed"),
                                "output_snippet": agent_output[:200],
                                "agent": agent_choice
                            })

                            # --- Memory enhancement: store prompt and output after each step ---
                            memory_dict["last_prompt"] = prompt
                            memory_dict["last_step_output"] = agent_output
                            memory.log_event("Step memory updated", {
                                "prompt": prompt,
                                "output": agent_output[:200]
                            })

                            # --- Loop Detection ---
                            if memory_dict.get("last_prompt") == prompt and memory_dict.get("last_step_output") == agent_output:
                                st.warning("⚠️ Detected potential infinite loop — skipping repeat.")
                                break

                            # --- Dynamic Tool Insertion ---
                            if "insert_tool" in agent_output:
                                try:
                                    tool_name = agent_output.split("insert_tool:")[1].strip().split()[0]
                                    tool_path_dyn = os.path.join(TOOL_DIR, tool_name)
                                    if os.path.exists(tool_path_dyn):
                                        result_dyn = subprocess.run(["python3", tool_path_dyn], capture_output=True, text=True)
                                        memory.log_event("Dynamically inserted tool executed", {"tool": tool_name, "stdout": result_dyn.stdout})
                                        log_text += f"\n--- Dynamic Tool: {tool_name} ---\n{result_dyn.stdout}\n"
                                        # Inject mission context into dynamic tool logs (from agent output)
                                        if "mission_data" in st.session_state:
                                            log_text += f"\n--- Mission Context ---\n{json.dumps(st.session_state['mission_data'])}\n"
                                            append_to_chain_log(log_text)
                                            log_area.text(log_text[-2000:])
                                        else:
                                            append_to_chain_log(log_text)
                                            log_area.text(log_text[-2000:])
                                except Exception as e:
                                    st.error(f"⚠️ Failed to run dynamically inserted tool: {e}")

                            # --- Mission-based auto chain switching ---
                            if auto_switch_enabled and "mission" in agent_output.lower():
                                try:
                                    mission = st.session_state.get("mission_data", {}).get("mission", "")
                                    if mission:
                                        next_chain = mission.split()[0].lower() + "_chain.json"
                                        next_path = os.path.join(chain_dir, next_chain)
                                        if os.path.exists(next_path):
                                            st.info(f"🔄 Mission-linked switch to: {next_chain}")
                                            subprocess.run(["python3", "agent.py"], input=f"10\n{next_path}\n", text=True)
                                            memory.log_event("Chain auto-switched via mission", {"next_chain": next_chain})
                                        else:
                                            st.warning(f"Mission-suggested chain '{next_chain}' not found.")
                                except Exception as e:
                                    st.error(f"❌ Mission-based auto-switch failed: {e}")

                            # --- Automatic chain switching based on agent output ---
                            if auto_switch_enabled and "switch_to_chain" in agent_output:
                                try:
                                    next_chain = agent_output.split("switch_to_chain:")[1].strip().split()[0]
                                    next_path = os.path.join(chain_dir, next_chain)
                                    if os.path.exists(next_path):
                                        st.info(f"🔄 Switching to chain: {next_chain}")
                                        subprocess.run(["python3", "agent.py"], input=f"10\n{next_path}\n", text=True)
                                        memory.log_event("Chain auto-switched", {"next_chain": next_chain})
                                    else:
                                        st.warning(f"Chain file '{next_chain}' not found.")
                                except Exception as e:
                                    st.error(f"Failed to auto-switch chain: {e}")

                            # --- Autonomous Recovery: retry failed steps (inside steps loop) ---
                            if "error" in agent_output.lower() or "exception" in agent_output.lower():
                                memory.log_event("Detected potential failure, attempting recovery")
                                retry_prompt = f"Try to recover from this error:\n\n{agent_output}"
                                retry_output = agent_runner(retry_prompt, model=model)
                                log_text += f"\n--- Recovery Attempt ---\n{retry_output}\n"
                                append_to_chain_log(f"--- Recovery Attempt ---\n{retry_output}")
                                log_area.text(log_text[-2000:])

                        # --- After the chain finishes, write memory_dict back to agent_memory.json ---
                        with open(memory_path, "w") as mf:
                            json.dump(memory_dict, mf, indent=2)

                        memory.log_event("Chain executed from UI", {"chain_file": selected_chain})
                        status = "✅ Chain complete"
                        status_placeholder.success(status)
                        subprocess.run(["git", "add", "."], cwd=os.getcwd())
                        subprocess.run(["git", "commit", "-m", f"🤖 Auto-commit: {selected_chain} run from dashboard"], cwd=os.getcwd())
                        subprocess.run(["git", "push"], cwd=os.getcwd())
                    except Exception as e:
                        status_placeholder.error("❌ Failed to run chain")
                        st.error(f"❌ Failed to run chain: {e}")

            # --- Custom autopilot builder template ---
            if st.button("🚀 Generate Starter Autopilot Chain"):
                model = st.session_state.get("global_model_selector", "mistral")
                autopilot_template = [
                    {"name": "Step 1", "prompt": "Summarize this input: {input}", "model": model},
                    {"name": "Step 2", "prompt": "Based on that summary, suggest improvements.", "model": model}
                ]
                new_path = os.path.join(chain_dir, "autopilot_template.json")
                with open(new_path, "w") as f:
                    json.dump(autopilot_template, f, indent=2)
                st.success("🚀 Autopilot starter chain created: autopilot_template.json")
                st.experimental_rerun()

# --- Memory Log Viewer ---
with st.expander("🧠 Memory Log Viewer"):
    memory_path = os.path.join(os.getcwd(), "FredFix", "core", "agent_memory.json")
    if not os.path.exists(memory_path):
        st.info("No memory log found at FredFix/core/agent_memory.json")
    else:
        try:
            with open(memory_path, "r") as f:
                try:
                    memory_data = json.load(f)
                except Exception:
                    memory_data = []

            if not memory_data:
                st.info("Memory log is empty.")
            else:
                try:
                    df = pd.DataFrame(memory_data)
                except Exception:
                    st.info("Memory log is not in tabular format.")
                    df = None
                if df is not None:
                    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
                    df = df.sort_values(by="timestamp", ascending=False)
                    unique_events = df["event"].dropna().unique().tolist()
                    selected_event = st.selectbox("Filter by event type", ["(all)"] + unique_events)

                    if selected_event != "(all)":
                        df = df[df["event"] == selected_event]

                    # Added full-text search
                    search_term = st.text_input("🔍 Search memory logs")
                    if search_term:
                        df = df[df.astype(str).apply(lambda row: row.str.contains(search_term, case=False)).any(axis=1)]

                    st.dataframe(df, use_container_width=True)
                    st.caption("Memory log loaded from agent_memory.json")

                    # Added chain usage chart
                    if "event" in df.columns:
                        chain_events = df[df["event"].str.contains("Chain executed", case=False, na=False)]
                        if not chain_events.empty:
                            st.subheader("📈 Chain Execution Over Time")
                            chain_events["count"] = 1
                            daily_counts = chain_events.groupby(chain_events["timestamp"].dt.date)["count"].count()
                            st.bar_chart(daily_counts)

                    # Added smart memory summarizer
                    if st.button("🧠 Summarize Memory Log with Local Agent"):
                        try:
                            summary_prompt = f"Summarize the following agent memory log in 5 bullet points:\n\n{df.to_json(orient='records')[:8000]}"
                            stream_placeholder = st.empty()
                            streamed_output = ""
                            model = st.session_state.get("global_model_selector", "mistral")
                            for chunk in stream_model_response(summary_prompt, model=model):
                                streamed_output += chunk + " "
                                stream_placeholder.text_area("📝 Summary", value=streamed_output.strip(), height=200)
                            memory.log_event("Generated memory summary")
                        except Exception as e:
                            st.error(f"Failed to summarize: {e}")

                    # Memory boosting from log
                    if st.button("📥 Boost Agent Memory from Log"):
                        try:
                            boost_prompt = f"Act as an AI assistant enhancing its long-term memory. Parse and retain useful information from this log:\n\n{df.to_json(orient='records')[:8000]}"
                            streamed_output = ""
                            model = st.session_state.get("global_model_selector", "mistral")
                            for chunk in stream_model_response(boost_prompt, model=model):
                                st.text(chunk.strip())
                                streamed_output += chunk + " "
                            memory.log_event("Boosted agent memory from logs", {"model_used": model})
                            # --- Enhancement: Update agent_memory.json with boosted insights ---
                            try:
                                with open(memory_path, "r") as mf:
                                    try:
                                        memory_dict = json.load(mf) if os.path.getsize(mf.name) > 0 else {}
                                    except Exception:
                                        memory_dict = {}
                            except Exception:
                                memory_dict = {}
                            memory_dict["boosted_insights"] = streamed_output.strip()
                            with open(memory_path, "w") as f:
                                json.dump(memory_dict, f, indent=2)
                        except Exception as e:
                            st.error(f"Failed to boost memory: {e}")

                    # Memory recall test button
                    if st.button("🔍 Test Memory Recall"):
                        try:
                            test_prompt = "What chains or tools have I recently used?"
                            model = st.session_state.get("global_model_selector", "mistral")
                            for chunk in stream_model_response(test_prompt, model=model):
                                st.text(chunk.strip())
                            memory.log_event("Memory recall test")
                        except Exception as e:
                            st.error(f"Failed to test memory: {e}")

                    # Show Project Mission button
                    if st.button("📖 Show Project Mission"):
                        if "mission_data" in st.session_state:
                            st.json(st.session_state["mission_data"])
                        else:
                            st.warning("No mission loaded.")
        except Exception as e:
            st.error(f"Failed to read memory file: {e}")


# --- Dev Tools Suite ---
with st.expander("🔧 Dev Tools Suite"):
    st.markdown("Run useful dev utilities on your codebase")

    TOOL_DIR = os.path.join(Path(__file__).resolve().parent.parent, "FredFix", "tools")
    if not os.path.exists(TOOL_DIR):
        st.warning("Tools folder not found.")
    else:
        tool_files = [f for f in os.listdir(TOOL_DIR) if f.endswith(".py")]
        if not tool_files:
            st.info("No Python tools found in tools directory.")
        else:
            selected_tool = st.selectbox("🛠️ Select a tool to run", tool_files)
            selected_path = os.path.join(TOOL_DIR, selected_tool)

            args = st.text_input("Optional arguments (space-separated)")
            if st.button("🚀 Run Tool"):
                try:
                    from subprocess import run
                    cmd = ["python3", selected_path] + args.strip().split()
                    result = run(cmd, capture_output=True, text=True)
                    st.code(result.stdout or "✅ No output", language="bash")
                    if result.stderr:
                        st.error(result.stderr)
                    memory.log_event("Dev tool run", {"tool": selected_tool, "args": args})
                    subprocess.run(["git", "add", "."], cwd=os.getcwd())
                    subprocess.run(["git", "commit", "-m", f"🤖 Auto-commit: {selected_tool} run from dashboard"], cwd=os.getcwd())
                    subprocess.run(["git", "push"], cwd=os.getcwd())
                except Exception as e:
                    st.error(f"❌ Failed to run tool: {e}")

memory.save()