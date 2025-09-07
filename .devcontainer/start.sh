#!/bin/bash
# Auto-start script for GitHub Codespaces

echo "🚀 Starting Inventory Intelligence services..."

# Check if H2O cluster should auto-start (for demos)
if [ "$AUTO_START" = "true" ]; then
    echo "🤖 Auto-starting H2O cluster..."
    docker-compose up -d h2o
    
    # Wait for H2O to be ready
    echo "⏳ Waiting for H2O cluster..."
    for i in {1..30}; do
        if curl -s http://localhost:54321 >/dev/null; then
            echo "✅ H2O cluster ready!"
            break
        fi
        sleep 2
    done
    
    echo "📊 Auto-starting dashboard..."
    streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 &
    
    echo "🎉 Services started!"
    echo "📊 Dashboard: https://$CODESPACE_NAME-8501.app.github.dev"
    echo "🤖 H2O: https://$CODESPACE_NAME-54321.app.github.dev"
else
    echo "💡 Services not auto-started. Run './deploy.sh' when ready."
fi