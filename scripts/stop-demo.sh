#!/bin/bash
# Stop demo to preserve Codespaces hours

echo "🛑 Stopping Inventory Intelligence Demo..."

# Stop Streamlit
echo "Stopping dashboard..."
pkill -f streamlit || echo "Dashboard already stopped"

# Stop H2O container
echo "Stopping H2O cluster..."
docker stop h2o-demo >/dev/null 2>&1 || echo "H2O already stopped"
docker rm h2o-demo >/dev/null 2>&1 || echo "H2O container already removed"

# Clean up resources
echo "Cleaning up resources..."
docker system prune -f >/dev/null 2>&1

echo "✅ Demo stopped successfully"
echo "💡 Codespaces will auto-suspend in 30 minutes"
echo "🔄 To restart demo: ./scripts/codespaces-demo.sh"