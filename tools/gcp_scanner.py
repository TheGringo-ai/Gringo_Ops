import subprocess
import json

def get_service_accounts():
    """
    Gets a list of all service accounts in the current GCP project.
    """
    try:
        result = subprocess.run(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "list",
                "--format=json"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error getting service accounts: {e}")
        return []

def get_iam_policy(service_account_email):
    """
    Gets the IAM policy for a specific service account.
    """
    try:
        result = subprocess.run(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "get-iam-policy",
                service_account_email,
                "--format=json"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error getting IAM policy for {service_account_email}: {e}")
        return {}

def get_service_account_permissions(project_id):
    """Gets a list of service accounts and their permissions."""
    try:
        service_accounts = get_service_accounts()
        permissions = {}
        for account in service_accounts:
            email = account.get("email")
            if email:
                policy = get_iam_policy(email)
                permissions[email] = policy.get("bindings", [])
        return permissions
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def get_api_usage(project_id):
    """Gets a report of API usage for the project."""
    try:
        command = [
            "gcloud", "services", "operations", "list",
            "--project", project_id,
            "--format=json"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to get API usage: {e.stderr}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    project_id = "chatterfix-ui"  # Replace with your project ID
    accounts = get_service_accounts()
    for account in accounts:
        email = account.get("email")
        if email:
            print(f"\n--- Service Account: {email} ---")
            policy = get_iam_policy(email)
            print(json.dumps(policy, indent=2))
    
    gcp_memory = {
        "service_accounts": get_service_account_permissions(project_id),
        "api_usage": get_api_usage(project_id)
    }
    
    with open("memory/gcp_memory.json", "w") as f:
        json.dump(gcp_memory, f, indent=2)
