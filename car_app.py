import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Car Price Prediction",
    page_icon="",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    h1 {color: #e74c3c; padding-bottom: 1rem;}
    </style>
    """, unsafe_allow_html=True)


# Load model
@st.cache_resource
def load_model():
    try:
        model = joblib.load('car_prediction_model.pkl')
        return model
    except FileNotFoundError:
        return None


# Header
st.title("Car Price Prediction System")
st.markdown("### Get Instant Valuation for Your Used Car")

# Load model
model = load_model()

if model is None:
    st.error("**Model file not found!**")
    st.info("""
    Please run the following command first:
    ```
    python car_price_prediction.py
    ```
    This will train and save the model.
    """)
    st.stop()

# Sidebar inputs
st.sidebar.title("Car Details")

st.sidebar.subheader("Basic Information")
year = st.sidebar.slider('Manufacturing Year', 2000, 2024, 2015)
present_price = st.sidebar.number_input('Current Ex-Showroom Price (Lakhs)', 0.0, 50.0, 5.0, 0.1)
kms_driven = st.sidebar.number_input('Kilometers Driven', 0, 500000, 50000, 1000)

st.sidebar.subheader("Car Specifications")
fuel_type = st.sidebar.selectbox('Fuel Type', ['Petrol', 'Diesel', 'CNG'])
seller_type = st.sidebar.selectbox('Seller Type', ['Dealer', 'Individual'])
transmission = st.sidebar.selectbox('Transmission', ['Manual', 'Automatic'])
owner = st.sidebar.selectbox('Number of Previous Owners', [0, 1, 2, 3])

# Calculate car age
current_year = 2024
car_age = current_year - year

# Predict button
st.sidebar.markdown("---")
predict_btn = st.sidebar.button("Get Price Estimate", type="primary", use_container_width=True)

# Main content
if predict_btn:
    # Encode categorical variables
    fuel_encoded = {'Petrol': 0, 'Diesel': 1, 'CNG': 2}[fuel_type]
    seller_encoded = {'Dealer': 0, 'Individual': 1}[seller_type]
    transmission_encoded = {'Manual': 0, 'Automatic': 1}[transmission]
    
    # Prepare input
    input_data = pd.DataFrame({
        'Year': [year],
        'Present_Price': [present_price],
        'Kms_Driven': [kms_driven],
        'Fuel_Type': [fuel_encoded],
        'Seller_Type': [seller_encoded],
        'Transmission': [transmission_encoded],
        'Owner': [owner]
    })
    
    # Make prediction
    predicted_price = model.predict(input_data)[0]
    
    # Calculate depreciation
    depreciation = present_price - predicted_price
    depreciation_percent = (depreciation / present_price) * 100 if present_price > 0 else 0
    
    # Display results
    st.markdown("---")
    st.header("Price Estimation Results")
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Estimated Selling Price",
            f"₹{predicted_price:.2f} Lakhs",
            delta=None
        )
    
    with col2:
        st.metric(
            "Current Showroom Price",
            f"₹{present_price:.2f} Lakhs",
            delta=None
        )
    
    with col3:
        st.metric(
            "Total Depreciation",
            f"₹{depreciation:.2f} Lakhs",
            delta=f"-{depreciation_percent:.1f}%"
        )
    
    # Gauge chart for price range
    st.markdown("---")
    st.subheader("Price Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Price range estimate (±10%)
        lower_estimate = predicted_price * 0.9
        upper_estimate = predicted_price * 1.1
        
        st.success(f"""
        **Expected Price Range:** ₹{lower_estimate:.2f}L - ₹{upper_estimate:.2f}L
        
        This is the typical market range for similar vehicles.
        """)
        
        # Price breakdown
        st.write("**Price Factors:**")
        
        factors = []
        
        if car_age <= 2:
            factors.append("Very new car - minimal depreciation")
        elif car_age <= 5:
            factors.append("Relatively new - good resale value")
        elif car_age <= 10:
            factors.append("Moderate age - average market value")
        else:
            factors.append("Older car - higher depreciation")
        
        if kms_driven < 30000:
            factors.append("Low mileage - adds value")
        elif kms_driven < 80000:
            factors.append("Average mileage")
        else:
            factors.append("High mileage - reduces value")
        
        if transmission == 'Automatic':
            factors.append("Automatic transmission - premium pricing")
        
        if fuel_type == 'Diesel':
            factors.append("Diesel - preferred for high usage")
        elif fuel_type == 'Petrol':
            factors.append("Petrol - standard option")
        
        if seller_type == 'Dealer':
            factors.append("Dealer - may offer better warranty")
        
        for factor in factors:
            st.markdown(f"- {factor}")
    
    with col2:
        # Gauge chart
        max_price = present_price * 1.2
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predicted_price,
            title={'text': "Estimated Price"},
            number={'prefix': "₹", 'suffix': "L"},
            gauge={
                'axis': {'range': [None, max_price]},
                'bar': {'color': "#e74c3c"},
                'steps': [
                    {'range': [0, present_price * 0.3], 'color': "lightgray"},
                    {'range': [present_price * 0.3, present_price * 0.7], 'color': "lightyellow"},
                    {'range': [present_price * 0.7, max_price], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "blue", 'width': 4},
                    'thickness': 0.75,
                    'value': present_price
                }
            }
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    # Car details summary
    st.markdown("---")
    st.subheader("Your Car Details")
    
    details_col1, details_col2 = st.columns(2)
    
    with details_col1:
        st.write(f"**Manufacturing Year:** {year}")
        st.write(f"**Car Age:** {car_age} years")
        st.write(f"**Kilometers Driven:** {kms_driven:,} km")
        st.write(f"**Fuel Type:** {fuel_type}")
    
    with details_col2:
        st.write(f"**Transmission:** {transmission}")
        st.write(f"**Seller Type:** {seller_type}")
        st.write(f"**Previous Owners:** {owner}")
        st.write(f"**Current Showroom Price:** ₹{present_price} Lakhs")
    
    # Tips for selling
    st.markdown("---")
    st.subheader("Tips to Get Better Price")
    
    
else:
    # Initial page
    st.markdown("---")
    st.info("Enter your car details in the sidebar and click **Get Price Estimate**")
    
    # Show example cars
    st.subheader("Example Valuations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Recent Car**")
        st.write("Year: 2020")
        st.write("Price: ₹8.5L")
        st.write("Kms: 20,000")
        st.write("Est: ₹6.5-7.5L")
    
    with col2:
        st.write("**Mid-range Car**")
        st.write("Year: 2015")
        st.write("Price: ₹6.0L")
        st.write("Kms: 50,000")
        st.write("Est: ₹3.5-4.5L")
    
    with col3:
        st.write("**Older Car**")
        st.write("Year: 2010")
        st.write("Price: ₹5.0L")
        st.write("Kms: 100,000")
        st.write("Est: ₹1.5-2.5L")
    
    st.markdown("---")
    
    # Model info
    st.subheader("Model Information")
    col1, col2, col3 = st.columns(3)
    col1.metric("Algorithm", "ML Regression")
    col2.metric("Accuracy", "~85%")
    col3.metric("Dataset", "300+ cars")

#  cd car-price-prediction-main
# python -m streamlit run car_app.py