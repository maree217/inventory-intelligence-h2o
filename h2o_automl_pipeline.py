"""
H2O-3 AutoML pipeline using native H2O synthetic data
Optimized for rapid prototyping with specialized retail forecasting
"""

import h2o
from h2o.automl import H2OAutoML
from h2o import H2OFrame
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

def initialize_h2o():
    """Initialize H2O cluster with optimal settings for demo"""
    try:
        h2o.init(ip="localhost", port=54321, max_mem_size="4g", nthreads=-1)
        print("✅ H2O cluster initialized successfully")
        print(f"📊 Cluster info: {h2o.cluster().cloud_name}")
        print(f"🖥️  Memory: {h2o.cluster().free_mem}")
        return True
    except Exception as e:
        print(f"❌ H2O initialization failed: {e}")
        print("💡 Start H2O with: docker run -d -p 54321:54321 h2oai/h2o-open-source")
        return False

def create_advanced_retail_dataset():
    """Create sophisticated retail dataset using H2O's native functions"""
    print("🏪 Creating advanced retail dataset with H2O native functions...")
    
    # Create base product catalog using H2O
    products = h2o.create_frame(
        rows=50,  # 50 products for demo speed
        cols=4,
        categorical_fraction=0.5,  # Categories, brands
        real_fraction=0.25,        # Prices, margins  
        integer_fraction=0.25,     # Stock levels
        factors=8,                 # 8 different categories
        real_range=200,            # Price range $0-200
        integer_range=1000,        # Stock up to 1000 units
        missing_fraction=0.0,
        seed=42
    )
    
    products.columns = ['category', 'brand', 'base_price', 'margin', 'initial_stock']
    
    # Create customer segments
    segments = h2o.create_frame(
        rows=5,
        cols=3,
        categorical_fraction=0.33,
        real_fraction=0.67,
        factors=3,
        real_range=100,
        seed=123
    )
    segments.columns = ['segment_name', 'purchase_frequency', 'price_sensitivity']
    
    # Create main sales transaction dataset
    sales = h2o.create_frame(
        rows=10000,  # 10K transactions for demo
        cols=12,
        categorical_fraction=0.25,  # Product, customer, channel
        real_fraction=0.5,          # Prices, quantities, weather
        integer_fraction=0.17,      # Dates, IDs
        binary_fraction=0.08,       # Promotions, weekends
        factors=20,
        real_range=100,
        integer_range=365,
        binary_ones_fraction=0.15,  # 15% promotion rate
        missing_fraction=0.01,      # Minimal missing data
        has_response=True,          # Add target variable
        response_factors=1,         # Continuous target (sales amount)
        seed=456
    )
    
    # Rename columns for business context
    sales.columns = [
        'product_id', 'customer_segment', 'sales_channel', 'price', 'base_demand',
        'weather_score', 'competitor_price', 'inventory_level', 'day_of_year', 
        'month', 'promo_depth', 'is_weekend', 'response'  # response is our target
    ]
    
    print(f"✅ Created datasets:")
    print(f"   - Products: {products.shape}")
    print(f"   - Segments: {segments.shape}") 
    print(f"   - Sales: {sales.shape}")
    
    return products, segments, sales

def enhance_features(sales_frame):
    """Add advanced features using H2O operations"""
    print("🔧 Engineering advanced features with H2O...")
    
    # Create time-based features
    sales_frame['quarter'] = (sales_frame['month'] / 3).ceil()
    sales_frame['is_holiday_season'] = (sales_frame['month'].isin([11, 12])).ifelse(1, 0)
    sales_frame['is_summer'] = (sales_frame['month'].isin([6, 7, 8])).ifelse(1, 0)
    
    # Price-based features
    sales_frame['price_vs_competitor'] = sales_frame['price'] / sales_frame['competitor_price']
    sales_frame['discount_pct'] = (sales_frame['promo_depth'] / sales_frame['price']) * 100
    
    # Demand-based features
    sales_frame['inventory_ratio'] = sales_frame['inventory_level'] / sales_frame['base_demand']
    sales_frame['demand_weather_interaction'] = sales_frame['base_demand'] * sales_frame['weather_score']
    
    # Binary feature combinations
    sales_frame['weekend_promo'] = (sales_frame['is_weekend'] * (sales_frame['promo_depth'] > 0)).ifelse(1, 0)
    
    print("✅ Added advanced features using H2O operations")
    print(f"📊 Enhanced dataset shape: {sales_frame.shape}")
    
    return sales_frame

