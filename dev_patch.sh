#!/bin/bash
echo "🔧 Running GringoOps dev patch..."

echo "🧼 Running cleanup of .DS_Store files and compiled Python files..."
find . -name ".DS_Store" -type f -delete
find . -name "*.pyc" -type f -delete
find . -name "__pycache__" -type d -exec rm -r {} +

echo "📦 Ensuring essential requirements.txt includes all core packages..."
cat <<EOF > dev-requirements.txt
streamlit
openai
google-cloud-secret-manager
pydantic
protobuf
requests
EOF

echo "🧠 Linking memory.json and key configs..."
mkdir -p Agent/data
touch Agent/data/memory.json
echo '{}' > Agent/data/memory.json

echo "🔁 Creating patch logs directory..."
mkdir -p logs/patches

echo "✅ Dev patch complete. You can now commit and push to GitHub."