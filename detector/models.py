"""
Database models for fraud detection system
"""
from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    """Store transaction details and fraud predictions"""
    
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    hour = models.IntegerField()
    minute = models.IntegerField()
    day = models.IntegerField()
    location_id = models.IntegerField()
    merchant_category = models.CharField(max_length=50)
    device_id = models.CharField(max_length=100)
    is_foreign = models.BooleanField(default=False)
    num_transactions_1h = models.IntegerField(default=0)
    num_transactions_24h = models.IntegerField(default=0)
    avg_amount_30d = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Prediction results
    is_fraud = models.BooleanField(default=False)
    fraud_score = models.FloatField(default=0.0)
    model_used = models.CharField(max_length=50, default='random_forest')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.transaction_id} - ${self.amount} - {'FRAUD' if self.is_fraud else 'LEGITIMATE'}"


class FraudAlert(models.Model):
    """Store fraud alerts"""
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='alerts')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    message = models.TextField()
    is_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Alert: {self.transaction.transaction_id} - {self.severity}"


class UserProfile(models.Model):
    """Store user behavior patterns"""
    
    user_id = models.CharField(max_length=100, unique=True)
    avg_transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_transactions = models.IntegerField(default=0)
    fraud_count = models.IntegerField(default=0)
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    risk_score = models.FloatField(default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"User {self.user_id} - Risk: {self.risk_score:.2f}"
