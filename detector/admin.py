from django.contrib import admin
from .models import Transaction, FraudAlert, UserProfile


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'amount', 'timestamp', 'is_fraud', 'fraud_score', 'merchant_category']
    list_filter = ['is_fraud', 'merchant_category', 'is_foreign']
    search_fields = ['transaction_id', 'device_id']
    ordering = ['-timestamp']


@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'severity', 'is_reviewed', 'created_at']
    list_filter = ['severity', 'is_reviewed']
    ordering = ['-created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'total_transactions', 'fraud_count', 'risk_score', 'last_transaction_date']
    search_fields = ['user_id']
    ordering = ['-risk_score']
