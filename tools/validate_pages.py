import os
from collections import Counter

pages_dir = "pages"
if not os.path.exists(pages_dir):
    print("No pages/ directory found.")
    exit(0)

slugs = [f.lower().replace(".py", "") for f in os.listdir(pages_dir) if f.endswith(".py")]
duplicates = [slug for slug, count in Counter(slugs).items() if count > 1]

if duplicates:
    print(f"❌ Duplicate page slugs detected: {duplicates}")
    exit(1)
else:
    print("✅ All Streamlit pages are unique.")
