"""
H2O-native synthetic data generation for inventory intelligence
Using h2o.create_frame() for specialized retail/time-series data
"""

import h2o
from h2o import H2OFrame
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def initialize_h2o():
    """Initialize H2O cluster"""
    try:
        h2o.init(ip="localhost", port=54321, max_mem_size="4g")
        print("✅ Connected to H2O cluster")
        return True
    except Exception as e:
        print(f"❌ H2O connection failed. Start with: docker run -d -p 54321:54321 h2oai/h2o-open-source")
        print(f"Error: {e}")
        return False

def create_retail_base_frame():
    """Create base retail data using H2O's native create_frame function"""
    print("🏪 Creating base retail frame with H2O...")
    
    # Create synthetic product data (100 products)
    products_frame = h2o.create_frame(
        rows=100,
        cols=6,
        randomize=True,
        categorical_fraction=0.5,  # Product categories, suppliers
        real_fraction=0.3,         # Base prices, weights
        integer_fraction=0.2,      # SKU numbers, shelf life
        factors=20,                # Different categories/suppliers
        real_range=500,            # Price range 0-500
        integer_range=365,         # Shelf life up to 1 year
        missing_fraction=0.0,      # No missing values for products
        seed=42
    )
    
    # Rename columns for clarity
    products_frame.columns = ['product_id', 'category', 'supplier', 'base_price', 'weight', 'shelf_life_days']
    
    print(f"✅ Created {products_frame.nrows} products with {products_frame.ncols} attributes")
    return products_frame

def create_time_series_features():
    """Create time-based features for 2 years of data"""
    print("📅 Creating time series features...")
    
    # Generate 730 days (2 years) of date data
    dates = pd.date_range(start='2022-01-01', periods=730, freq='D')
    
    # Create time features
    time_data = pd.DataFrame({
        'date': dates,
        'year': dates.year,
        'month': dates.month,
        'day_of_week': dates.dayofweek,
        'quarter': dates.quarter,
        'week_of_year': dates.isocalendar().week,
        'is_weekend': (dates.dayofweek >= 5).astype(int),
        'is_holiday_season': dates.month.isin([11, 12]).astype(int),
        'day_of_year': dates.dayofyear
    })
    
    # Convert to H2O Frame
    time_frame = H2OFrame(time_data)
    print(f"✅ Created {time_frame.nrows} days of time features")
    return time_frame

def create_sales_patterns_frame():
    """Create realistic sales patterns using H2O"""
    print("📊 Creating sales pattern data...")
    
    # Create sales patterns for each product-date combination
    # This would be 100 products * 730 days = 73,000 records
    sales_frame = h2o.create_frame(
        rows=73000,  # 100 products * 730 days
        cols=8,
        randomize=True,
        real_fraction=0.6,     # Sales metrics, prices
        integer_fraction=0.3,   # Quantities, stock levels
        binary_fraction=0.1,    # Promotion flags
        real_range=100,         # Sales quantities 0-100
        integer_range=500,      # Stock levels 0-500
        binary_ones_fraction=0.1,  # 10% promotion rate
        missing_fraction=0.0,   # Complete data
        seed=123
    )
    
    # Rename columns meaningfully
    sales_frame.columns = [
        'base_demand', 'seasonal_factor', 'promotion_impact', 'weather_factor',
        'quantity_sold', 'stock_level', 'reorder_quantity', 'on_promotion'
    ]
    
    print(f"✅ Created {sales_frame.nrows} sales records")
    return sales_frame

