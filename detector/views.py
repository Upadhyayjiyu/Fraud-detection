"""
Views for fraud detection system
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
import json
import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path to import ml_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .models import Transaction, FraudAlert, UserProfile


def dashboard(request):
    """Main dashboard view"""
    # Get statistics
    total_transactions = Transaction.objects.count()
    fraud_transactions = Transaction.objects.filter(is_fraud=True).count()
    legitimate_transactions = total_transactions - fraud_transactions
    
    # Calculate fraud rate
    fraud_rate = (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0
    
    # Get recent transactions
    recent_transactions = Transaction.objects.all()[:10]
    
    # Get recent alerts
    recent_alerts = FraudAlert.objects.filter(is_reviewed=False)[:5]
    
    # Get fraud by category
    fraud_by_category = Transaction.objects.filter(is_fraud=True).values(
        'merchant_category'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    context = {
        'total_transactions': total_transactions,
        'fraud_transactions': fraud_transactions,
        'legitimate_transactions': legitimate_transactions,
        'fraud_rate': round(fraud_rate, 2),
        'recent_transactions': recent_transactions,
        'recent_alerts': recent_alerts,
        'fraud_by_category': fraud_by_category,
    }
    
    return render(request, 'dashboard.html', context)


def monitoring(request):
    """Real-time transaction monitoring view"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    
    # Build query
    transactions = Transaction.objects.all()
    
    if status_filter == 'fraud':
        transactions = transactions.filter(is_fraud=True)
    elif status_filter == 'legitimate':
        transactions = transactions.filter(is_fraud=False)
    
    # Paginate
    transactions = transactions[:50]
    
    context = {
        'transactions': transactions,
        'status_filter': status_filter,
    }
    
    return render(request, 'monitoring.html', context)


def analytics(request):
    """Analytics and model performance view"""
    # Load models exist check
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    models_trained = os.path.exists(os.path.join(models_dir, 'random_forest.pkl'))
    
    # Get transaction statistics
    total_count = Transaction.objects.count()
    fraud_count = Transaction.objects.filter(is_fraud=True).count()
    
    # Hourly fraud distribution
    hourly_fraud = []
    for hour in range(24):
        count = Transaction.objects.filter(is_fraud=True, hour=hour).count()
        hourly_fraud.append({'hour': hour, 'count': count})
    
    # Fraud by amount range
    amount_ranges = [
        (0, 100, '$0-$100'),
        (100, 500, '$100-$500'),
        (500, 1000, '$500-$1000'),
        (1000, 5000, '$1000-$5000'),
        (5000, 10000, '$5000+'),
    ]
    
    fraud_by_amount = []
    for min_amt, max_amt, label in amount_ranges:
        if max_amt == 10000:
            count = Transaction.objects.filter(is_fraud=True, amount__gte=min_amt).count()
        else:
            count = Transaction.objects.filter(is_fraud=True, amount__gte=min_amt, amount__lt=max_amt).count()
        fraud_by_amount.append({'label': label, 'count': count})
    
    context = {
        'models_trained': models_trained,
        'total_count': total_count,
        'fraud_count': fraud_count,
        'hourly_fraud': json.dumps(hourly_fraud),
        'fraud_by_amount': json.dumps(fraud_by_amount),
    }
    
    return render(request, 'analytics.html', context)


