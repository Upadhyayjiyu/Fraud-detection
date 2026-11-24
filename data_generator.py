"""
Data Generator for Fraud Detection System
Generates synthetic transaction data with realistic fraud patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class TransactionDataGenerator:
    def __init__(self, n_transactions=10000, fraud_rate=0.02):
        """
        Initialize the data generator
        
        Args:
            n_transactions: Total number of transactions to generate
            fraud_rate: Percentage of fraudulent transactions
        """
        self.n_transactions = n_transactions
        self.fraud_rate = fraud_rate
        self.n_fraud = int(n_transactions * fraud_rate)
        self.n_legitimate = n_transactions - self.n_fraud
        
    def generate_legitimate_transactions(self):
        """Generate legitimate transaction patterns"""
        legitimate = []
        
        for i in range(self.n_legitimate):
            # Normal spending patterns
            amount = np.random.gamma(2, 50)  # Most transactions are small amounts
            amount = min(amount, 1000)  # Cap at reasonable amount
            
            # Time patterns (more transactions during business hours)
            hour = np.random.choice(range(24), p=self._hour_probabilities())
            minute = np.random.randint(0, 60)
            day = np.random.randint(0, 30)
            
            # Location (consistent patterns)
            location_id = np.random.choice(range(100), p=self._location_probabilities())
            
            # Merchant categories (normal distribution)
            merchant_category = np.random.choice([
                'grocery', 'restaurant', 'gas_station', 'retail', 
                'online', 'entertainment', 'utilities'
            ])
            
            # Device info (mostly consistent)
            device_id = f"device_{np.random.randint(1, 20)}"
            
            transaction = {
                'transaction_id': f'TXN{i:06d}',
                'amount': round(amount, 2),
                'hour': hour,
                'minute': minute,
                'day': day,
                'location_id': location_id,
                'merchant_category': merchant_category,
                'device_id': device_id,
                'is_foreign': 0,
                'num_transactions_1h': np.random.poisson(1),
                'num_transactions_24h': np.random.poisson(5),
                'avg_amount_30d': round(np.random.gamma(2, 40), 2),
                'is_fraud': 0
            }
            legitimate.append(transaction)
            
        return pd.DataFrame(legitimate)
    
    def generate_fraudulent_transactions(self):
        """Generate fraudulent transaction patterns"""
        fraudulent = []
        
        for i in range(self.n_fraud):
            # Unusual patterns for fraud
            # Higher amounts
            amount = np.random.uniform(500, 5000)
            
            # Odd hours (late night/early morning)
            hour = np.random.choice([0, 1, 2, 3, 4, 5, 22, 23])
            minute = np.random.randint(0, 60)
            day = np.random.randint(0, 30)
            
            # Random/unusual locations
            location_id = np.random.randint(100, 500)
            
            # Unusual merchant categories or patterns
            merchant_category = np.random.choice([
                'online', 'international', 'cryptocurrency', 'luxury'
            ])
            
            # Different/new device
            device_id = f"device_{np.random.randint(100, 500)}"
            
            # Foreign transaction
            is_foreign = np.random.choice([0, 1], p=[0.3, 0.7])
            
            # Burst of transactions
            num_transactions_1h = np.random.poisson(5) + 3
            num_transactions_24h = np.random.poisson(15) + 10
            
            transaction = {
                'transaction_id': f'FRAUD{i:06d}',
                'amount': round(amount, 2),
                'hour': hour,
                'minute': minute,
                'day': day,
                'location_id': location_id,
                'merchant_category': merchant_category,
                'device_id': device_id,
                'is_foreign': is_foreign,
                'num_transactions_1h': num_transactions_1h,
                'num_transactions_24h': num_transactions_24h,
                'avg_amount_30d': round(np.random.gamma(2, 40), 2),
                'is_fraud': 1
            }
            fraudulent.append(transaction)
            
        return pd.DataFrame(fraudulent)
    
    def _hour_probabilities(self):
        """Generate realistic hour probabilities for legitimate transactions"""
        probs = np.array([0.5, 0.5, 0.3, 0.2, 0.2, 0.3,  # 0-5 AM (low)
                          0.8, 1.5, 2.0, 2.5, 3.0, 3.5,  # 6-11 AM (increasing)
                          4.0, 3.5, 3.0, 2.5, 2.0, 3.0,  # 12-5 PM (peak)
                          3.5, 4.0, 3.0, 2.0, 1.5, 1.0]) # 6-11 PM (evening)
        return probs / probs.sum()
    
    def _location_probabilities(self):
        """Generate location probabilities (some locations more common)"""
        probs = np.random.exponential(2, 100)
        return probs / probs.sum()
    
    def generate_dataset(self, save_path='transaction_data.csv'):
        """Generate complete dataset and save to CSV"""
        print("Generating legitimate transactions...")
        legitimate_df = self.generate_legitimate_transactions()
        
        print("Generating fraudulent transactions...")
        fraudulent_df = self.generate_fraudulent_transactions()
        
        print("Combining and shuffling dataset...")
        df = pd.concat([legitimate_df, fraudulent_df], ignore_index=True)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Add timestamp
        start_date = datetime.now() - timedelta(days=30)
        df['timestamp'] = [
            start_date + timedelta(days=int(row['day']), 
                                   hours=int(row['hour']), 
                                   minutes=int(row['minute']))
            for _, row in df.iterrows()
        ]
        
        # Save to CSV
        df.to_csv(save_path, index=False)
        print(f"\n✅ Dataset saved to {save_path}")
        print(f"Total transactions: {len(df)}")
        print(f"Fraudulent: {df['is_fraud'].sum()} ({df['is_fraud'].mean()*100:.2f}%)")
        print(f"Legitimate: {(1-df['is_fraud']).sum()} ({(1-df['is_fraud']).mean()*100:.2f}%)")
        
        return df

def main():
    """Generate sample dataset"""
    print("=" * 60)
    print("Fraud Detection System - Data Generator")
    print("=" * 60)
    
    generator = TransactionDataGenerator(n_transactions=10000, fraud_rate=0.02)
    df = generator.generate_dataset('transaction_data.csv')
    
    print("\nSample transactions:")
    print(df.head(10))
    print("\nDataset statistics:")
    print(df.describe())

if __name__ == '__main__':
    main()
