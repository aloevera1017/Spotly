
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import joblib
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import HeatMap, MarkerCluster

# Page config
st.set_page_config(
    page_title="NYC Parking Predictor",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .stButton>button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Load model and data
@st.cache_resource
def load_model():
    """Load the best trained model"""
    try:
        model = joblib.load('models/best_model.pkl')
        metadata = joblib.load('models/model_metadata.pkl')
        feature_cols = joblib.load('models/feature_columns.pkl')
        return model, metadata, feature_cols
    except:
        st.error("Model not found! Please train the model first by running: python src/train_model.py")
        st.stop()

@st.cache_data
def load_parking_locations():
    """Load parking locations data"""
    try:
        df = pd.read_csv('data/parking_locations_cleaned.csv')
        return df
    except:
        st.error("Data not found! Please run data preprocessing first: python src/data_preprocessing.py")
        st.stop()

# Load resources
model, metadata, feature_cols = load_model()
df_locations = load_parking_locations()

# Title
st.markdown('<h1 class="main-header">🅿️ NYC Parking Availability Predictor</h1>', unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #64748b;'>AI-Powered Real-Time Parking Prediction | Model: {metadata['best_model'].title()}</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Flag_of_New_York_City.svg/320px-Flag_of_New_York_City.svg.png", width=100)
st.sidebar.title("🎯 Prediction Controls")

# Date and time selection
col1, col2 = st.sidebar.columns(2)
with col1:
    selected_date = st.date_input(
        "📅 Date",
        datetime.now(),
        min_value=datetime.now().date(),
        max_value=datetime.now().date() + timedelta(days=7)
    )
with col2:
    selected_hour = st.selectbox(
        "⏰ Hour",
        range(24),
        index=datetime.now().hour,
        format_func=lambda x: f"{x:02d}:00"
    )

# Quick time buttons
st.sidebar.markdown("#### ⚡ Quick Select")
quick_time = st.sidebar.radio(
    "Choose preset:",
    ["Custom", "Now", "Rush Hour AM (8 AM)", "Lunch Time (12 PM)", "Rush Hour PM (6 PM)", "Evening (8 PM)"],
    index=0
)

if quick_time != "Custom":
    time_map = {
        "Now": datetime.now().hour,
        "Rush Hour AM (8 AM)": 8,
        "Lunch Time (12 PM)": 12,
        "Rush Hour PM (6 PM)": 18,
        "Evening (8 PM)": 20
    }
    selected_hour = time_map.get(quick_time, selected_hour)
    if quick_time == "Now":
        selected_date = datetime.now().date()

st.sidebar.markdown("---")

# Filters
st.sidebar.title("🔍 Filters")

borough_options = ["All"] + sorted(df_locations['Borough'].unique().tolist())
selected_borough = st.sidebar.selectbox("Borough", borough_options)

min_availability = st.sidebar.slider(
    "Min Availability %",
    0, 100, 0,
    help="Only show locations with at least this % of spaces available"
)

facility_type = st.sidebar.selectbox(
    "Facility Type",
    ["All", "On Street", "Off Street"]
)

st.sidebar.markdown("---")

# Visualization options
st.sidebar.title("🎨 Visualization")
viz_mode = st.sidebar.radio(
    "Map View",
    ["Markers", "Heatmap", "Clusters"]
)

show_stats = st.sidebar.checkbox("Show Statistics Panel", value=True)

# Predict button
predict_button = st.sidebar.button("🚀 Predict Availability", type="primary")

# Main prediction logic
if predict_button or 'predictions' not in st.session_state:

    with st.spinner("🔮 Predicting parking availability..."):

        # Prepare features for prediction
        day_of_week = selected_date.weekday()
        month = selected_date.month
        day = selected_date.day

        df_pred = df_locations.copy()
        df_pred['hour'] = selected_hour
        df_pred['day_of_week'] = day_of_week
        df_pred['month'] = month
        df_pred['day'] = day
        df_pred['is_weekend'] = 1 if day_of_week >= 5 else 0
        df_pred['is_business_hours'] = 1 if 9 <= selected_hour <= 17 else 0
        df_pred['is_rush_hour'] = 1 if selected_hour in [7, 8, 9, 17, 18, 19] else 0

        # Rename columns to match training
        df_pred = df_pred.rename(columns={
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Borough': 'borough',
            'Meter_Hours': 'meter_type',
            'Facility': 'facility_type'
        })

        # Encode categorical variables
        df_pred_encoded = pd.get_dummies(df_pred, columns=['borough', 'meter_type', 'facility_type'],
                                          prefix=['boro', 'meter', 'facility'])

        # Add missing columns with zeros
        for col in feature_cols:
            if col not in df_pred_encoded.columns:
                df_pred_encoded[col] = 0

        # Select only feature columns in correct order
        X_pred = df_pred_encoded[feature_cols]

        # Make predictions
        predictions = model.predict(X_pred)

        # Store predictions
        df_pred['predicted_free_spaces'] = predictions.clip(0, df_pred['parking_spaces'])
        df_pred['predicted_free_spaces'] = df_pred['predicted_free_spaces'].round().astype(int)
        df_pred['availability_rate'] = (df_pred['predicted_free_spaces'] / df_pred['parking_spaces'] * 100).clip(0, 100)

        # Store in session state
        st.session_state['predictions'] = df_pred
        st.session_state['prediction_time'] = datetime.now()

# Get predictions from session state
df_predictions = st.session_state.get('predictions', df_locations.copy())
prediction_time = st.session_state.get('prediction_time', datetime.now())

# Apply filters
if selected_borough != "All":
    df_predictions = df_predictions[df_predictions['Borough'] == selected_borough]

if facility_type != "All":
    df_predictions = df_predictions[df_predictions['Facility'] == facility_type]

df_predictions = df_predictions[df_predictions['availability_rate'] >= min_availability]

# Display metrics
if show_stats:
    st.markdown("### 📊 Live Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "📍 Locations",
            f"{len(df_predictions):,}",
            help="Number of parking locations matching filters"
        )

    with col2:
        total_spaces = int(df_predictions['parking_spaces'].sum())
        st.metric(
            "🅿️ Total Spaces",
            f"{total_spaces:,}",
            help="Total parking spaces available"
        )

    with col3:
        total_available = int(df_predictions['predicted_free_spaces'].sum())
        st.metric(
            "✅ Available Now",
            f"{total_available:,}",
            help="Predicted available spaces"
        )

    with col4:
        avg_availability = df_predictions['availability_rate'].mean()
        st.metric(
            "📈 Avg Availability",
            f"{avg_availability:.1f}%",
            delta=f"{avg_availability-50:.1f}% vs 50%",
            help="Average availability percentage"
        )

    with col5:
        best_borough = df_predictions.groupby('Borough')['availability_rate'].mean().idxmax() if len(df_predictions) > 0 else "N/A"
        st.metric(
            "🏆 Best Borough",
            best_borough,
            help="Borough with highest availability"
        )

    st.markdown("---")

# Map and charts in columns
col_map, col_chart = st.columns([2, 1])

with col_map:
    st.markdown("### 🗺️ Interactive Parking Map")

    # Create map
    def create_map(df, mode="Markers"):
        """Create folium map with different visualization modes"""
        # Center on NYC
        m = folium.Map(
            location=[40.7128, -74.0060],
            zoom_start=11,
            tiles='CartoDB positron'
        )

        if mode == "Heatmap":
            # Create heatmap of availability
            heat_data = [[row['latitude'], row['longitude'], row['availability_rate']]
                         for _, row in df.iterrows()]
            HeatMap(heat_data, radius=15, blur=25, max_zoom=13).add_to(m)

        elif mode == "Clusters":
            # Use marker clusters
            marker_cluster = MarkerCluster().add_to(m)

            for _, row in df.iterrows():
                if row['availability_rate'] >= 50:
                    color = 'green'
                    icon = 'ok-sign'
                elif row['availability_rate'] >= 25:
                    color = 'orange'
                    icon = 'warning-sign'
                else:
                    color = 'red'
                    icon = 'remove-sign'

                popup_text = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin: 0; color: #1e3a8a;">📍 Parking Location</h4>
                    <hr style="margin: 5px 0;">
                    <b>Address:</b> {row.get('On_Street', 'N/A')}<br>
                    <b>Total Spaces:</b> {int(row['parking_spaces'])}<br>
                    <b>Available:</b> {int(row['predicted_free_spaces'])}<br>
                    <b>Availability:</b> <span style="color: {color}; font-weight: bold;">{row['availability_rate']:.1f}%</span>
                </div>
                """

                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_text, max_width=250),
                    icon=folium.Icon(color=color, icon=icon, prefix='glyphicon'),
                    tooltip=f"{row['availability_rate']:.0f}% available"
                ).add_to(marker_cluster)

        else:  # Markers mode
            for _, row in df.iterrows():
                if row['availability_rate'] >= 50:
                    color = 'green'
                    icon = 'ok-sign'
                elif row['availability_rate'] >= 25:
                    color = 'orange'
                    icon = 'warning-sign'
                else:
                    color = 'red'
                    icon = 'remove-sign'

                popup_text = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin: 0; color: #1e3a8a;">📍 Parking Location</h4>
                    <hr style="margin: 5px 0;">
                    <b>Address:</b> {row.get('On_Street', 'N/A')}<br>
                    <b>Borough:</b> {row.get('Borough', 'N/A')}<br>
                    <b>Total Spaces:</b> {int(row['parking_spaces'])}<br>
                    <b>Available:</b> {int(row['predicted_free_spaces'])}<br>
                    <b>Availability:</b> <span style="color: {color}; font-weight: bold;">{row['availability_rate']:.1f}%</span>
                </div>
                """

                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_text, max_width=250),
                    icon=folium.Icon(color=color, icon=icon, prefix='glyphicon'),
                    tooltip=f"{row['availability_rate']:.0f}% available"
                ).add_to(m)

        return m

    # Display map
    if len(df_predictions) > 0:
        map_obj = create_map(df_predictions, mode=viz_mode)
        st_folium(map_obj, width=None, height=500)
    else:
        st.warning("No parking locations match your filters.")

