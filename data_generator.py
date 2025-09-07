"""
Generate synthetic retail sales data for inventory optimization demo
Focus: realistic patterns that showcase H2O-3 AutoML capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from utils.data_generator import RapidDataGenerator
import pandas as pd

def generate_and_save_retail_data():
    """Generate comprehensive retail dataset for H2O-3 training"""
    
    print("🏪 Starting Inventory Intelligence data generation...")
    
    generator = RapidDataGenerator(seed=42)
    
    # Generate 2 years of data for 100 products (as per sprint plan)
    retail_df = generator.generate_retail_data(n_products=100, n_days=730)
    
    # Add additional features for ML
    retail_df['date'] = pd.to_datetime(retail_df['date'])
    retail_df['year'] = retail_df['date'].dt.year
    retail_df['quarter'] = retail_df['date'].dt.quarter
    retail_df['week_of_year'] = retail_df['date'].dt.isocalendar().week
    
    # Calculate rolling features (good for time series)
    retail_df = retail_df.sort_values(['product_id', 'date'])
    retail_df['quantity_sold_7d_avg'] = retail_df.groupby('product_id')['quantity_sold'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    retail_df['quantity_sold_30d_avg'] = retail_df.groupby('product_id')['quantity_sold'].transform(
        lambda x: x.rolling(window=30, min_periods=1).mean()
    )
    
    # Create inventory metrics
    retail_df['stock_level'] = retail_df.groupby('product_id').apply(
        lambda group: pd.Series(
            [max(50, int(np.random.uniform(20, 200))) for _ in range(len(group))],
            index=group.index
        )
    ).values
    
    retail_df['stockout_risk'] = (retail_df['stock_level'] < retail_df['quantity_sold_7d_avg']).astype(int)
    
    # Split into train/test (80/20 split by time)
    split_date = retail_df['date'].quantile(0.8)
    train_df = retail_df[retail_df['date'] <= split_date].copy()
    test_df = retail_df[retail_df['date'] > split_date].copy()
    
    # Save datasets
    os.makedirs('../shared/data', exist_ok=True)
    retail_df.to_csv('../shared/data/retail_full.csv', index=False)
    train_df.to_csv('../shared/data/retail_train.csv', index=False)
    test_df.to_csv('../shared/data/retail_test.csv', index=False)
    
    print(f"✅ Saved retail datasets:")
    print(f"   - Full dataset: {len(retail_df)} records")
    print(f"   - Training: {len(train_df)} records")
    print(f"   - Testing: {len(test_df)} records")
    print(f"   - Products: {retail_df['product_id'].nunique()}")
    print(f"   - Date range: {retail_df['date'].min()} to {retail_df['date'].max()}")
    
    # Show sample data
    print("\n📊 Sample data:")
    print(retail_df.head())
    
    return retail_df

if __name__ == "__main__":
    import numpy as np
    generate_and_save_retail_data()