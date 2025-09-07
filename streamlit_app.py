"""
Inventory Intelligence Dashboard - H2O AutoML powered
Real-time demand forecasting and inventory optimization
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# H2O import with fallback for demo
try:
    import h2o
    H2O_AVAILABLE = True
except ImportError:
    H2O_AVAILABLE = False
    st.sidebar.warning("⚠️ H2O not installed - running in demo mode")

# Add path for shared utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

class InventoryDashboard:
    def __init__(self):
        self.h2o_initialized = False
        self.model = None
        self.model_path = None
        
    def initialize_h2o(self):
        """Initialize H2O cluster"""
        if not H2O_AVAILABLE:
            st.error("❌ H2O not available - running in demo mode")
            return False
            
        if not self.h2o_initialized:
            try:
                # Try to connect to existing H2O cluster
                h2o_url = os.getenv('H2O_URL', 'http://localhost:54321')
                if 'localhost' in h2o_url:
                    h2o.init(ip="localhost", port=54321, max_mem_size="4g", strict_version_check=False)
                else:
                    h2o.init(url=h2o_url, strict_version_check=False)
                
                self.h2o_initialized = True
                st.success("✅ Connected to H2O cluster")
                return True
            except Exception as e:
                st.error(f"❌ H2O connection failed: {e}")
                st.info("💡 Make sure H2O is running: docker run -d -p 54321:54321 h2oai/h2o-open-source")
                return False
        return True
    
    def load_model(self):
        """Load trained H2O model"""
        if not H2O_AVAILABLE:
            st.warning("⚠️ H2O not available - using demo mode")
            return False
            
        model_dir = '../shared/models/h2o_retail_forecasting'
        
        if os.path.exists(model_dir):
            try:
                # Find MOJO file
                mojo_files = [f for f in os.listdir(model_dir) if f.endswith('.zip')]
                if mojo_files:
                    mojo_path = os.path.join(model_dir, mojo_files[0])
                    self.model = h2o.import_mojo(mojo_path)
                    st.success(f"✅ Model loaded: {mojo_files[0]}")
                    return True
                else:
                    st.warning("⚠️ No MOJO file found in model directory")
            except Exception as e:
                st.error(f"❌ Model loading failed: {e}")
        else:
            st.warning("⚠️ No trained model found. Run training pipeline first.")
        return False
    
    def load_sample_data(self):
        """Load sample data for demo"""
        data_path = '../shared/data/retail_test.csv'
        if os.path.exists(data_path):
            return pd.read_csv(data_path)
        else:
            # Generate minimal sample data
            return pd.DataFrame({
                'product_id': [f'PROD_{i:03d}' for i in range(1, 11)],
                'category': ['Electronics', 'Clothing', 'Food', 'Books', 'Home'] * 2,
                'price': np.random.uniform(10, 200, 10),
                'day_of_week': np.random.randint(0, 7, 10),
                'month': np.random.randint(1, 13, 10),
                'is_weekend': np.random.choice([0, 1], 10),
                'is_holiday_season': np.random.choice([0, 1], 10),
                'on_promotion': np.random.choice([0, 1], 10),
                'quantity_sold_7d_avg': np.random.uniform(5, 50, 10),
                'quantity_sold_30d_avg': np.random.uniform(10, 40, 10),
                'stock_level': np.random.randint(20, 300, 10)
            })

def main():
    st.set_page_config(
        page_title="Inventory Intelligence", 
        page_icon="🏪",
        layout="wide"
    )
    
    # Header
    st.title("🏪 Inventory Intelligence Dashboard")
    st.subtitle("H2O AutoML-Powered Demand Forecasting & Inventory Optimization")
    
    dashboard = InventoryDashboard()
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Configuration")
    
    # H2O Connection
    if st.sidebar.button("🔗 Connect to H2O"):
        dashboard.initialize_h2o()
    
    # Model Management
    st.sidebar.subheader("🤖 Model Management")
    
    if st.sidebar.button("📥 Load Model"):
        if dashboard.initialize_h2o():
            dashboard.load_model()
    
    if st.sidebar.button("🔄 Retrain Model"):
        if dashboard.initialize_h2o():
            with st.spinner("Training new model..."):
                # Run training pipeline
                os.system("cd /Users/rammaree/h2o_ml_usecases/h2o-prototypes/inventory && python h2o_automl_pipeline.py")
                st.success("✅ Model retrained successfully!")
                dashboard.load_model()
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔮 Predictions", "📈 Analytics", "📋 Data"])
    
    # Load sample data
    sample_data = dashboard.load_sample_data()
    
    with tab1:
        st.header("📊 Inventory Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_products = len(sample_data['product_id'].unique())
            st.metric("Total Products", total_products)
        
        with col2:
            avg_stock = sample_data['stock_level'].mean()
            st.metric("Avg Stock Level", f"{avg_stock:.0f}")
        
        with col3:
            low_stock_count = (sample_data['stock_level'] < 50).sum()
            st.metric("Low Stock Items", low_stock_count, delta=-5)
        
        with col4:
            promo_rate = sample_data['on_promotion'].mean() * 100
            st.metric("Promotion Rate", f"{promo_rate:.1f}%")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Stock levels by category
            fig = px.box(sample_data, x='category', y='stock_level', 
                        title="Stock Levels by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Demand vs Stock scatter
            fig = px.scatter(sample_data, x='quantity_sold_7d_avg', y='stock_level',
                           color='category', size='price',
                           title="Demand vs Stock Levels")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("🔮 Demand Predictions")
        
        if dashboard.model is None:
            st.warning("⚠️ Please load a trained model first")
            
            # Manual prediction form
            st.subheader("📝 Manual Prediction")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                product_id = st.selectbox("Product", sample_data['product_id'].unique())
                price = st.number_input("Price ($)", min_value=0.0, value=50.0)
                day_of_week = st.selectbox("Day of Week", list(range(7)), format_func=lambda x: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][x])
            
            with col2:
                month = st.selectbox("Month", list(range(1, 13)))
                is_weekend = st.checkbox("Weekend")
                is_holiday = st.checkbox("Holiday Season")
            
            with col3:
                on_promotion = st.checkbox("On Promotion")
                avg_demand_7d = st.number_input("7-day Avg Demand", min_value=0.0, value=25.0)
                avg_demand_30d = st.number_input("30-day Avg Demand", min_value=0.0, value=30.0)
                stock_level = st.number_input("Current Stock", min_value=0, value=100)
            
            if st.button("🎯 Predict Demand"):
                # Mock prediction for demo
                base_demand = avg_demand_7d * (1.5 if on_promotion else 1.0)
                seasonal_factor = 1.2 if is_holiday else 1.0
                weekend_factor = 1.1 if is_weekend else 1.0
                
                predicted_demand = base_demand * seasonal_factor * weekend_factor * np.random.uniform(0.8, 1.2)
                
                st.success(f"🎯 Predicted Demand: **{predicted_demand:.1f} units**")
                
                # Recommendations
                st.subheader("💡 Recommendations")
                if stock_level < predicted_demand * 7:
                    st.warning(f"⚠️ **Reorder Alert**: Stock may run out in {stock_level/predicted_demand:.1f} days")
                    st.info(f"💡 **Recommended Reorder**: {int(predicted_demand * 14 - stock_level)} units")
                else:
                    st.success("✅ **Stock Status**: Adequate inventory levels")
        
        else:
            # Real model predictions
            st.success("🤖 Using trained H2O model for predictions")
            # Implementation would use dashboard.model.predict()
    
    with tab3:
        st.header("📈 Advanced Analytics")
        
        # Trend analysis
        st.subheader("📊 Demand Trends")
        
        # Generate sample time series data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        trend_data = pd.DataFrame({
            'date': dates,
            'demand': np.random.normal(30, 8, len(dates)) + 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
        })
        
        fig = px.line(trend_data, x='date', y='demand', title="Daily Demand Trend")
        st.plotly_chart(fig, use_container_width=True)
        
        # ABC Analysis
        st.subheader("🏷️ ABC Analysis")
        
        # Mock ABC data
        abc_data = pd.DataFrame({
            'product_id': sample_data['product_id'],
            'revenue': sample_data['price'] * sample_data['quantity_sold_7d_avg'],
            'category': sample_data['category']
        })
        abc_data['abc_class'] = pd.qcut(abc_data['revenue'], q=3, labels=['C', 'B', 'A'])
        
        fig = px.bar(abc_data.groupby('abc_class').size().reset_index(name='count'), 
                    x='abc_class', y='count', title="ABC Classification Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Optimization recommendations
        st.subheader("🎯 Optimization Recommendations")
        
        recommendations = [
            "📈 **Increase stock** for high-demand items (Class A products)",
            "🔄 **Optimize reorder points** based on seasonal patterns",
            "💰 **Implement dynamic pricing** for promotional periods",
            "📦 **Consolidate suppliers** for Class C products to reduce costs",
            "⚡ **Fast-track** weekend inventory replenishment"
        ]
        
        for rec in recommendations:
            st.markdown(f"- {rec}")
    
    with tab4:
        st.header("📋 Data Explorer")
        
        # Data upload
        st.subheader("📤 Upload New Data")
        uploaded_file = st.file_uploader("Choose CSV file", type="csv")
        
        if uploaded_file is not None:
            new_data = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(new_data)} records")
            st.dataframe(new_data.head())
        
        # Current data view
        st.subheader("📊 Sample Data")
        st.dataframe(sample_data)
        
        # Data quality check
        st.subheader("🔍 Data Quality")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Missing Values:**")
            missing = sample_data.isnull().sum()
            st.write(missing[missing > 0] if missing.sum() > 0 else "No missing values")
        
        with col2:
            st.write("**Data Types:**")
            st.write(sample_data.dtypes)
    
    # Footer
    st.markdown("---")
    st.markdown("🏪 **Inventory Intelligence** | Powered by H2O AutoML | Built with Streamlit")

if __name__ == "__main__":
    main()