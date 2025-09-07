#!/bin/bash
# GitHub Codespaces optimized demo startup
# Robust error handling for client presentations

set -e  # Exit on error, but handle gracefully

echo "🏪 Starting Inventory Intelligence Demo..."

# Check if we're in Codespaces
if [[ -n "$CODESPACE_NAME" ]]; then
    echo "✅ Running in GitHub Codespaces: $CODESPACE_NAME"
    DASHBOARD_URL="https://$CODESPACE_NAME-8501.app.github.dev"
    H2O_URL="https://$CODESPACE_NAME-54321.app.github.dev"
else
    echo "🖥️  Running locally"
    DASHBOARD_URL="http://localhost:8501"
    H2O_URL="http://localhost:54321"
fi

# Function to check if service is running
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=${3:-30}
    
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

# Install H2O if not available (lightweight approach)
if ! python3 -c "import h2o" 2>/dev/null; then
    echo "📦 Installing H2O (this may take 2-3 minutes)..."
    pip install h2o==3.46.0.2 --quiet
fi

# Generate quick demo data
echo "📊 Generating demo data..."
python3 -c "
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Ensure data directory exists
os.makedirs('shared/data', exist_ok=True)

# Quick synthetic data for demo (reduced size for speed)
np.random.seed(42)
dates = pd.date_range('2023-01-01', '2023-06-30', freq='D')  # 6 months instead of 2 years
products = [f'PROD_{i:03d}' for i in range(1, 21)]  # 20 products instead of 50
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
print(f'✅ Generated {len(df)} demo records')
"

# Start Streamlit dashboard (no H2O cluster needed for basic demo)
echo "🚀 Starting Streamlit Dashboard..."
export DEMO_MODE=true
export PYTHONPATH=/workspaces/inventory-intelligence-h2o:$PYTHONPATH

# Start Streamlit in background
nohup streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.runOnSave=false \
    --server.fileWatcherType=none \
    --browser.gatherUsageStats=false \
    > logs/streamlit.log 2>&1 &

# Wait for dashboard to be ready
if check_service "$DASHBOARD_URL/_stcore/health" "Streamlit Dashboard" 20; then
    echo ""
    echo "🎉 INVENTORY INTELLIGENCE DEMO READY!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 DASHBOARD: $DASHBOARD_URL"
    if [[ -n "$CODESPACE_NAME" ]]; then
        echo "🔗 DIRECT LINK: $DASHBOARD_URL"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎯 DEMO FEATURES READY:"
    echo "• 📊 Executive KPI Dashboard"
    echo "• 🔮 AI-Powered Demand Forecasting" 
    echo "• 📈 Advanced Analytics & Trends"
    echo "• 📋 Data Management & Upload"
    echo ""
    echo "💡 Click the dashboard link above to start your presentation!"
    echo "🛑 Run './scripts/stop-demo.sh' when finished to save resources"
    echo ""
else
    echo "❌ Demo startup failed. Checking logs..."
    echo ""
    echo "🔍 Streamlit logs:"
    tail -20 logs/streamlit.log 2>/dev/null || echo "No log file found"
    echo ""
    echo "🩺 Troubleshooting:"
    echo "1. Check if port 8501 is available: netstat -tlnp | grep 8501"
    echo "2. Try manual start: streamlit run streamlit_app.py"
    echo "3. Check Python path: echo \$PYTHONPATH"
    exit 1
fi