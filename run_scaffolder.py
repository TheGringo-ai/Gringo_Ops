import os
import sys
import argparse
sys.path.append('./lib')
from scaffold import scaffold

def main():
    parser = argparse.ArgumentParser(
        description="Generate a scaffold from a template into a target path"
    )
    parser.add_argument("project_path", help="Target path to create the project in")
    parser.add_argument("template_name", help="Name of the template to use")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be created")

    args = parser.parse_args()

    path = os.path.expanduser(args.project_path)
    template = args.template_name

    print(f"🚀 Scaffolding '{template}' into: {path}")

    try:
        created_files = scaffold(path, template, dry_run=args.dry_run)
        print(f"✅ Created {len(created_files)} items:")
        for f in created_files:
            print("   -", f)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