def run_automl_experiment(train_frame, test_frame, target_col='response', max_runtime_secs=300):
    """Run comprehensive AutoML experiment"""
    print(f"🤖 Starting AutoML experiment (max {max_runtime_secs}s)...")
    
    # Define feature columns (exclude target and IDs)
    feature_cols = [col for col in train_frame.columns if col != target_col]
    
    print(f"🎯 Target: {target_col}")
    print(f"📊 Features: {len(feature_cols)} columns")
    print(f"🏋️  Training samples: {train_frame.nrows}")
    print(f"🧪 Test samples: {test_frame.nrows}")
    
    # Initialize AutoML with comprehensive settings
    aml = H2OAutoML(
        max_runtime_secs=max_runtime_secs,
        max_models=25,              # More models for better results
        seed=42,
        verbosity='info',
        sort_metric='RMSE',         # Optimize for regression
        balance_classes=False,       # For regression
        exclude_algos=['DeepLearning'],  # Faster training without DL
        stopping_metric='RMSE',
        stopping_tolerance=0.001,
        stopping_rounds=3,
        nfolds=5                    # Cross-validation
    )
    
    # Train AutoML
    print("🚀 Training AutoML models...")
    aml.train(x=feature_cols, y=target_col, training_frame=train_frame)
    
    # Get results
    print("\n🏆 AutoML Leaderboard (Top 10):")
    leaderboard = aml.leaderboard.as_data_frame()
    print(leaderboard.head(10))
    
    # Test set performance
    best_model = aml.leader
    test_performance = best_model.model_performance(test_frame)
    
    print(f"\n📈 Best Model Performance on Test Set:")
    print(f"   Algorithm: {best_model.algo}")
    print(f"   RMSE: {test_performance.rmse()[0][0]:.4f}")
    print(f"   MAE: {test_performance.mae()[0][0]:.4f}")
    print(f"   Mean Residual Deviance: {test_performance.mean_residual_deviance():.4f}")
    
    # Feature importance
    print(f"\n🔍 Top 10 Feature Importances:")
    if hasattr(best_model, 'varimp'):
        var_imp = best_model.varimp(use_pandas=True)
        print(var_imp.head(10))
    
    return aml, test_performance

