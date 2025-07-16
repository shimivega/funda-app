#!/usr/bin/env bash
# Build script for Render deployment

# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

echo "Build completed successfully"