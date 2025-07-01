import os
import json
import subprocess

# === Configuration ===
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

REQUIRED_FILES = [
    "firebase.json",
    "package.json",
    "vite.config.ts",
    "README.md",
    "gui_launcher.py",
    "streamlit_app.py",
    "gringoops_dashboard.py",
    "src/App.tsx",
    "src/pages/Dashboard.tsx",
    "src/pages/Admin.tsx",
    "src/pages/Reports.tsx",
    "src/pages/AgentChat.tsx",
    "src/pages/FileHistory.tsx",
    "src/firebase.ts",
    "public/index.html"
]

# === Utilities ===
def check_file(path: str) -> bool:
    """Check if a given file path exists."""
    return os.path.exists(os.path.join(PROJECT_DIR, path))

def check_file_contents(path: str) -> bool:
    """Check if file exists and is non-trivially sized (>10 bytes)."""
    full_path = os.path.join(PROJECT_DIR, path)
    return os.path.isfile(full_path) and os.path.getsize(full_path) > 10


def check_folder_structure():
    required_dirs = ["src/pages", "public"]
    print("\n📁 Folder Structure")
    print("=" * 50)
    folder_results = {}
    for folder in required_dirs:
        full_path = os.path.join(PROJECT_DIR, folder)
        if os.path.isdir(full_path):
            print(f"✅ Folder exists: {folder}")
            folder_results[folder] = "found"
        else:
            print(f"❌ Missing folder: {folder}")
            folder_results[folder] = "missing"
    return folder_results


def check_dependencies():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    print("\n📦 Dependency Check")
    print("=" * 50)
    required_deps = ["react", "vite", "firebase"]
    dep_results = {}
    if not os.path.exists(package_json_path):
        print("❌ package.json not found.")
        for dep in required_deps:
            dep_results[dep] = "package.json missing"
        return dep_results
    with open(package_json_path, "r") as f:
        try:
            pkg = json.load(f)
            deps = pkg.get("dependencies", {})
            for dep in required_deps:
                if dep in deps:
                    print(f"✅ {dep} found")
                    dep_results[dep] = "found"
                else:
                    print(f"❌ {dep} missing")
                    dep_results[dep] = "missing"
        except json.JSONDecodeError:
            print("❌ Failed to parse package.json")
            for dep in required_deps:
                dep_results[dep] = "package.json parse error"
    return dep_results


# Validate required scripts in package.json
def check_scripts():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    print("\n📝 NPM Scripts Check")
    print("=" * 50)
    required_scripts = ["dev", "build", "lint", "deploy"]
    scripts_results = {}
    if not os.path.exists(package_json_path):
        print("❌ package.json not found.")
        for script in required_scripts:
            scripts_results[script] = "package.json missing"
        return scripts_results
    with open(package_json_path, "r") as f:
        try:
            pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            for script in required_scripts:
                if script in scripts:
                    print(f"✅ Script '{script}' found")
                    scripts_results[script] = "found"
                else:
                    print(f"❌ Script '{script}' missing")
                    scripts_results[script] = "missing"
        except json.JSONDecodeError:
            print("❌ Failed to parse package.json")
            for script in required_scripts:
                scripts_results[script] = "package.json parse error"
    return scripts_results


