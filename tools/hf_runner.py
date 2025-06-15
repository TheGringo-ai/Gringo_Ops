import os
import logging
import tarfile
from huggingface_hub import HfApi, Repository

logging.basicConfig(level=logging.INFO)

def deploy_model(model_name, model_path=None):
    if model_path is None:
        model_path = os.path.join("models", model_name)
    print(f"🚀 Deploying Hugging Face model: {model_name} from {model_path}")
    logging.info(f"Starting deployment of model '{model_name}' from path '{model_path}'")

    api = HfApi()
    try:
        # Create repo if it does not exist
        api.create_repo(repo_id=model_name, exist_ok=True)
        # Upload folder contents to the repo
        api.upload_folder(
            folder_path=model_path,
            repo_id=model_name,
            repo_type="model",
            path_in_repo="",
            ignore_patterns=None,
        )
        print("✅ Deployment complete.")
        logging.info(f"Model '{model_name}' successfully deployed.")
        return f"Model '{model_name}' successfully deployed."
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        logging.error(f"Deployment failed for model '{model_name}': {e}")
        return f"Deployment failed: {e}"

def cli_deploy(model_name, model_path=None):
    if model_path is None:
        model_path = os.path.join("models", model_name)
    archive_name = f"{model_name}.tar.gz"
    print(f"📦 Archiving model directory {model_path} to {archive_name}")
    try:
        with tarfile.open(archive_name, "w:gz") as tar:
            tar.add(model_path, arcname=os.path.basename(model_path))
        print(f"📤 Archive created: {archive_name}")
        result = deploy_model(model_name, model_path)
        if result.startswith("Model"):
            os.remove(archive_name)
            print(f"🗑️ Removed archive {archive_name} after successful deployment.")
        return result
    except Exception as e:
        print(f"❌ Archiving or deployment failed: {e}")
        logging.error(f"Archiving or deployment failed for model '{model_name}': {e}")
        return f"Archiving or deployment failed: {e}"

def launch_upload_tab():
    import streamlit as st

    st.header("Upload and Deploy Hugging Face Model")
    st.write("Enter the name of your model below. Once a valid model name is provided, a usage snippet will be generated to help you import and use your model in your code.")

    model_name = st.text_input("Model Name", "")

    if model_name.strip():
        if st.button("🛠 Create Dummy Model"):
            dummy_model_dir = os.path.join("models", model_name.strip())
            try:
                os.makedirs(dummy_model_dir, exist_ok=True)
                config_path = os.path.join(dummy_model_dir, "config.json")
                readme_path = os.path.join(dummy_model_dir, "README.md")
                model_bin_path = os.path.join(dummy_model_dir, "pytorch_model.bin")

                with open(config_path, "w") as f:
                    f.write('{"architectures": ["DummyModel"], "model_type": "dummy"}\n')

                with open(readme_path, "w") as f:
                    f.write(f"# Dummy model {model_name.strip()}\nThis is a dummy model directory for testing purposes.\n")

                with open(model_bin_path, "wb") as f:
                    f.write(b"\x00\x01\x02\x03")  # dummy binary content

                st.success(f"Dummy model created at {dummy_model_dir}")
            except Exception as e:
                st.error(f"Failed to create dummy model: {e}")

        usage_code = f"""from transformers import AutoModel, AutoTokenizer

model_name = "{model_name.strip()}"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Now you can use tokenizer and model for inference
"""
        st.code(usage_code, language="python")
    else:
        st.info("Please enter a model name above to see the usage snippet.")

    model_path = st.text_area("Model Path (optional)", "")

    if st.button("Deploy Model"):
        if not model_name.strip():
            st.error("Please enter a model name.")
        else:
            path = model_path.strip() if model_path.strip() else None
            result = deploy_model(model_name.strip(), path)
            if result.startswith("Model"):
                st.success(result)
            else:
                st.error(result)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python hf_runner.py <model_name> [optional_model_path]")
        sys.exit(1)
    if sys.argv[1] == "--cli":
        if len(sys.argv) < 3:
            print("Usage: python hf_runner.py --cli <model_name> [optional_model_path]")
            sys.exit(1)
        model_name = sys.argv[2]
        model_path = sys.argv[3] if len(sys.argv) > 3 else None
        cli_deploy(model_name, model_path)
    else:
        model_name = sys.argv[1]
        model_path = sys.argv[2] if len(sys.argv) > 2 else None
        deploy_model(model_name, model_path)