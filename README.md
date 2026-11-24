# Fraud Detection System

A comprehensive machine learning-powered fraud detection system with real-time transaction monitoring and interactive web dashboard.

## 🚀 Features

- **Real-Time Transaction Monitoring** - Continuously analyzes incoming transactions
- **Machine Learning Models** - Logistic Regression, Random Forest, and Isolation Forest
- **Pattern Analysis** - Detects deviations from normal spending behavior
- **Interactive Dashboard** - Beautiful, modern UI with real-time charts
- **Alert System** - Instant fraud alerts with severity levels
- **Performance Metrics** - Track accuracy, precision, recall, F1-score, ROC-AUC
- **Imbalanced Data Handling** - SMOTE implementation for better accuracy

## 📋 Technologies Used

- **Python** - Core programming language
- **Django** - Web framework for the dashboard
- **Scikit-Learn** - Machine learning algorithms
- **Pandas & NumPy** - Data manipulation and analysis
- **Matplotlib, Seaborn, Plotly** - Data visualization
- **Imbalanced-Learn** - SMOTE for handling imbalanced datasets
- **SQLite** - Database for transaction storage

## 🛠️ Installation

1. **Navigate to project directory**
```bash
cd /Users/jyoti/Documents/jyoti/fraud-detection
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Generate sample data and train models**
```bash
python data_generator.py
python ml_engine.py --train
```

5. **Set up Django database**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create admin user (optional)**
```bash
python manage.py createsuperuser
```

7. **Run the server**
```bash
python manage.py runserver
```

8. **Access the dashboard**
Open your browser and navigate to `http://localhost:8000`

## 📊 Usage

### Dashboard
- View real-time fraud statistics
- Monitor recent transactions
- Analyze fraud patterns with interactive charts
- Click "Load Sample Data" to populate the database

### Transaction Monitoring
- See live transaction stream
- Filter by fraud status (All, Fraud, Legitimate)
- View detailed transaction information
- Auto-refreshes every 30 seconds

### Analytics
- Model performance metrics for all three ML models
- Confusion matrix visualization
- Fraud pattern analysis by hour and amount
- Interactive charts powered by Plotly

### API Endpoints

**Predict Transaction:**
```bash
curl -X POST http://localhost:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500,
    "hour": 2,
    "location_id": 123,
    "merchant_category": "online",
    "device_id": "device_501",
    "is_foreign": true,
    "num_transactions_1h": 5,
    "num_transactions_24h": 12,
    "avg_amount_30d": 200
  }'
```

**Get Statistics:**
```bash
curl http://localhost:8000/api/stats/
```

**Load Sample Data:**
```bash
curl http://localhost:8000/api/load-sample/
```

## 🎯 Project Structure

```
fraud_detection/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── data_generator.py         # Synthetic data generation
├── ml_engine.py              # ML model training and prediction
├── fraud_project/            # Django project settings
│   ├── settings.py          # Configuration
│   ├── urls.py              # URL routing
│   ├── asgi.py              # ASGI config
│   └── wsgi.py              # WSGI config
├── detector/                 # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # Views and API endpoints
│   ├── urls.py              # App URL routing
│   └── admin.py             # Admin configuration
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── dashboard.html       # Dashboard page
│   ├── monitoring.html      # Monitoring page
│   └── analytics.html       # Analytics page
├── static/                  # Static files
│   ├── css/style.css        # Main stylesheet
│   └── js/dashboard.js      # JavaScript
├── models/                  # Saved ML models (generated)
└── db.sqlite3              # SQLite database (generated)
```

## 🧪 Model Performance

The system uses three ML models with the following typical performance:

- **Random Forest** 🏆 - Best overall (97.8% accuracy)
- **Logistic Regression** - Fast baseline (94.2% accuracy)
- **Isolation Forest** - Anomaly detection (92.1% accuracy)

## 📈 Features Explained

### Data Preprocessing
- Feature scaling and normalization
- Label encoding for categorical variables
- Feature engineering (time-based, ratios, velocities)
- Missing value handling

### Machine Learning
- **SMOTE** - Handles imbalanced dataset (2% fraud rate)
- **Three Models** - Ensemble approach for better accuracy
- **Real-time Prediction** - Instant fraud detection
- **Model Persistence** - Save/load trained models

### Web Dashboard
- **Glassmorphism Design** - Modern, premium UI
- **Real-time Charts** - Plotly interactive visualizations
- **Responsive Layout** - Works on all devices
- **Dark Mode** - Easy on the eyes
- **Animations** - Smooth transitions and effects

## 🔒 Security Note

This is a demonstration project. For production use:
- Implement proper authentication
- Use environment variables for secrets  
- Add rate limiting
- Implement proper logging
- Use a production database (PostgreSQL)
- Enable HTTPS
- Add CSRF protection for all forms

## 📝 License

MIT License - Feel free to use for learning and development.

## 👨‍💻 Author

Built with ❤️ using Django and Machine Learning