def create_comprehensive_retail_dataset():
    """Create comprehensive retail dataset using H2O's capabilities"""
    if not initialize_h2o():
        return None
    
    print("🚀 Building comprehensive retail dataset with H2O...")
    
    # Step 1: Create product master data
    products_frame = create_retail_base_frame()
    
    # Step 2: Create time series features
    time_frame = create_time_series_features()
    
    # Step 3: Create sales patterns
    sales_frame = create_sales_patterns_frame()
    
    # Step 4: Create product-date combinations
    print("🔗 Creating product-date combinations...")
    
    # Create a cross-join equivalent for products and dates
    products_list = products_frame.as_data_frame()
    time_list = time_frame.as_data_frame()
    
    # Create Cartesian product (all combinations)
    retail_data = []
    for _, product in products_list.iterrows():
        for _, time_row in time_list.iterrows():
            # Calculate realistic demand based on multiple factors
            base_demand = np.random.uniform(5, 50)
            
            # Seasonal effects
            seasonal_multiplier = 1 + 0.3 * np.sin(2 * np.pi * time_row['day_of_year'] / 365)
            
            # Weekend effects (varies by category)
            weekend_effect = 1.3 if time_row['is_weekend'] and np.random.random() < 0.5 else 1.0
            
            # Holiday season boost
            holiday_effect = 2.0 if time_row['is_holiday_season'] else 1.0
            
            # Random promotions
            on_promotion = np.random.random() < 0.1  # 10% chance
            promotion_effect = 1.5 if on_promotion else 1.0
            
            # Calculate final demand with noise
            final_demand = max(0, int(
                base_demand * seasonal_multiplier * weekend_effect * 
                holiday_effect * promotion_effect * np.random.uniform(0.7, 1.3)
            ))
            
            # Dynamic pricing
            price = product['base_price'] * (0.8 if on_promotion else 1.0) * np.random.uniform(0.95, 1.05)
            
            retail_data.append({
                'date': time_row['date'],
                'product_id': f"PROD_{int(product['product_id']):03d}",
                'category': product['category'],
                'supplier': product['supplier'],
                'quantity_sold': final_demand,
                'price': round(price, 2),
                'revenue': round(final_demand * price, 2),
                'stock_level': np.random.randint(20, 300),
                'base_price': product['base_price'],
                'weight': product['weight'],
                'year': time_row['year'],
                'month': time_row['month'],
                'day_of_week': time_row['day_of_week'],
                'quarter': time_row['quarter'],
                'is_weekend': time_row['is_weekend'],
                'is_holiday_season': time_row['is_holiday_season'],
                'on_promotion': on_promotion,
                'day_of_year': time_row['day_of_year']
            })
    
    # Convert to H2O Frame
    retail_df = pd.DataFrame(retail_data)
    print(f"📊 Created comprehensive dataset with {len(retail_df)} records")
    
    # Convert to H2O Frame
    h2o_retail_frame = H2OFrame(retail_df)
    
    # Add calculated features using H2O operations
    print("🔧 Adding advanced features with H2O...")
    
    # Sort by product and date for time series features
    h2o_retail_frame = h2o_retail_frame.sort(['product_id', 'date'])
    
    # Add rolling averages (H2O way)
    # Note: H2O doesn't have direct rolling window functions, so we'll add these in pandas then convert
    retail_df['date'] = pd.to_datetime(retail_df['date'])
    retail_df = retail_df.sort_values(['product_id', 'date'])
    
    # Calculate rolling features
    retail_df['quantity_sold_7d_avg'] = retail_df.groupby('product_id')['quantity_sold'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    retail_df['quantity_sold_30d_avg'] = retail_df.groupby('product_id')['quantity_sold'].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean()
    )
    retail_df['revenue_7d_sum'] = retail_df.groupby('product_id')['revenue'].transform(
        lambda x: x.rolling(window=7, min_periods=1).sum()
    )
    
    # Stockout risk indicator
    retail_df['stockout_risk'] = (retail_df['stock_level'] < retail_df['quantity_sold_7d_avg'] * 3).astype(int)
    
    # Reorder point calculation
    retail_df['reorder_point'] = retail_df['quantity_sold_30d_avg'] * 7  # 1 week buffer
    retail_df['needs_reorder'] = (retail_df['stock_level'] < retail_df['reorder_point']).astype(int)
    
    # Convert final dataset to H2O Frame
    final_h2o_frame = H2OFrame(retail_df)
    
    print(f"✅ Final dataset shape: {final_h2o_frame.shape}")
    print("📝 Dataset columns:", final_h2o_frame.columns)
    
    return final_h2o_frame, retail_df

def save_datasets(h2o_frame, pandas_df):
    """Save datasets in multiple formats"""
    print("💾 Saving datasets...")
    
    import os
    os.makedirs('../shared/data', exist_ok=True)
    
    # Save pandas version for compatibility
    pandas_df.to_csv('../shared/data/retail_full.csv', index=False)
    
    # Split into train/test
    split_date = pandas_df['date'].quantile(0.8)
    train_df = pandas_df[pandas_df['date'] <= split_date]
    test_df = pandas_df[pandas_df['date'] > split_date]
    
    train_df.to_csv('../shared/data/retail_train.csv', index=False)
    test_df.to_csv('../shared/data/retail_test.csv', index=False)
    
    # Save H2O version
    h2o.export_file(h2o_frame, '../shared/data/retail_h2o.csv', force=True)
    
    print(f"✅ Saved datasets:")
    print(f"   - Full: {len(pandas_df)} records ({len(pandas_df.columns)} columns)")
    print(f"   - Train: {len(train_df)} records")
    print(f"   - Test: {len(test_df)} records")
    print(f"   - Products: {pandas_df['product_id'].nunique()}")
    print(f"   - Date range: {pandas_df['date'].min()} to {pandas_df['date'].max()}")

def demo_h2o_features():
    """Demonstrate H2O's advanced data generation features"""
    print("🎯 Demonstrating H2O's advanced data generation...")
    
    if not initialize_h2o():
        return
    
    # Example 1: Create a customer dataset with specific distributions
    customers = h2o.create_frame(
        rows=1000,
        cols=5,
        categorical_fraction=0.4,  # Demographics
        real_fraction=0.4,         # Income, spending
        integer_fraction=0.2,      # Age, tenure
        factors=10,
        real_range=100000,         # Income up to 100K
        integer_range=80,          # Age up to 80
        missing_fraction=0.05,     # Some missing data
        seed=456
    )
    
    customers.columns = ['segment', 'region', 'income', 'spending_score', 'age']
    print("👥 Customer dataset:", customers.shape)
    
    # Example 2: Create time series with response variable
    timeseries = h2o.create_frame(
        rows=1000,
        cols=8,
        has_response=True,         # Add target variable
        response_factors=1,        # Continuous response
        real_fraction=0.8,
        categorical_fraction=0.1,
        integer_fraction=0.1,
        missing_fraction=0.02,
        seed=789
    )
    
    print("📈 Time series with target:", timeseries.shape)
    print("📊 Sample data:")
    print(timeseries.head())
    
    return customers, timeseries

if __name__ == "__main__":
    print("🚀 H2O Native Synthetic Data Generation Demo")
    
    # Demo H2O's capabilities
    demo_h2o_features()
    
    # Create comprehensive retail dataset
    h2o_frame, pandas_df = create_comprehensive_retail_dataset()
    
    # Save datasets
    save_datasets(h2o_frame, pandas_df)
    
    print("\n🎉 H2O-powered data generation complete!")
    print("📊 Ready for AutoML training with native H2O datasets")