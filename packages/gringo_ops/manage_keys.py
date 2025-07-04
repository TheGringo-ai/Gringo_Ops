import subprocess
import argparse

def add_key(service, value):
    subprocess.run([
        "security", "add-generic-password",
        "-a", "fredtaylor",
        "-s", service,
        "-w", value,
        "-U"
    ])
    print(f"✅ Key '{service}' added or updated.")

def delete_key(service):
    subprocess.run([
        "security", "delete-generic-password",
        "-s", service
    ])
    print(f"🗑️ Key '{service}' deleted.")

def read_key(service):
    result = subprocess.run([
        "security", "find-generic-password",
        "-s", service,
        "-w"
    ], capture_output=True, text=True)
    print(f"{service}: {result.stdout.strip()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", help="Add or update a key")
    parser.add_argument("--delete", help="Delete a key")
    parser.add_argument("--read", help="Read a key")

    args = parser.parse_args()

    if args.add:
        value = input(f"🔐 Enter value for '{args.add}': ")
        add_key(args.add, value)
    elif args.delete:
        delete_key(args.delete)
    elif args.read:
        read_key(args.read)
