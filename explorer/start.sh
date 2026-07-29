#!/bin/bash
# MobiusCoin Explorer - Quick Start Script

echo "============================================================"
echo "🚀 Starting MobiusCoin Blockchain Explorer"
echo "============================================================"
echo ""

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install --break-system-packages -r requirements.txt
    echo ""
fi

# Start the explorer
echo "🌐 Starting web server..."
echo "   Open http://localhost:5000 in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

python3 app.py
