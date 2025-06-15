import sys
import os
sys.path.append('./lib')
from scaffold import scaffold

if len(sys.argv) != 3:
    print("Usage: python3 run_scaffolder.py <project_path> <template_name>")
    sys.exit(1)

path = os.path.expanduser(sys.argv[1])
template = sys.argv[2]
created_files = scaffold(path, template)

print(f"✅ Created {len(created_files)} items:")
for f in created_files:
    print("   -", f)
