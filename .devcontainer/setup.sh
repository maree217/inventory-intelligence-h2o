#!/bin/bash
# GitHub Codespaces setup script for Inventory Intelligence
# Non-interactive setup to prevent container build failures

set -e  # Exit on any error

echo "🏪 Setting up Inventory Intelligence environment..."

# Ensure we're in the correct directory
cd /workspaces/inventory-intelligence-h2o

# Install Python dependencies with error handling
echo "📦 Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "✅ Python dependencies installed"

# Make scripts executable
echo "🔧 Setting up scripts..."
chmod +x deploy.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true

# Create directories
echo "📁 Creating directories..."
mkdir -p shared/data shared/models logs

# Test Python environment
echo "🐍 Testing Python environment..."
python3 -c "import sys; print(f'Python {sys.version}')"

# Check if requirements are properly installed
echo "📊 Checking core dependencies..."
python3 -c "import streamlit, pandas, numpy, plotly; print('✅ Core packages available')" 2>/dev/null || echo "⚠️  Some packages may need manual installation"

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "🚀 To start the demo:"
echo "   ./scripts/codespaces-demo.sh"
echo ""
echo "📊 Or start manually:"
echo "   streamlit run streamlit_app.py"
echo ""