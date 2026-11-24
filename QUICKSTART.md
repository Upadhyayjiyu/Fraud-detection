# Quick Start Guide

## 🚀 Quick Installation

Run the automated setup script:

```bash
cd /Users/jyoti/Documents/jyoti/food-mgmt/fraud_detection
bash setup.sh
```

This will:
- Create a virtual environment  
- Install all dependencies
- Generate sample transaction data
- Train ML models
- Set up the database

## 🎯 Manual Installation (if setup.sh fails)

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate data
python data_generator.py

# 4. Train models
python ml_engine.py --train

# 5. Setup database
python manage.py makemigrations
python manage.py migrate

# 6. Run server
python manage.py runserver
```

## 📱 Access the Application

Open your browser to: **http://localhost:8000**

### Pages:
- **Dashboard** - http://localhost:8000/
- **Monitoring** - http://localhost:8000/monitoring/
- **Analytics** - http://localhost:8000/analytics/

## 💡 Quick Actions

**Load Sample Data** (if database is empty):
- Click the "Load Sample Data" link on the dashboard
- Or visit: http://localhost:8000/api/load-sample/

**Test Fraud Prediction API**:
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 2500,
    "hour": 3,
    "location_id": 450,
    "merchant_category": "cryptocurrency",
    "device_id": "device_999",
    "is_foreign": true,
    "num_transactions_1h": 8,
    "num_transactions_24h": 20,
    "avg_amount_30d": 150
  }'
```

## 🛑 Troubleshooting

**Virtual environment not activating?**
```bash
source venv/bin/activate
```

**Dependencies installation failed?**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Database errors?**
```bash
rm db.sqlite3
python manage.py migrate
```

**Models not loading?**
```bash
python ml_engine.py --train
```

## 📊 Features to Try

1. **Dashboard** - View overall fraud statistics and recent transactions
2. **Monitoring** - Filter transactions by status (All/Fraud/Legitimate)
3. **Analytics** - Explore fraud patterns with interactive Plotly charts
4. **API** - Test real-time fraud prediction endpoint

Enjoy your Fraud Detection System! 🎉
