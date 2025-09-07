"""
H2O-3 AutoML pipeline for demand forecasting
Rapid training approach - under 5 minutes for demo purposes
"""

import h2o
from h2o.automl import H2OAutoML
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

def initialize_h2o():
    """Initialize H2O cluster (assumes Docker container is running)"""
    try:
        h2o.init(ip="localhost", port=54321, max_mem_size="4g")
        print("✅ Connected to H2O cluster")
        print(f"H2O cluster info: {h2o.cluster().cloud_name}")
    except Exception as e:
        print(f"❌ Failed to connect to H2O. Make sure Docker container is running:")
        print("   docker run -d -p 54321:54321 h2oai/h2o-open-source")
        print(f"Error: {e}")
        return False
    return True

def prepare_data_for_h2o(csv_path):
    """Load and prepare data for H2O AutoML"""
    print(f"📊 Loading data from {csv_path}")
    
    # Load with H2O
    df = h2o.import_file(csv_path)
    
    print(f"Loaded dataset shape: {df.shape}")
    print("Columns:", df.columns)
    
    # Convert date column
    df['date'] = h2o.as_date(df['date'], format="%Y-%m-%d")
    
    # Define features and target
    target = 'quantity_sold'
    features = [
        'product_id', 'category', 'price', 'day_of_week', 'month', 
        'is_weekend', 'is_holiday_season', 'on_promotion',
        'quantity_sold_7d_avg', 'quantity_sold_30d_avg', 'stock_level'
    ]
    
    # Filter to available features
    available_features = [f for f in features if f in df.columns]
    print(f"Using features: {available_features}")
    
    return df, available_features, target

def train_automl_model(df, features, target, max_runtime_secs=300):
    """Train H2O AutoML model for demand forecasting"""
    print(f"🤖 Training AutoML model (max {max_runtime_secs}s)...")
    
    # Split data (H2O way)
    train, test = df.split_frame(ratios=[0.8], seed=42)
    
    # Initialize AutoML
    aml = H2OAutoML(
        max_runtime_secs=max_runtime_secs,  # 5 minutes max
        max_models=20,  # Reasonable for demo
        seed=42,
        verbosity='info',
        sort_metric='RMSE'  # Good for regression
    )
    
    # Train model
    aml.train(x=features, y=target, training_frame=train)
    
    # Model performance
    print("\n🏆 Model Leaderboard (Top 5):")
    lb = aml.leaderboard.as_data_frame()
    print(lb.head())
    
    # Test set performance
    best_model = aml.leader
    test_perf = best_model.model_performance(test)
    print(f"\n📈 Best model test RMSE: {test_perf.rmse()[0][0]:.2f}")
    
    # Feature importance
    print("\n🔍 Top 10 Feature Importances:")
    var_imp = best_model.varimp(use_pandas=True)
    print(var_imp.head(10))
    
    return aml, test_perf

def save_model(aml, model_name="inventory_demand_model"):
    """Save trained model as MOJO for deployment"""
    print(f"💾 Saving model: {model_name}")
    
    os.makedirs('../shared/models', exist_ok=True)
    model_path = f'../shared/models/{model_name}'
    
    # Save as MOJO (fast scoring)
    mojo_path = aml.leader.download_mojo(path=model_path)
    print(f"✅ Model saved as MOJO: {mojo_path}")
    
    # Save predictions function
    predictions_code = f"""
# Generated H2O model predictions
import h2o

def predict_demand(data_dict):
    '''
    Predict demand for given product/date combination
    data_dict: dict with keys matching model features
    '''
    h2o.init()
    
    # Load MOJO
    model = h2o.import_mojo('{mojo_path}')
    
    # Convert dict to H2O frame
    df = h2o.H2OFrame(data_dict)
    
    # Make prediction
    prediction = model.predict(df)
    
    return prediction.as_data_frame()['predict'][0]
"""
    
    with open(f'{model_path}/predict.py', 'w') as f:
        f.write(predictions_code)
    
    return mojo_path

def main():
    """Main training pipeline"""
    print("🏪 Starting Inventory Intelligence ML Pipeline")
    
    # Step 1: Initialize H2O
    if not initialize_h2o():
        return
    
    # Step 2: Check if we have data, generate if needed
    data_path = '../shared/data/retail_train.csv'
    if not os.path.exists(data_path):
        print("📊 No training data found, generating...")
        os.system('python data_generator.py')
    
    # Step 3: Prepare data
    df, features, target = prepare_data_for_h2o(data_path)
    
    # Step 4: Train model
    aml, test_perf = train_automl_model(df, features, target, max_runtime_secs=300)
    
    # Step 5: Save model
    mojo_path = save_model(aml, "inventory_demand_model")
    
    print(f"\n🎉 Training complete!")
    print(f"Best model: {aml.leader.algo}")
    print(f"MOJO saved at: {mojo_path}")
    
    return aml, test_perf

if __name__ == "__main__":
    # Run the full pipeline
    aml, perf = main()