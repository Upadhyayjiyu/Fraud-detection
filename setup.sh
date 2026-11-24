#!/bin/bash

# Fraud Detection System - Setup Script

echo "============================================================"
echo "Fraud Detection System - Automated Setup"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "============================================================"
echo "Step 1: Generate sample transaction data"
echo "============================================================"
python data_generator.py

echo ""
echo "============================================================"
echo "Step 2: Train ML models"
echo "============================================================"
python ml_engine.py --train

echo ""
echo "============================================================"
echo "Step 3: Set up Django database"
echo "============================================================"
python manage.py makemigrations
python manage.py migrate

echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "To start the server:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the server: python manage.py runserver"
echo "  3. Open your browser to: http://localhost:8000"
echo ""
echo "Optional - Create admin user:"
echo "  python manage.py createsuperuser"
echo ""
echo "============================================================"