@csrf_exempt
def predict_transaction(request):
    """API endpoint for fraud prediction"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=400)
    
    try:
        # Parse request data
        data = json.loads(request.body)
        
        # Create transaction record
        transaction = Transaction.objects.create(
            transaction_id=data.get('transaction_id', f'TXN{Transaction.objects.count():06d}'),
            amount=data['amount'],
            hour=data.get('hour', timezone.now().hour),
            minute=data.get('minute', timezone.now().minute),
            day=data.get('day', timezone.now().day),
            location_id=data.get('location_id', 0),
            merchant_category=data.get('merchant_category', 'unknown'),
            device_id=data.get('device_id', 'unknown'),
            is_foreign=data.get('is_foreign', False),
            num_transactions_1h=data.get('num_transactions_1h', 1),
            num_transactions_24h=data.get('num_transactions_24h', 5),
            avg_amount_30d=data.get('avg_amount_30d', 100),
        )
        
        # Try to load ML model and predict
        try:
            from ml_engine import FraudDetectionEngine
            
            engine = FraudDetectionEngine()
            engine.load_models('models')
            
            # Create DataFrame for prediction
            trans_df = pd.DataFrame([{
                'amount': float(transaction.amount),
                'hour': transaction.hour,
                'minute': transaction.minute,
                'day': transaction.day,
                'location_id': transaction.location_id,
                'merchant_category': transaction.merchant_category,
                'device_id': transaction.device_id,
                'is_foreign': 1 if transaction.is_foreign else 0,
                'num_transactions_1h': transaction.num_transactions_1h,
                'num_transactions_24h': transaction.num_transactions_24h,
                'avg_amount_30d': float(transaction.avg_amount_30d),
            }])
            
            # Predict
            result = engine.predict(trans_df, model_name='random_forest')
            
            # Update transaction
            transaction.is_fraud = bool(result['is_fraud'][0])
            transaction.fraud_score = float(result['fraud_scores'][0])
            transaction.save()
            
            # Create alert if fraud detected
            if transaction.is_fraud:
                severity = 'critical' if transaction.fraud_score > 0.9 else 'high' if transaction.fraud_score > 0.7 else 'medium'
                FraudAlert.objects.create(
                    transaction=transaction,
                    severity=severity,
                    message=f"Suspicious transaction detected: ${transaction.amount} with {transaction.fraud_score*100:.1f}% fraud probability"
                )
            
        except Exception as e:
            # Fallback: simple rule-based detection
            transaction.is_fraud = float(transaction.amount) > 1000 or transaction.hour in [0, 1, 2, 3]
            transaction.fraud_score = 0.5
            transaction.save()
        
        return JsonResponse({
            'success': True,
            'transaction_id': transaction.transaction_id,
            'is_fraud': transaction.is_fraud,
            'fraud_score': transaction.fraud_score,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_statistics(request):
    """API endpoint for dashboard statistics"""
    # Last 24 hours stats
    last_24h = timezone.now() - timedelta(hours=24)
    
    recent_transactions = Transaction.objects.filter(timestamp__gte=last_24h)
    
    stats = {
        'total_24h': recent_transactions.count(),
        'fraud_24h': recent_transactions.filter(is_fraud=True).count(),
        'avg_amount_24h': recent_transactions.aggregate(Avg('amount'))['amount__avg'] or 0,
        'pending_alerts': FraudAlert.objects.filter(is_reviewed=False).count(),
    }
    
    return JsonResponse(stats)


def load_sample_data(request):
    """Load sample transaction data into database"""
    try:
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'transaction_data.csv')
        
        if not os.path.exists(csv_path):
            return JsonResponse({'error': 'transaction_data.csv not found. Run data_generator.py first'}, status=400)
        
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Clear existing data
        Transaction.objects.all().delete()
        FraudAlert.objects.all().delete()
        
        # Import transactions
        transactions_to_create = []
        for _, row in df.head(1000).iterrows():  # Load first 1000 for demo
            transactions_to_create.append(Transaction(
                transaction_id=row['transaction_id'],
                amount=row['amount'],
                timestamp=pd.to_datetime(row['timestamp']),
                hour=row['hour'],
                minute=row['minute'],
                day=row['day'],
                location_id=row['location_id'],
                merchant_category=row['merchant_category'],
                device_id=row['device_id'],
                is_foreign=bool(row['is_foreign']),
                num_transactions_1h=row['num_transactions_1h'],
                num_transactions_24h=row['num_transactions_24h'],
                avg_amount_30d=row['avg_amount_30d'],
                is_fraud=bool(row['is_fraud']),
                fraud_score=float(row['is_fraud']),
            ))
        
        Transaction.objects.bulk_create(transactions_to_create)
        
        # Create alerts for fraud transactions
        fraud_transactions = Transaction.objects.filter(is_fraud=True)[:50]
        alerts_to_create = []
        for trans in fraud_transactions:
            alerts_to_create.append(FraudAlert(
                transaction=trans,
                severity='high',
                message=f"Fraudulent transaction detected: ${trans.amount}"
            ))
        
        FraudAlert.objects.bulk_create(alerts_to_create)
        
        return JsonResponse({
            'success': True,
            'transactions_loaded': len(transactions_to_create),
            'alerts_created': len(alerts_to_create)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
