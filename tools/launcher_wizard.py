import streamlit as st
import json
import os
import subprocess
import time

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "launcher_config.json")
ADMIN_PASSWORD = "admin123"  # Hardcoded passphrase
LOGO_PATH = "path/to/logo.png"  # Placeholder image path

if FIREBASE_AVAILABLE:
    try:
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        FIREBASE_INITIALIZED = True
    except Exception as e:
        st.error(f"Firebase initialization error: {e}")
        FIREBASE_AVAILABLE = False
        FIREBASE_INITIALIZED = False
else:
    FIREBASE_INITIALIZED = False

def upload_config_to_firestore(config):
    if not FIREBASE_AVAILABLE:
        return
    try:
        config_to_upload = dict(config)
        config_to_upload['last_updated'] = int(time.time())
        doc_ref = db.document('launchers/config')
        doc_ref.set(config_to_upload)
    except Exception as e:
        st.error(f"Failed to upload configuration to Firestore: {e}")

def download_config_from_firestore():
    if not FIREBASE_AVAILABLE:
        st.error("Firebase is not available.")
        return None
    try:
        doc_ref = db.document('launchers/config')
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            st.warning("No configuration found in Firestore.")
            return None
    except Exception as e:
        st.error(f"Failed to download configuration from Firestore: {e}")
        return None

def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        else:
            return {"groups": {}}
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return None

def save_config(config):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
        upload_config_to_firestore(config)
    except Exception as e:
        st.error(f"Error saving configuration: {e}")