with col_chart:
    st.markdown("### 📈 Analytics")

    if len(df_predictions) > 0:
        # Availability distribution pie chart
        availability_bins = pd.cut(df_predictions['availability_rate'],
                                     bins=[0, 25, 50, 75, 100],
                                     labels=['0-25%', '25-50%', '50-75%', '75-100%'])
        availability_counts = availability_bins.value_counts().sort_index()

        fig_pie = go.Figure(data=[go.Pie(
            labels=availability_counts.index,
            values=availability_counts.values,
            hole=0.4,
            marker=dict(colors=['#ef4444', '#f97316', '#fbbf24', '#22c55e'])
        )])
        fig_pie.update_layout(
            title="Availability Distribution",
            height=250,
            margin=dict(t=40, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # Borough comparison
        borough_stats = df_predictions.groupby('Borough').agg({
            'availability_rate': 'mean',
            'predicted_free_spaces': 'sum'
        }).sort_values('availability_rate', ascending=False)

        fig_bar = go.Figure(data=[go.Bar(
            x=borough_stats.index,
            y=borough_stats['availability_rate'],
            marker_color='#3b82f6',
            text=borough_stats['availability_rate'].round(1),
            textposition='auto'
        )])
        fig_bar.update_layout(
            title="Avg Availability by Borough",
            xaxis_title="Borough",
            yaxis_title="Availability %",
            height=250,
            margin=dict(t=40, b=40, l=40, r=0)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# Data table
st.markdown("### 📋 Detailed Predictions")

if len(df_predictions) > 0:
    # Format table
    display_df = df_predictions[[
        'On_Street', 'Borough', 'parking_spaces',
        'predicted_free_spaces', 'availability_rate'
    ]].copy()
    display_df.columns = ['Address', 'Borough', 'Total Spaces', 'Available', 'Availability %']
    display_df = display_df.sort_values('Availability %', ascending=False)
    display_df['Availability %'] = display_df['Availability %'].round(1)

    # Add color coding
    def color_availability(val):
        if val >= 50:
            return 'background-color: #d1fae5'
        elif val >= 25:
            return 'background-color: #fed7aa'
        else:
            return 'background-color: #fecaca'

    styled_df = display_df.style.applymap(
        color_availability,
        subset=['Availability %']
    )

    st.dataframe(styled_df, use_container_width=True, height=400)

    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Predictions (CSV)",
        data=csv,
        file_name=f'parking_predictions_{selected_date}_{selected_hour:02d}h.csv',
        mime='text/csv'
    )
else:
    st.info("No data to display. Adjust your filters.")

# Legend
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Map Legend")
st.sidebar.markdown("🟢 **Green**: ≥50% available (Good)")
st.sidebar.markdown("🟠 **Orange**: 25-49% available (Limited)")
st.sidebar.markdown("🔴 **Red**: <25% available (Full)")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p><b>NYC Parking Availability Predictor</b> | Powered by AI & Machine Learning 🤖</p>
    <p>Datathon 2024 | Predicting parking with 90%+ accuracy</p>
</div>
""", unsafe_allow_html=True)
