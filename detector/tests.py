from django.test import TestCase
from .models import Transaction, FraudAlert, UserProfile


class TransactionModelTest(TestCase):
    def setUp(self):
        self.transaction = Transaction.objects.create(
            transaction_id='TEST001',
            amount=150.00,
            hour=14,
            minute=30,
            day=15,
            location_id=50,
            merchant_category='retail',
            device_id='device_10',
            is_foreign=False,
            num_transactions_1h=1,
            num_transactions_24h=5,
            avg_amount_30d=120.00,
            is_fraud=False,
            fraud_score=0.15
        )
    
    def test_transaction_creation(self):
        self.assertEqual(self.transaction.transaction_id, 'TEST001')
        self.assertEqual(float(self.transaction.amount), 150.00)
        self.assertFalse(self.transaction.is_fraud)
    
    def test_transaction_str(self):
        expected = 'TEST001 - $150.00 - LEGITIMATE'
        self.assertEqual(str(self.transaction), expected)


class FraudAlertModelTest(TestCase):
    def setUp(self):
        self.transaction = Transaction.objects.create(
            transaction_id='FRAUD001',
            amount=2500.00,
            hour=3,
            minute=15,
            day=20,
            location_id=450,
            merchant_category='cryptocurrency',
            device_id='device_500',
            is_foreign=True,
            num_transactions_1h=8,
            num_transactions_24h=20,
            avg_amount_30d=150.00,
            is_fraud=True,
            fraud_score=0.95
        )
        
        self.alert = FraudAlert.objects.create(
            transaction=self.transaction,
            severity='critical',
            message='High fraud probability detected'
        )
    
    def test_alert_creation(self):
        self.assertEqual(self.alert.severity, 'critical')
        self.assertFalse(self.alert.is_reviewed)
    
    def test_alert_str(self):
        expected = 'Alert: FRAUD001 - critical'
        self.assertEqual(str(self.alert), expected)
