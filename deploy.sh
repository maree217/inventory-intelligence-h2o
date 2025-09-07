#!/bin/bash
# Quick deployment script for Inventory Intelligence Dashboard

echo "🏪 Deploying Inventory Intelligence Dashboard..."

# Build and run with Docker Compose
echo "📦 Building Docker containers..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check H2O cluster health
if curl -f http://localhost:54321 > /dev/null 2>&1; then
    echo "✅ H2O cluster running at http://localhost:54321"
else
    echo "⚠️  H2O cluster not responding"
fi

# Check Streamlit app health
if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Dashboard running at http://localhost:8501"
    echo ""
    echo "🚀 Deployment complete!"
    echo "📊 Dashboard: http://localhost:8501"
    echo "🤖 H2O Cluster: http://localhost:54321"
else
    echo "❌ Dashboard not responding"
    echo "🔧 Checking logs..."
    docker-compose logs app
fi