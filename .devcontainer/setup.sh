#!/bin/bash
# GitHub Codespaces setup script for Inventory Intelligence

echo "🏪 Setting up Inventory Intelligence environment..."

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install additional tools for demos
pip install jupyter notebook ipywidgets

# Make scripts executable
chmod +x deploy.sh
chmod +x scripts/*.sh

# Create directories
mkdir -p shared/data shared/models logs

# Generate sample data if H2O is available
echo "📊 Preparing synthetic data generation..."
python -c "import h2o; print('H2O available')" 2>/dev/null || echo "⚠️ H2O will be installed on first run"

# Pre-warm Docker if needed
docker --version || echo "Docker not available in this environment"

echo "✅ Environment setup complete!"
echo "🚀 Run './deploy.sh' to start the application"
echo "📊 Dashboard will be available on port 8501"
echo "🤖 H2O cluster will be available on port 54321"