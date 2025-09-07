#!/bin/bash
# Diagnostic script for GitHub Codespaces deployment issues

echo "🔍 GITHUB CODESPACES DIAGNOSTIC REPORT"
echo "======================================="
echo ""

# Check environment
echo "🌐 ENVIRONMENT INFORMATION:"
echo "CODESPACE_NAME: ${CODESPACE_NAME:-'Not set (running locally)'}"
echo "USER: $(whoami)"
echo "PWD: $(pwd)"
echo "HOME: $HOME"
echo ""

# Check Python
echo "🐍 PYTHON INFORMATION:"
echo "Python version: $(python3 --version 2>/dev/null || echo 'python3 not found')"
echo "Python location: $(which python3 2>/dev/null || echo 'python3 not in PATH')"
echo "Pip version: $(pip --version 2>/dev/null || echo 'pip not found')"
echo "Pip3 version: $(pip3 --version 2>/dev/null || echo 'pip3 not found')"
echo ""

# Check if we can import required packages
echo "📦 PACKAGE AVAILABILITY:"
python3 -c "
import sys
packages = ['streamlit', 'pandas', 'numpy', 'plotly', 'h2o']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg} - not installed')
" 2>/dev/null || echo "❌ Python3 execution failed"
echo ""

# Check file structure
echo "📁 FILE STRUCTURE:"
echo "Current directory contents:"
ls -la
echo ""
echo "Scripts directory:"
ls -la scripts/ 2>/dev/null || echo "❌ scripts/ directory not found"
echo ""
echo "Shared directory:"
ls -la shared/ 2>/dev/null || echo "❌ shared/ directory not found"
echo ""

# Check if streamlit app exists and can be parsed
echo "🔧 STREAMLIT APP CHECK:"
if [[ -f "streamlit_app.py" ]]; then
    echo "✅ streamlit_app.py exists"
    # Try to parse Python syntax
    python3 -m py_compile streamlit_app.py 2>/dev/null && echo "✅ streamlit_app.py syntax is valid" || echo "❌ streamlit_app.py has syntax errors"
else
    echo "❌ streamlit_app.py not found"
fi
echo ""

# Check network and ports
echo "🌐 NETWORK INFORMATION:"
if [[ -n "$CODESPACE_NAME" ]]; then
    echo "Expected dashboard URL: https://$CODESPACE_NAME-8501.app.github.dev"
    echo "Expected H2O URL: https://$CODESPACE_NAME-54321.app.github.dev"
else
    echo "Local URLs:"
    echo "Dashboard: http://localhost:8501"
    echo "H2O: http://localhost:54321"
fi
echo ""

# Check if anything is running on port 8501
echo "🔍 PORT STATUS:"
if command -v netstat >/dev/null 2>&1; then
    echo "Port 8501 status:"
    netstat -tlnp 2>/dev/null | grep 8501 || echo "Nothing running on port 8501"
else
    echo "netstat not available"
fi
echo ""

# Check running processes
echo "🏃 RUNNING PROCESSES:"
if ps aux | grep -i streamlit | grep -v grep; then
    echo "Streamlit processes found above"
else
    echo "No Streamlit processes running"
fi
echo ""

# Check logs
echo "📋 LOG FILES:"
if [[ -f "logs/streamlit.log" ]]; then
    echo "✅ logs/streamlit.log exists"
    echo "Last 5 lines:"
    tail -5 logs/streamlit.log
else
    echo "❌ logs/streamlit.log not found"
fi
echo ""

# Try a simple manual test
echo "🧪 MANUAL TEST:"
echo "Attempting to start Streamlit manually for 10 seconds..."

# Create a minimal test app
cat > test_app.py << 'EOF'
import streamlit as st
st.title("🏪 Test App")
st.write("If you can see this, Streamlit is working!")
st.success("✅ Basic Streamlit functionality confirmed")
EOF

# Try to start it briefly
timeout 10s python3 -m streamlit run test_app.py --server.headless=true --server.port=8502 > test_output.log 2>&1 &
TEST_PID=$!
sleep 3

# Check if it started
if curl -s http://localhost:8502/_stcore/health >/dev/null 2>&1; then
    echo "✅ Manual Streamlit test successful on port 8502"
else
    echo "❌ Manual Streamlit test failed"
    echo "Test output:"
    cat test_output.log 2>/dev/null || echo "No test output available"
fi

# Clean up
kill $TEST_PID 2>/dev/null || true
rm -f test_app.py test_output.log

echo ""
echo "🎯 RECOMMENDED ACTIONS:"
echo ""

# Provide specific recommendations
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Install Python 3"
fi

if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Install Streamlit: pip install streamlit"
fi

if ! python3 -c "import pandas, numpy, plotly" 2>/dev/null; then
    echo "❌ Install data packages: pip install pandas numpy plotly"
fi

if [[ ! -f "streamlit_app.py" ]]; then
    echo "❌ Ensure you're in the correct directory with streamlit_app.py"
fi

if [[ -n "$CODESPACE_NAME" ]]; then
    echo "✅ Try running: ./scripts/codespaces-demo.sh"
    echo "✅ Or manual start: python3 -m streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"
else
    echo "✅ Try running: streamlit run streamlit_app.py"
fi

echo ""
echo "📞 If issues persist, please share this diagnostic report for further troubleshooting."