# Run TypeScript check
def run_ts_check():
    print("\n🧪 TypeScript Check")
    print("=" * 50)
    ts_result = {"status": "", "details": ""}
    try:
        result = subprocess.run(["npx", "tsc", "--noEmit"], cwd=PROJECT_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ No TypeScript issues")
            ts_result["status"] = "ok"
        else:
            print("❌ TypeScript issues detected:")
            print(result.stdout)
            ts_result["status"] = "issues"
            ts_result["details"] = result.stdout
    except FileNotFoundError:
        print("❌ tsc not found. Run `npm install` first.")
        ts_result["status"] = "tsc not found"
    return ts_result


# Save a summary report (markdown and JSON)
def export_report(
    file_statuses,
    folder_statuses,
    dep_statuses,
    script_statuses,
    ts_status,
    cicd_status,
):
    report_path = os.path.join(PROJECT_DIR, "patch_scan_report.md")
    json_report_path = os.path.join(PROJECT_DIR, "patch_scan_report.json")
    # Markdown
    with open(report_path, "w") as report:
        report.write("# Patch Scan Report\n\n")
        # File checks
        report.write("## 📄 File Checks\n")
        for file, status in file_statuses.items():
            if status == "found":
                report.write(f"- ✅ Found: `{file}`\n")
            elif status == "empty":
                report.write(f"- ⚠️ Empty File: `{file}`\n")
            else:
                report.write(f"- ❌ Missing: `{file}`\n")
        # Folder checks
        report.write("\n## 📁 Folder Structure\n")
        for folder, status in folder_statuses.items():
            if status == "found":
                report.write(f"- ✅ Folder exists: `{folder}`\n")
            else:
                report.write(f"- ❌ Missing folder: `{folder}`\n")
        # Dependency checks
        report.write("\n## 📦 Dependency Check\n")
        for dep, status in dep_statuses.items():
            emoji = "✅" if status == "found" else "❌"
            report.write(f"- {emoji} {dep}: {status}\n")
        # Script checks
        report.write("\n## 📝 NPM Scripts Check\n")
        for script, status in script_statuses.items():
            emoji = "✅" if status == "found" else "❌"
            report.write(f"- {emoji} {script}: {status}\n")
        # TypeScript check
        report.write("\n## 🧪 TypeScript Check\n")
        if ts_status["status"] == "ok":
            report.write("- ✅ No TypeScript issues\n")
        elif ts_status["status"] == "issues":
            report.write("- ❌ TypeScript issues detected\n")
            report.write(f"  - Details: {ts_status.get('details','').strip()[:200]}...\n")
        else:
            report.write(f"- ❌ {ts_status['status']}\n")
        # CI/CD readiness
        report.write("\n## 🚦 CI/CD Readiness\n")
        if cicd_status["ready"]:
            report.write("- ✅ Project appears CI/CD ready (firebase.json and vite.config.ts present)\n")
        else:
            report.write("- ⚠️ CI/CD readiness incomplete. See details below.\n")
        for k, v in cicd_status["details"].items():
            report.write(f"  - {k}: {v}\n")
    print(f"\n📝 Report saved to: {report_path}")
    # JSON
    json_report = {
        "files": file_statuses,
        "folders": folder_statuses,
        "dependencies": dep_statuses,
        "scripts": script_statuses,
        "typescript": ts_status,
        "cicd": cicd_status,
    }
    with open(json_report_path, "w") as jf:
        json.dump(json_report, jf, indent=2)
    print(f"📊 JSON report saved to: {json_report_path}")


# CI/CD readiness scan
def check_cicd_readiness():
    status = {"ready": False, "details": {}}
    # Check firebase.json
    firebase_path = os.path.join(PROJECT_DIR, "firebase.json")
    vite_path = os.path.join(PROJECT_DIR, "vite.config.ts")
    firebase_ok = os.path.isfile(firebase_path)
    vite_ok = os.path.isfile(vite_path)
    # Check firebase.json has some keys
    if firebase_ok:
        try:
            with open(firebase_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and len(data) > 0:
                status["details"]["firebase.json"] = "present & valid"
                firebase_ok = True
            else:
                status["details"]["firebase.json"] = "present but empty or invalid"
                firebase_ok = False
        except Exception:
            status["details"]["firebase.json"] = "present but not valid JSON"
            firebase_ok = False
    else:
        status["details"]["firebase.json"] = "missing"
    # Check vite.config.ts (just check for non-empty file)
    if vite_ok:
        if os.path.getsize(vite_path) > 10:
            status["details"]["vite.config.ts"] = "present & non-empty"
            vite_ok = True
        else:
            status["details"]["vite.config.ts"] = "present but nearly empty"
            vite_ok = False
    else:
        status["details"]["vite.config.ts"] = "missing"
    # Ready if both are present & valid
    status["ready"] = firebase_ok and vite_ok
    return status

# === Main Logic ===
def main():
    print(f"\n🔍 Scanning project directory: {PROJECT_DIR}\n{'='*50}")
    # File checks with content awareness
    file_statuses = {}
    missing_for_placeholder = []
    print("## 📄 File Checks")
    print("=" * 50)
    for file in REQUIRED_FILES:
        if check_file(file):
            if check_file_contents(file):
                print(f"✅ Found:   {file}")
                file_statuses[file] = "found"
            else:
                print(f"⚠️ Empty File: {file}")
                file_statuses[file] = "empty"
        else:
            print(f"❌ Missing: {file}")
            file_statuses[file] = "missing"
            missing_for_placeholder.append(file)

    print("\n📋 Summary")
    print("=" * 50)
    if not missing_for_placeholder:
        print("🎉 All required files are present and accounted for.\n")
    else:
        print(f"⚠️  {len(missing_for_placeholder)} missing file(s) detected.\n")
        print("💡 To create placeholders, run the following:")
        for file in missing_for_placeholder:
            placeholder_path = os.path.join(PROJECT_DIR, file)
            print(f"touch {placeholder_path}")
        print()
        # Actually create placeholder content in missing files
        for file in missing_for_placeholder:
            full_path = os.path.join(PROJECT_DIR, file)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                if file.endswith(".ts") or file.endswith(".tsx"):
                    component_name = os.path.splitext(os.path.basename(file))[0].replace("-", "").replace(" ", "")
                    f.write(
                        f"// Auto-generated placeholder with Firebase logic\n"
                        f"import {{ useEffect, useState }} from 'react';\n"
                        f"import {{ db }} from '../firebase';\n\n"
                        f"export default function {component_name}() {{\n"
                        f"  const [data, setData] = useState([]);\n\n"
                        f"  useEffect(() => {{\n"
                        f"    const unsubscribe = db.collection('{component_name.lower()}').onSnapshot(snapshot => {{\n"
                        f"      const docs = snapshot.docs.map(doc => ({{ id: doc.id, ...doc.data() }}));\n"
                        f"      setData(docs);\n"
                        f"    }});\n"
                        f"    return () => unsubscribe();\n"
                        f"  }}, []);\n\n"
                        f"  return (\n"
                        f"    <div>\n"
                        f"      <h2>{component_name} (Live Firebase Data)</h2>\n"
                        f"      <pre>{{JSON.stringify(data, null, 2)}}</pre>\n"
                        f"    </div>\n"
                        f"  );\n"
                        f"}}\n"
                    )
                elif file.endswith(".json"):
                    # Special config for firebase.json placeholder
                    if os.path.basename(file) == "firebase.json":
                        f.write(json.dumps({
                            "hosting": {
                                "public": "dist",
                                "cleanUrls": True,
                                "ignore": [
                                    "firebase.json",
                                    "**/.*",
                                    "**/node_modules/**"
                                ],
                                "rewrites": [
                                    {
                                        "source": "**",
                                        "destination": "/index.html"
                                    }
                                ]
                            }
                        }, indent=2))
                    else:
                        f.write("{}\n")
                elif file.endswith(".html"):
                    f.write("<!doctype html>\n<html><head><title>Placeholder</title></head><body><h1>Placeholder</h1></body></html>\n")
                elif file.endswith(".py"):
                    f.write("# Auto-generated placeholder\n\nprint('Placeholder file: {}')\n".format(file))
                else:
                    f.write("// Placeholder\n")
            print(f"📝 Created placeholder: {file}")

    # --- Enhancements: folder, dependencies, scripts, typescript, cicd, report ---
    folder_statuses = check_folder_structure()
    dep_statuses = check_dependencies()
    script_statuses = check_scripts()
    ts_status = run_ts_check()
    cicd_status = check_cicd_readiness()
    # For files flagged as "empty", create minimal placeholder content
    for file, status in file_statuses.items():
        if status == "empty":
            full_path = os.path.join(PROJECT_DIR, file)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                if file.endswith(".ts") or file.endswith(".tsx"):
                    component_name = os.path.splitext(os.path.basename(file))[0].replace("-", "").replace(" ", "")
                    f.write(
                        f"// Auto-generated placeholder with Firebase logic\n"
                        f"import {{ useEffect, useState }} from 'react';\n"
                        f"import {{ db }} from '../firebase';\n\n"
                        f"export default function {component_name}() {{\n"
                        f"  const [data, setData] = useState([]);\n\n"
                        f"  useEffect(() => {{\n"
                        f"    const unsubscribe = db.collection('{component_name.lower()}').onSnapshot(snapshot => {{\n"
                        f"      const docs = snapshot.docs.map(doc => ({{ id: doc.id, ...doc.data() }}));\n"
                        f"      setData(docs);\n"
                        f"    }});\n"
                        f"    return () => unsubscribe();\n"
                        f"  }}, []);\n\n"
                        f"  return (\n"
                        f"    <div>\n"
                        f"      <h2>{component_name} (Live Firebase Data)</h2>\n"
                        f"      <pre>{{JSON.stringify(data, null, 2)}}</pre>\n"
                        f"    </div>\n"
                        f"  );\n"
                        f"}}\n"
                    )
                elif file.endswith(".json"):
                    # Special config for firebase.json placeholder
                    if os.path.basename(file) == "firebase.json":
                        f.write(json.dumps({
                            "hosting": {
                                "public": "dist",
                                "cleanUrls": True,
                                "ignore": [
                                    "firebase.json",
                                    "**/.*",
                                    "**/node_modules/**"
                                ],
                                "rewrites": [
                                    {
                                        "source": "**",
                                        "destination": "/index.html"
                                    }
                                ]
                            }
                        }, indent=2))
                    else:
                        f.write("{}\n")
                elif file.endswith(".html"):
                    f.write("<!doctype html>\n<html><head><title>Placeholder</title></head><body><h1>Placeholder</h1></body></html>\n")
                elif file.endswith(".py"):
                    f.write("# Auto-generated placeholder\n\nprint('Placeholder file: {}')\n".format(file))
                else:
                    f.write("// Placeholder\n")
            print(f"📝 Wrote minimal placeholder content to empty file: {file}")
    # Print CI/CD readiness
    print("\n🚦 CI/CD Readiness")
    print("=" * 50)
    if cicd_status["ready"]:
        print("✅ Project appears CI/CD ready (firebase.json and vite.config.ts present & valid)")
    else:
        print("⚠️ CI/CD readiness incomplete. See details below.")
        for k, v in cicd_status["details"].items():
            print(f"  - {k}: {v}")
    export_report(
        file_statuses,
        folder_statuses,
        dep_statuses,
        script_statuses,
        ts_status,
        cicd_status,
    )

if __name__ == "__main__":
    main()