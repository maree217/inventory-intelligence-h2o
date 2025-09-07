#!/bin/bash
# GitHub Codespaces optimized demo startup
# Robust error handling for client presentations

# Disable strict error exit for better error handling
set +e

echo "🏪 Starting Inventory Intelligence Demo..."

# Check if we're in Codespaces
if [[ -n "$CODESPACE_NAME" ]]; then
    echo "✅ Running in GitHub Codespaces: $CODESPACE_NAME"
    DASHBOARD_URL="https://$CODESPACE_NAME-8501.app.github.dev"
    H2O_URL="https://$CODESPACE_NAME-54321.app.github.dev"
    PIP_CMD="pip"
    PYTHON_CMD="python3"
else
    echo "🖥️  Running locally"
    DASHBOARD_URL="http://localhost:8501"
    H2O_URL="http://localhost:54321"
    
    # Try to find pip command (virtual env aware)
    if command -v ../venv/bin/pip >/dev/null 2>&1; then
        PIP_CMD="../venv/bin/pip"
        PYTHON_CMD="../venv/bin/python"
        echo "📦 Using virtual environment"
    elif command -v pip3 >/dev/null 2>&1; then
        PIP_CMD="pip3"
        PYTHON_CMD="python3"
    elif command -v pip >/dev/null 2>&1; then
        PIP_CMD="pip"
        PYTHON_CMD="python3"
    else
        echo "❌ No pip command found. Please install Python and pip."
        exit 1
    fi
fi

echo "🔧 Using Python: $PYTHON_CMD"
echo "🔧 Using pip: $PIP_CMD"

# Function to check if service is running
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=${3:-20}
    
    echo "⏳ Waiting for $service_name..."
    for i in $(seq 1 $max_attempts); do
        if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
            echo "✅ $service_name is ready at $url"
            return 0
        fi
        sleep 2
        echo "   ... attempt $i/$max_attempts"
    done
    echo "⚠️  $service_name not responding at $url"
    return 1
}

# Check and install required packages
echo "📦 Checking required packages..."

# Check if packages are available
if ! $PYTHON_CMD -c "import streamlit, pandas, numpy, plotly" 2>/dev/null; then
    echo "📦 Installing required packages..."
    $PIP_CMD install streamlit pandas numpy plotly --quiet
fi

# Install H2O if not available (optional for basic demo)
if ! $PYTHON_CMD -c "import h2o" 2>/dev/null; then
    echo "📦 H2O not found - installing (may take 2-3 minutes)..."
    $PIP_CMD install h2o==3.46.0.2 --quiet || echo "⚠️ H2O installation failed - demo will run without H2O AutoML"
fi

# Create directories
mkdir -p shared/data logs

# Generate quick demo data
echo "📊 Generating demo data..."
$PYTHON_CMD -c "
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Ensure data directory exists
os.makedirs('shared/data', exist_ok=True)

# Quick synthetic data for demo (reduced size for speed)
np.random.seed(42)
dates = pd.date_range('2023-01-01', '2023-06-30', freq='D')
products = [f'PROD_{i:03d}' for i in range(1, 21)]
categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home']

data = []
for product in products:
    for date in dates[:50]:  # Only 50 days per product for speed
        base_demand = np.random.uniform(5, 50)
        seasonal = 1 + 0.3 * np.sin(2 * np.pi * date.dayofyear / 365)
        weekend = 1.2 if date.weekday() >= 5 else 1.0
        demand = max(1, int(base_demand * seasonal * weekend * np.random.uniform(0.8, 1.2)))
        
        data.append({
            'date': date,
            'product_id': product,
            'category': np.random.choice(categories),
            'quantity_sold': demand,
            'price': round(np.random.uniform(10, 200), 2),
            'stock_level': np.random.randint(20, 300),
            'day_of_week': date.weekday(),
            'month': date.month,
            'is_weekend': int(date.weekday() >= 5),
            'is_holiday_season': int(date.month in [11, 12]),
            'on_promotion': int(np.random.random() < 0.1),
            'quantity_sold_7d_avg': round(demand * np.random.uniform(0.9, 1.1), 2),
            'quantity_sold_30d_avg': round(demand * np.random.uniform(0.85, 1.15), 2)
        })

df = pd.DataFrame(data)
df.to_csv('shared/data/demo_data.csv', index=False)
print(f'Generated {len(df)} demo records for presentation')
"

if [[ $? -eq 0 ]]; then
    echo "✅ Demo data generated successfully"
else
    echo "❌ Failed to generate demo data"
    exit 1
fi

# Start Streamlit dashboard
echo "🚀 Starting Streamlit Dashboard..."
export DEMO_MODE=true

# Kill any existing streamlit processes
pkill -f streamlit >/dev/null 2>&1 || true

# Set Python path
if [[ -n "$CODESPACE_NAME" ]]; then
    export PYTHONPATH=/workspaces/inventory-intelligence-h2o:$PYTHONPATH
else
    export PYTHONPATH=$(pwd):$PYTHONPATH
fi

# Start Streamlit with explicit command
if [[ -n "$CODESPACE_NAME" ]]; then
    # Codespace environment
    nohup $PYTHON_CMD -m streamlit run streamlit_app.py \
        --server.port=8501 \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --server.runOnSave=false \
        --server.fileWatcherType=none \
        --browser.gatherUsageStats=false \
        > logs/streamlit.log 2>&1 &
else
    # Local environment
    nohup $PYTHON_CMD -m streamlit run streamlit_app.py \
        --server.port=8501 \
        --server.address=localhost \
        --server.headless=true \
        > logs/streamlit.log 2>&1 &
fi

echo "🔄 Streamlit starting in background..."

# Wait for dashboard to be ready
sleep 5  # Give it time to start

if check_service "$DASHBOARD_URL/_stcore/health" "Streamlit Dashboard" 15; then
    echo ""
    echo "🎉 INVENTORY INTELLIGENCE DEMO READY!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 DASHBOARD: $DASHBOARD_URL"
    if [[ -n "$CODESPACE_NAME" ]]; then
        echo "🌐 PUBLIC URL: $DASHBOARD_URL"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎯 DEMO FEATURES READY:"
    echo "• 📊 Executive KPI Dashboard with ROI metrics"
    echo "• 🔮 AI-Powered Demand Forecasting simulation" 
    echo "• 📈 Advanced Analytics & Business Intelligence"
    echo "• 📋 Data Management & CSV Upload capabilities"
    echo ""
    echo "💡 Click the dashboard link above to start your client presentation!"
    echo "🛑 Run './scripts/stop-demo.sh' when finished to save resources"
    echo ""
else
    echo "❌ Demo startup failed. Troubleshooting information:"
    echo ""
    echo "🔍 Streamlit logs:"
    if [[ -f logs/streamlit.log ]]; then
        echo "Last 10 lines of streamlit.log:"
        tail -10 logs/streamlit.log
    else
        echo "No log file found at logs/streamlit.log"
    fi
    echo ""
    echo "🩺 Manual troubleshooting steps:"
    echo "1. Check Python: $PYTHON_CMD --version"
    echo "2. Check packages: $PYTHON_CMD -c 'import streamlit, pandas, numpy, plotly'"
    echo "3. Test manually: $PYTHON_CMD -m streamlit run streamlit_app.py"
    echo "4. Check port: netstat -tlnp | grep 8501"
    echo "5. Check process: ps aux | grep streamlit"
    exit 1
fi