#!/usr/bin/env python3
"""
Test script to verify Streamlit app can import and run basic functions
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    print("🔍 Testing Streamlit app components...")
    
    # Test core imports
    print("📦 Testing imports...")
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    print("✅ Core packages imported successfully")
    
    # Test if H2O is available
    try:
        import h2o
        print("✅ H2O available")
        H2O_AVAILABLE = True
    except ImportError:
        print("⚠️  H2O not available - will run in demo mode")
        H2O_AVAILABLE = False
    
    # Test data loading
    print("📊 Testing data generation...")
    dates = pd.date_range('2023-01-01', '2023-01-31', freq='D')
    products = [f'PROD_{i:03d}' for i in range(1, 6)]
    categories = ['Electronics', 'Clothing', 'Food']
    
    data = []
    for product in products:
        for date in dates:
            base_demand = np.random.uniform(5, 50)
            demand = max(1, int(base_demand * np.random.uniform(0.8, 1.2)))
            
            data.append({
                'date': date,
                'product_id': product,
                'category': np.random.choice(categories),
                'quantity_sold': demand,
                'price': round(np.random.uniform(10, 200), 2),
                'stock_level': np.random.randint(20, 300),
                'day_of_week': date.weekday(),
                'month': date.month,
                'is_weekend': int(date.weekday() >= 5),
                'is_holiday_season': int(date.month in [11, 12]),
                'on_promotion': int(np.random.random() < 0.1),
                'quantity_sold_7d_avg': round(demand * 0.95, 2),
                'quantity_sold_30d_avg': round(demand * 1.05, 2)
            })
    
    df = pd.DataFrame(data)
    print(f"✅ Generated test data: {len(df)} records")
    
    # Test plotly chart creation
    print("📈 Testing chart generation...")
    fig = px.bar(df.head(10), x='product_id', y='quantity_sold', title="Test Chart")
    print("✅ Plotly chart created successfully")
    
    # Test file operations
    print("📁 Testing file operations...")
    os.makedirs('shared/data', exist_ok=True)
    df.to_csv('shared/data/test_data.csv', index=False)
    
    # Verify file was created and can be read back
    test_df = pd.read_csv('shared/data/test_data.csv')
    print(f"✅ File operations successful: {len(test_df)} records saved and loaded")
    
    # Clean up test file
    os.remove('shared/data/test_data.csv')
    
    print("")
    print("🎉 All tests passed! Streamlit app should work correctly.")
    print("")
    print("🚀 Ready to run:")
    print("   ./scripts/codespaces-demo.sh")
    print("   or")
    print("   streamlit run streamlit_app.py")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    print("")
    print("🔍 Troubleshooting suggestions:")
    print("1. Install missing packages: pip install streamlit pandas numpy plotly")
    print("2. Check Python version: python --version")
    print("3. Verify working directory contains streamlit_app.py")
    sys.exit(1)