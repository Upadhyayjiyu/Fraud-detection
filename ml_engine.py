"""
Machine Learning Engine for Fraud Detection
Handles data preprocessing, model training, evaluation, and prediction
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

class FraudDetectionEngine:
    def __init__(self):
        """Initialize the fraud detection engine"""
        self.models = {}
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
        
    def preprocess_data(self, df, fit=True):
        """
        Preprocess transaction data
        
        Args:
            df: DataFrame with transaction data
            fit: Whether to fit encoders and scaler (True for training)
        
        Returns:
            Preprocessed feature matrix
        """
        df = df.copy()
        
        # Encode categorical features
        categorical_cols = ['merchant_category', 'device_id']
        
        for col in categorical_cols:
            if col in df.columns:
                if fit:
                    self.label_encoders[col] = LabelEncoder()
                    df[col + '_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Handle unseen categories
                    df[col + '_encoded'] = df[col].astype(str).map(
                        lambda x: self.label_encoders[col].transform([x])[0] 
                        if x in self.label_encoders[col].classes_ 
                        else -1
                    )
        
        # Feature engineering
        df['amount_zscore'] = (df['amount'] - df['amount'].mean()) / df['amount'].std()
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['amount_vs_avg_ratio'] = df['amount'] / (df['avg_amount_30d'] + 1)
        df['transaction_velocity_1h'] = df['num_transactions_1h'] / 1
        df['transaction_velocity_24h'] = df['num_transactions_24h'] / 24
        
        # Select features for modeling
        feature_cols = [
            'amount', 'amount_zscore', 'hour_sin', 'hour_cos', 
            'location_id', 'is_foreign', 'num_transactions_1h', 
            'num_transactions_24h', 'amount_vs_avg_ratio',
            'transaction_velocity_1h', 'transaction_velocity_24h',
            'merchant_category_encoded', 'device_id_encoded'
        ]
        
        # Store feature columns for later use
        if fit:
            self.feature_columns = feature_cols
        
        X = df[feature_cols].fillna(0)
        
        # Scale features
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return X_scaled, df
    
    def handle_imbalanced_data(self, X, y):
        """Apply SMOTE to handle imbalanced dataset"""
        print(f"Original dataset - Fraud: {y.sum()}, Legitimate: {(1-y).sum()}")
        
        smote = SMOTE(random_state=42, k_neighbors=5)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        
        print(f"After SMOTE - Fraud: {y_resampled.sum()}, Legitimate: {(1-y_resampled).sum()}")
        
        return X_resampled, y_resampled
    
    def train_models(self, df):
        """
        Train multiple ML models for fraud detection
        
        Args:
            df: DataFrame with transaction data including 'is_fraud' column
        """
        print("=" * 60)
        print("Training Fraud Detection Models")
        print("=" * 60)
        
        # Preprocess data
        print("\n1. Preprocessing data...")
        X, df_processed = self.preprocess_data(df, fit=True)
        y = df['is_fraud'].values
        
        # Split data
        print("2. Splitting data (80% train, 20% test)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Handle imbalanced data
        print("\n3. Applying SMOTE to handle imbalanced data...")
        X_train_balanced, y_train_balanced = self.handle_imbalanced_data(X_train, y_train)
        
        # Train Logistic Regression
        print("\n4. Training Logistic Regression...")
        lr_model = LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')
        lr_model.fit(X_train_balanced, y_train_balanced)
        self.models['logistic_regression'] = lr_model
        
        # Train Random Forest
        print("5. Training Random Forest...")
        rf_model = RandomForestClassifier(
            n_estimators=100, random_state=42, max_depth=10, 
            class_weight='balanced', n_jobs=-1
        )
        rf_model.fit(X_train_balanced, y_train_balanced)
        self.models['random_forest'] = rf_model
        
        # Train Isolation Forest (anomaly detection)
        print("6. Training Isolation Forest...")
        iso_model = IsolationForest(
            contamination=0.02, random_state=42, n_jobs=-1
        )
        iso_model.fit(X_train)  # Isolation Forest works differently
        self.models['isolation_forest'] = iso_model
        
        # Evaluate models
        print("\n" + "=" * 60)
        print("Model Evaluation Results")
        print("=" * 60)
        
        self.evaluate_models(X_test, y_test)
        
        self.is_trained = True
        print("\n✅ All models trained successfully!")
        
        # Save models
        self.save_models()
        
    def evaluate_models(self, X_test, y_test):
        """Evaluate all trained models"""
        for model_name, model in self.models.items():
            print(f"\n📊 {model_name.upper().replace('_', ' ')}:")
            print("-" * 60)
            
            if model_name == 'isolation_forest':
                # Isolation Forest returns -1 for anomalies, 1 for normal
                y_pred = model.predict(X_test)
                y_pred = np.where(y_pred == -1, 1, 0)  # Convert to 0/1
                y_pred_proba = model.score_samples(X_test)
            else:
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            
            print(f"Accuracy:  {accuracy:.4f}")
            print(f"Precision: {precision:.4f}")
            print(f"Recall:    {recall:.4f}")
            print(f"F1-Score:  {f1:.4f}")
            
            if model_name != 'isolation_forest':
                roc_auc = roc_auc_score(y_test, y_pred_proba)
                print(f"ROC-AUC:   {roc_auc:.4f}")
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            print(f"\nConfusion Matrix:")
            print(f"TN: {cm[0][0]:4d} | FP: {cm[0][1]:4d}")
            print(f"FN: {cm[1][0]:4d} | TP: {cm[1][1]:4d}")
    
    def predict(self, transaction_data, model_name='random_forest'):
        """
        Predict fraud for new transaction(s)
        
        Args:
            transaction_data: DataFrame with transaction features
            model_name: Name of model to use for prediction
        
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            raise Exception("Models not trained! Run train_models() first.")
        
        # Preprocess
        X, df_processed = self.preprocess_data(transaction_data, fit=False)
        
        # Get model
        model = self.models.get(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not found")
        
        # Predict
        if model_name == 'isolation_forest':
            predictions = model.predict(X)
            predictions = np.where(predictions == -1, 1, 0)
            fraud_scores = -model.score_samples(X)  # Higher score = more anomalous
        else:
            predictions = model.predict(X)
            fraud_scores = model.predict_proba(X)[:, 1]
        
        results = {
            'predictions': predictions,
            'fraud_scores': fraud_scores,
            'is_fraud': predictions.astype(bool)
        }
        
        return results
    
    def save_models(self, directory='models'):
        """Save trained models and preprocessors"""
        os.makedirs(directory, exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            model_path = os.path.join(directory, f'{name}.pkl')
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
        
        # Save scaler and encoders
        with open(os.path.join(directory, 'scaler.pkl'), 'wb') as f:
            pickle.dump(self.scaler, f)
        
        with open(os.path.join(directory, 'label_encoders.pkl'), 'wb') as f:
            pickle.dump(self.label_encoders, f)
        
        with open(os.path.join(directory, 'feature_columns.pkl'), 'wb') as f:
            pickle.dump(self.feature_columns, f)
        
        print(f"\n💾 Models saved to '{directory}/' directory")
    
    def load_models(self, directory='models'):
        """Load trained models and preprocessors"""
        # Load models
        for model_name in ['logistic_regression', 'random_forest', 'isolation_forest']:
            model_path = os.path.join(directory, f'{model_name}.pkl')
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.models[model_name] = pickle.load(f)
        
        # Load scaler and encoders
        with open(os.path.join(directory, 'scaler.pkl'), 'rb') as f:
            self.scaler = pickle.load(f)
        
        with open(os.path.join(directory, 'label_encoders.pkl'), 'rb') as f:
            self.label_encoders = pickle.load(f)
        
        with open(os.path.join(directory, 'feature_columns.pkl'), 'rb') as f:
            self.feature_columns = pickle.load(f)
        
        self.is_trained = True
        print("✅ Models loaded successfully!")

def main():
    """Main training pipeline"""
    import sys
    
    # Check if training flag is passed
    if len(sys.argv) > 1 and sys.argv[1] == '--train':
        # Load data
        print("Loading transaction data...")
        df = pd.read_csv('transaction_data.csv')
        
        # Initialize engine
        engine = FraudDetectionEngine()
        
        # Train models
        engine.train_models(df)
    else:
        print("Usage: python ml_engine.py --train")
        print("Make sure transaction_data.csv exists (run data_generator.py first)")

if __name__ == '__main__':
    main()
