#!/bin/bash

echo "🚀 Welcome to the GringoOps Onboarding Script!"
echo "This script will help you set up your own private GringoOps instance."

# Check for .env file
if [ -f ".env" ]; then
    echo "✅ .env file already exists. Skipping creation."
else
    echo "📋 No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please fill it out with your own API keys and secrets."
fi

echo "🧹 Clearing out old memory and logs..."
rm -f memory/*.json
rm -f docs/dev_journal.json
rm -f docs/gringoops-dev-journal.md

echo "✅ GringoOps is now ready for a fresh start!"
echo "Next steps:"
echo "1. Fill out the .env file with your own API keys and secrets."
echo "2. Run 'firebase login' to authenticate with Firebase."
echo "3. Run 'firebase deploy' to deploy your new GringoOps instance."