def create_prediction_service(aml, model_name="retail_forecasting_model"):
    """Create production-ready prediction service"""
    print(f"🚀 Creating prediction service: {model_name}")
    
    # Create models directory
    os.makedirs('../shared/models', exist_ok=True)
    model_dir = f'../shared/models/{model_name}'
    os.makedirs(model_dir, exist_ok=True)
    
    # Save best model as MOJO
    best_model = aml.leader
    mojo_path = best_model.download_mojo(path=model_dir)
    
    # Create prediction function
    prediction_code = f'''
"""
Production-ready prediction service for retail forecasting
Generated by H2O AutoML pipeline
"""

import h2o
import pandas as pd
from h2o import H2OFrame

class RetailForecastingService:
    def __init__(self):
        self.model_path = "{mojo_path}"
        self.model = None
        self.is_initialized = False
    
    def initialize(self):
        """Initialize H2O and load model"""
        if not self.is_initialized:
            h2o.init()
            self.model = h2o.import_mojo(self.model_path)
            self.is_initialized = True
            print("✅ Forecasting service initialized")
    
    def predict_demand(self, input_data):
        """
        Predict retail demand for given inputs
        
        Args:
            input_data: dict or pandas DataFrame with features
        
        Returns:
            Predicted demand value(s)
        """
        if not self.is_initialized:
            self.initialize()
        
        # Convert input to H2O Frame
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
        
        h2o_data = H2OFrame(input_data)
        
        # Make prediction
        prediction = self.model.predict(h2o_data)
        
        return prediction.as_data_frame()['predict'].tolist()
    
    def predict_batch(self, csv_file_path):
        """Batch prediction from CSV file"""
        if not self.is_initialized:
            self.initialize()
        
        data = h2o.import_file(csv_file_path)
        predictions = self.model.predict(data)
        
        return predictions.as_data_frame()

# Example usage:
# service = RetailForecastingService()
# result = service.predict_demand({{
#     'product_id': 'PROD_001',
#     'price': 29.99,
#     'base_demand': 15,
#     'weather_score': 0.8,
#     'month': 12,
#     'is_weekend': 1,
#     'promo_depth': 5.0
# }})
'''
    
    # Save prediction service
    with open(f'{model_dir}/prediction_service.py', 'w') as f:
        f.write(prediction_code)
    
    # Save model metadata
    metadata = f'''
# Retail Forecasting Model Metadata

**Model Type**: {best_model.algo}
**Training Date**: {pd.Timestamp.now()}
**Performance Metrics**: 
- RMSE: {aml.leader.rmse()}
- Model Count**: {len(aml.leaderboard)}

**Features Used**: {aml.leader.params.get('x', 'N/A')}

**Usage**:
```python
from prediction_service import RetailForecastingService
service = RetailForecastingService()
prediction = service.predict_demand(your_data)
```
'''
    
    with open(f'{model_dir}/README.md', 'w') as f:
        f.write(metadata)
    
    print(f"✅ Model saved with prediction service at: {model_dir}")
    return model_dir

def run_comprehensive_pipeline():
    """Run the complete H2O-native pipeline"""
    print("🚀 H2O-Native Retail Forecasting Pipeline Starting...")
    
    # Step 1: Initialize H2O
    if not initialize_h2o():
        return None
    
    # Step 2: Create synthetic datasets using H2O
    products, segments, sales = create_advanced_retail_dataset()
    
    # Step 3: Feature engineering
    enhanced_sales = enhance_features(sales)
    
    # Step 4: Train/test split (80/20)
    train, test = enhanced_sales.split_frame(ratios=[0.8], seed=42)
    
    print(f"📊 Data split: {train.nrows} train, {test.nrows} test samples")
    
    # Step 5: Run AutoML
    aml, performance = run_automl_experiment(train, test, target_col='response', max_runtime_secs=300)
    
    # Step 6: Create prediction service
    model_path = create_prediction_service(aml, "h2o_retail_forecasting")
    
    # Step 7: Demo predictions
    print("\n🎯 Demo Predictions:")
    sample_data = test.head(5)
    predictions = aml.leader.predict(sample_data)
    
    # Show sample predictions
    sample_df = sample_data.as_data_frame()
    pred_df = predictions.as_data_frame()
    
    print("📊 Sample Predictions vs Actuals:")
    comparison = pd.DataFrame({
        'Predicted': pred_df['predict'],
        'Actual': sample_df['response'],
        'Product': sample_df['product_id'],
        'Price': sample_df['price']
    })
    print(comparison)
    
    print(f"\n🎉 Pipeline Complete!")
    print(f"📁 Model saved at: {model_path}")
    print(f"🏆 Best algorithm: {aml.leader.algo}")
    print(f"📈 Test RMSE: {performance.rmse()[0][0]:.4f}")
    
    return aml, performance, model_path

if __name__ == "__main__":
    # Run the complete pipeline
    results = run_comprehensive_pipeline()
    
    if results:
        aml, performance, model_path = results
        print("\n✅ H2O-Native AutoML Pipeline Successfully Completed!")
        print("🚀 Ready for Streamlit UI integration")