def main():
    st.sidebar.image(LOGO_PATH, use_column_width=True)
    st.sidebar.title("User Role Selection")
    theme = st.sidebar.radio("Select Theme:", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown(
            """
            <style>
            .main {
                background-color: #0E1117;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    password_input = st.sidebar.text_input("Admin Password", type="password")
    if password_input == ADMIN_PASSWORD:
        role = "Admin"
    else:
        if password_input:
            st.sidebar.error("Incorrect password. Access downgraded to User.")
        role = "User"

    config = load_config()
    if config is None:
        st.error("Failed to load configuration file. Some features may be disabled.")
        config = {"groups": {}}

    if FIREBASE_INITIALIZED:
        st.sidebar.success("Cloud Sync: Connected")

        # Automatic sync from Firestore at launch
        firestore_config = download_config_from_firestore()
        if firestore_config is not None:
            # Remove last_updated from comparison
            local_config_compare = dict(config)
            local_config_compare.pop('last_updated', None)
            remote_config_compare = dict(firestore_config)
            remote_config_compare.pop('last_updated', None)
            if local_config_compare != remote_config_compare:
                st.sidebar.warning("Local configuration differs from Firestore version.")
                confirm_sync = st.sidebar.checkbox("Overwrite local config with Firestore version")
                if confirm_sync:
                    try:
                        with open(CONFIG_PATH, "w") as f:
                            json.dump(firestore_config, f, indent=4)
                        config = firestore_config
                        st.sidebar.success("Configuration automatically synced from Firestore.")
                    except Exception as e:
                        st.sidebar.error(f"Failed to overwrite local config: {e}")

        if st.sidebar.button("Download Config from Firestore"):
            confirm = st.sidebar.checkbox("Confirm overwrite of local config with Firestore version")
            if confirm:
                firestore_config = download_config_from_firestore()
                if firestore_config is not None:
                    try:
                        with open(CONFIG_PATH, "w") as f:
                            json.dump(firestore_config, f, indent=4)
                        config = firestore_config
                        st.sidebar.success("Configuration successfully synced from Firestore.")
                    except Exception as e:
                        st.sidebar.error(f"Failed to overwrite local config: {e}")
                else:
                    st.sidebar.warning("No configuration downloaded.")
            else:
                st.sidebar.info("Please confirm to overwrite local configuration.")

    with st.sidebar.expander("Onboarding Walkthrough"):
        st.markdown("""
        **Step 1:** Select your role (Admin or User) to access different features.  
        **Step 2 (Admin):** Use 'Add / Edit Launcher' tab to create or modify launcher entries.  
        **Step 3 (Admin & User):** Use 'Manage Launchers' tab to view, edit, launch, or delete entries.  
        **Step 4:** Use the export button to download the current configuration.  
        """)

    st.title("Launcher Wizard")

    # Display last updated timestamp if available
    last_updated = config.get('last_updated')
    if last_updated:
        try:
            readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_updated))
            st.markdown(f"**Configuration last updated:** {readable_time}")
        except Exception:
            pass

    if role == "Admin":
        tabs = st.tabs(["Add / Edit Launcher", "Manage Launchers"])
    else:
        st.info("This is a public-facing preview. Limited access for Users.")
        tabs = [st.container()]  # placeholder container for single tab

    if role == "Admin":
        with tabs[0]:
            name = st.text_input("Name")
            path = st.text_input("Path")

            if path and not os.path.exists(path):
                st.warning("The specified path does not exist.")

            groups = list(config.get("groups", {}).keys())
            groups_dropdown = ["Create New..."] + groups
            selected_group = st.selectbox("Group", groups_dropdown)

            if selected_group == "Create New...":
                new_group = st.text_input("New Group Name")
                group = new_group.strip()
            else:
                group = selected_group

            description = st.text_area("Description")

            if st.button("Submit"):
                if not name or not path or not group:
                    st.error("Name, Path, and Group are required fields.")
                    return

                if "groups" not in config:
                    config["groups"] = {}

                if group not in config["groups"]:
                    config["groups"][group] = []

                # Check if entry with same name exists, update it
                updated = False
                for entry in config["groups"][group]:
                    if entry.get("name") == name:
                        entry["path"] = path
                        entry["description"] = description
                        updated = True
                        break

                if not updated:
                    config["groups"][group].append({
                        "name": name,
                        "path": path,
                        "description": description
                    })

                save_config(config)
                st.success(f"Launcher entry for '{name}' in group '{group}' saved successfully.")

    if role == "Admin":
        with tabs[1]:
            st.subheader("Manage Current Launchers")
            if not config.get("groups"):
                st.info("No launcher entries found.")
            else:
                modified = False
                groups_to_delete = []
                for group, entries in list(config["groups"].items()):
                    st.markdown(f"### Group: {group}")
                    to_delete = []
                    for i, entry in enumerate(entries):
                        with st.expander(f"{entry['name']}"):
                            col1, col2 = st.columns([3,1])
                            with col1:
                                new_name = st.text_input(f"Name##{group}_{i}", value=entry["name"])
                                new_path = st.text_input(f"Path##{group}_{i}", value=entry["path"])
                                new_description = st.text_area(f"Description##{group}_{i}", value=entry.get("description", ""))
                                if new_path and not os.path.exists(new_path):
                                    st.warning("The specified path does not exist.")
                            with col2:
                                if st.button("Delete", key=f"del_{group}_{i}"):
                                    to_delete.append(i)
                                    modified = True
                                    st.experimental_rerun()
                                if st.button("Launch", key=f"launch_{group}_{i}"):
                                    try:
                                        if os.name == 'nt':
                                            os.startfile(new_path)
                                        elif os.name == 'posix':
                                            subprocess.Popen(['xdg-open', new_path])
                                        else:
                                            st.error("Unsupported OS for launching files.")
                                    except Exception as e:
                                        st.error(f"Failed to launch: {e}")

                            if (new_name != entry["name"] or new_path != entry["path"] or new_description != entry.get("description", "")):
                                entry["name"] = new_name
                                entry["path"] = new_path
                                entry["description"] = new_description
                                modified = True

                    # Delete entries marked for deletion
                    for index in sorted(to_delete, reverse=True):
                        del entries[index]
                    # Remove group if empty
                    if not entries:
                        groups_to_delete.append(group)
                        modified = True
                for group in groups_to_delete:
                    del config["groups"][group]

                if modified:
                    save_config(config)
                    st.success("Configuration updated.")

            # Export / Download config button
            config_data = None
            try:
                if os.path.exists(CONFIG_PATH):
                    with open(CONFIG_PATH, "r") as f:
                        config_data = f.read()
                else:
                    st.warning("Configuration file not found for export.")
            except Exception as e:
                st.error(f"Error reading configuration for export: {e}")

            if config_data:
                st.download_button(
                    label="Export Configuration",
                    data=config_data,
                    file_name="launcher_config.json",
                    mime="application/json"
                )
    else:
        # User role: show Manage Launchers only in main area
        st.subheader("Manage Current Launchers")
        if not config.get("groups"):
            st.info("No launcher entries found.")
        else:
            modified = False
            groups_to_delete = []
            for group, entries in list(config["groups"].items()):
                st.markdown(f"### Group: {group}")
                to_delete = []
                for i, entry in enumerate(entries):
                    with st.expander(f"{entry['name']}"):
                        col1, col2 = st.columns([3,1])
                        with col1:
                            new_name = st.text_input(f"Name##{group}_{i}", value=entry["name"])
                            new_path = st.text_input(f"Path##{group}_{i}", value=entry["path"])
                            new_description = st.text_area(f"Description##{group}_{i}", value=entry.get("description", ""))
                            if new_path and not os.path.exists(new_path):
                                st.warning("The specified path does not exist.")
                        with col2:
                            if st.button("Delete", key=f"del_{group}_{i}"):
                                to_delete.append(i)
                                modified = True
                                st.experimental_rerun()
                            if st.button("Launch", key=f"launch_{group}_{i}"):
                                try:
                                    if os.name == 'nt':
                                        os.startfile(new_path)
                                    elif os.name == 'posix':
                                        subprocess.Popen(['xdg-open', new_path])
                                    else:
                                        st.error("Unsupported OS for launching files.")
                                except Exception as e:
                                    st.error(f"Failed to launch: {e}")

                        if (new_name != entry["name"] or new_path != entry["path"] or new_description != entry.get("description", "")):
                            entry["name"] = new_name
                            entry["path"] = new_path
                            entry["description"] = new_description
                            modified = True

                # Delete entries marked for deletion
                for index in sorted(to_delete, reverse=True):
                    del entries[index]
                # Remove group if empty
                if not entries:
                    groups_to_delete.append(group)
                    modified = True
            for group in groups_to_delete:
                del config["groups"][group]

            if modified:
                save_config(config)
                st.success("Configuration updated.")

        # Export / Download config button
        config_data = None
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    config_data = f.read()
            else:
                st.warning("Configuration file not found for export.")
        except Exception as e:
            st.error(f"Error reading configuration for export: {e}")

        if config_data:
            st.download_button(
                label="Export Configuration",
                data=config_data,
                file_name="launcher_config.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
