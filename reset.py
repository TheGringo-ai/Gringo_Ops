import os
import shutil
import argparse

def factory_reset(force=False):
    """
    Resets the GringoOps instance to a clean, factory-sealed state.
    """
    print("🔥 Initiating GringoOps Factory Reset...")

    if not force:
        confirm = input("⚠️ This will delete all memory, logs, and custom configurations. Are you sure? (y/n): ")
        if confirm.lower() != 'y':
            print("Aborting factory reset.")
            return

    # Delete memory files
    print("🧹 Clearing memory...")
    if os.path.exists("memory"):
        shutil.rmtree("memory")
    os.makedirs("memory")

    # Delete logs
    print("🧹 Clearing logs...")
    if os.path.exists("docs/dev_journal.json"):
        os.remove("docs/dev_journal.json")
    if os.path.exists("docs/gringoops-dev-journal.md"):
        os.remove("docs/gringoops-dev-journal.md")

    # Reset .env file
    print("📋 Resetting .env file...")
    if os.path.exists(".env"):
        os.remove(".env")
    shutil.copy(".env.example", ".env")

    print("✅ GringoOps has been reset to a clean, factory-sealed state.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GringoOps Factory Reset Tool")
    parser.add_argument("--force", action="store_true", help="Force the factory reset without confirmation.")
    args = parser.parse_args()

    factory_reset(args.force)
