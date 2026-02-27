import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def prepare_features(df):
    """Prepare features for model training"""
    print("Preparing features...")

    # Select feature columns
    feature_cols = [
        'latitude', 'longitude', 'parking_spaces',
        'hour', 'day_of_week', 'month', 'day',
        'is_weekend', 'is_business_hours', 'is_rush_hour'
    ]

    # Add categorical encoding for borough
    df_encoded = pd.get_dummies(df, columns=['borough', 'meter_type', 'facility_type'],
                                  prefix=['boro', 'meter', 'facility'])

    # Get all feature columns (including one-hot encoded)
    feature_cols_encoded = [col for col in df_encoded.columns
                            if col in feature_cols or col.startswith(('boro_', 'meter_', 'facility_'))]

    X = df_encoded[feature_cols_encoded]
    y = df_encoded['free_spaces']

    print(f"Features: {X.shape[1]} columns")
    print(f"Target: {y.name}")

    return X, y, feature_cols_encoded

def train_models(X, y):
    """Train multiple models and compare performance"""
    print("\nSplitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training set: {len(X_train):,} samples")
    print(f"Test set: {len(X_test):,} samples")

    models = {}
    results = {}

    # 1. Random Forest
    print("\n" + "="*50)
    print("Training Random Forest...")
    print("="*50)
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    rf_model.fit(X_train, y_train)
    models['random_forest'] = rf_model

    # Evaluate Random Forest
    y_pred_train_rf = rf_model.predict(X_train)
    y_pred_test_rf = rf_model.predict(X_test)

    results['random_forest'] = {
        'train_mae': mean_absolute_error(y_train, y_pred_train_rf),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train_rf)),
        'train_r2': r2_score(y_train, y_pred_train_rf),
        'test_mae': mean_absolute_error(y_test, y_pred_test_rf),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test_rf)),
        'test_r2': r2_score(y_test, y_pred_test_rf)
    }

    print("\nRandom Forest Performance:")
    print(f"  Train MAE: {results['random_forest']['train_mae']:.3f}")
    print(f"  Train RMSE: {results['random_forest']['train_rmse']:.3f}")
    print(f"  Train R²: {results['random_forest']['train_r2']:.4f}")
    print(f"  Test MAE: {results['random_forest']['test_mae']:.3f}")
    print(f"  Test RMSE: {results['random_forest']['test_rmse']:.3f}")
    print(f"  Test R²: {results['random_forest']['test_r2']:.4f}")

    # 2. XGBoost
    print("\n" + "="*50)
    print("Training XGBoost...")
    print("="*50)
    xgb_model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=1
    )
    xgb_model.fit(X_train, y_train)
    models['xgboost'] = xgb_model

    # Evaluate XGBoost
    y_pred_train_xgb = xgb_model.predict(X_train)
    y_pred_test_xgb = xgb_model.predict(X_test)

    results['xgboost'] = {
        'train_mae': mean_absolute_error(y_train, y_pred_train_xgb),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train_xgb)),
        'train_r2': r2_score(y_train, y_pred_train_xgb),
        'test_mae': mean_absolute_error(y_test, y_pred_test_xgb),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test_xgb)),
        'test_r2': r2_score(y_test, y_pred_test_xgb)
    }

    print("\nXGBoost Performance:")
    print(f"  Train MAE: {results['xgboost']['train_mae']:.3f}")
    print(f"  Train RMSE: {results['xgboost']['train_rmse']:.3f}")
    print(f"  Train R²: {results['xgboost']['train_r2']:.4f}")
    print(f"  Test MAE: {results['xgboost']['test_mae']:.3f}")
    print(f"  Test RMSE: {results['xgboost']['test_rmse']:.3f}")
    print(f"  Test R²: {results['xgboost']['test_r2']:.4f}")

    # 3. Gradient Boosting
    print("\n" + "="*50)
    print("Training Gradient Boosting...")
    print("="*50)
    gb_model = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=8,
        learning_rate=0.1,
        random_state=42,
        verbose=1
    )
    gb_model.fit(X_train, y_train)
    models['gradient_boosting'] = gb_model

    # Evaluate Gradient Boosting
    y_pred_train_gb = gb_model.predict(X_train)
    y_pred_test_gb = gb_model.predict(X_test)

    results['gradient_boosting'] = {
        'train_mae': mean_absolute_error(y_train, y_pred_train_gb),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train_gb)),
        'train_r2': r2_score(y_train, y_pred_train_gb),
        'test_mae': mean_absolute_error(y_test, y_pred_test_gb),
        'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test_gb)),
        'test_r2': r2_score(y_test, y_pred_test_gb)
    }

    print("\nGradient Boosting Performance:")
    print(f"  Train MAE: {results['gradient_boosting']['train_mae']:.3f}")
    print(f"  Train RMSE: {results['gradient_boosting']['train_rmse']:.3f}")
    print(f"  Train R²: {results['gradient_boosting']['train_r2']:.4f}")
    print(f"  Test MAE: {results['gradient_boosting']['test_mae']:.3f}")
    print(f"  Test RMSE: {results['gradient_boosting']['test_rmse']:.3f}")
    print(f"  Test R²: {results['gradient_boosting']['test_r2']:.4f}")

    # Select best model
    best_model_name = min(results.items(), key=lambda x: x[1]['test_mae'])[0]
    best_model = models[best_model_name]

    print("\n" + "="*50)
    print(f"BEST MODEL: {best_model_name.upper()}")
    print("="*50)

    return models, results, best_model, best_model_name, X_test, y_test

def plot_feature_importance(model, feature_names, model_name):
    """Plot feature importance"""
    print("\nPlotting feature importance...")

    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        indices = np.argsort(importance)[::-1][:15]  # Top 15 features

        plt.figure(figsize=(10, 6))
        plt.title(f'Top 15 Features - {model_name}')
        plt.barh(range(15), importance[indices])
        plt.yticks(range(15), [feature_names[i] for i in indices])
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.savefig(f'../models/feature_importance_{model_name}.png', dpi=150)
        print(f"Saved feature importance plot to: models/feature_importance_{model_name}.png")
        plt.close()

def save_models(models, best_model_name, feature_cols):
    """Save all models"""
    print("\nSaving models...")

    for name, model in models.items():
        filename = f'../models/{name}_model.pkl'
        joblib.dump(model, filename)
        print(f"Saved {name} to: {filename}")

    # Save best model separately
    best_model_file = '../models/best_model.pkl'
    joblib.dump(models[best_model_name], best_model_file)
    print(f"\nBest model ({best_model_name}) saved to: {best_model_file}")

    # Save feature columns
    joblib.dump(feature_cols, '../models/feature_columns.pkl')
    print("Saved feature columns to: models/feature_columns.pkl")

    # Save model metadata
    metadata = {
        'best_model': best_model_name,
        'feature_columns': feature_cols,
        'timestamp': pd.Timestamp.now().isoformat()
    }
    joblib.dump(metadata, '../models/model_metadata.pkl')
    print("Saved model metadata to: models/model_metadata.pkl")

if __name__ == "__main__":
    # Load training data
    print("Loading training data...")
    df = pd.read_csv('../data/training_data.csv')
    print(f"Loaded {len(df):,} records")

    # Prepare features
    X, y, feature_cols = prepare_features(df)

    # Train models
    models, results, best_model, best_model_name, X_test, y_test = train_models(X, y)

    # Plot feature importance for best model
    plot_feature_importance(best_model, feature_cols, best_model_name)

    # Save models
    save_models(models, best_model_name, feature_cols)

    print("\n" + "="*50)
    print("MODEL TRAINING COMPLETE!")
    print("="*50)
