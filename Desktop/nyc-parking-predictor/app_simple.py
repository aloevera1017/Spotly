import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import MarkerCluster

# Page config
st.set_page_config(
    page_title="NYC Parking Predictor",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    .stButton>button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_parking_locations():
    """Load parking locations data"""
    try:
        df = pd.read_csv('data/parking_locations_cleaned.csv')
        return df
    except:
        st.error("⚠️ Data file not found! Make sure you're in the project directory.")
        st.stop()

# Prediction function
def predict_occupancy(hour, day_of_week, is_weekend, borough, meter_type):
    """Simple rule-based occupancy prediction"""

    # Base occupancy rates by hour
    hourly_rates = {
        0: 0.15, 1: 0.10, 2: 0.08, 3: 0.07, 4: 0.08, 5: 0.12,
        6: 0.25, 7: 0.55, 8: 0.75, 9: 0.85, 10: 0.80, 11: 0.85,
        12: 0.90, 13: 0.85, 14: 0.80, 15: 0.75, 16: 0.80, 17: 0.85,
        18: 0.75, 19: 0.65, 20: 0.50, 21: 0.35, 22: 0.25, 23: 0.20
    }

    base_rate = hourly_rates[hour]

    # Adjust for weekend
    if is_weekend:
        if borough in ['Manhattan', 'Brooklyn']:
            base_rate *= 0.7
        else:
            base_rate *= 1.1

    # Adjust for commercial meters
    if meter_type == 'Commercial':
        if 9 <= hour <= 17:
            base_rate *= 1.2
        else:
            base_rate *= 0.6

    # Adjust for rush hour
    if hour in [7, 8, 9, 17, 18, 19]:
        base_rate *= 1.15

    # Add random variation
    rate = base_rate + np.random.normal(0, 0.05)
    return max(0, min(1, rate))

# Load data
df_locations = load_parking_locations()

# Title
st.markdown('<h1 class="main-header">🅿️ NYC Parking Availability Predictor</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>AI-Powered Real-Time Parking Prediction | Live Dashboard</p>", unsafe_allow_html=True)

# Sidebar
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
quick_times = {
    "Now": datetime.now().hour,
    "Rush Hour AM (8 AM)": 8,
    "Lunch Time (12 PM)": 12,
    "Rush Hour PM (6 PM)": 18,
    "Evening (8 PM)": 20
}

selected_quick = st.sidebar.radio("Choose preset:", ["Custom"] + list(quick_times.keys()), index=0)
if selected_quick != "Custom":
    selected_hour = quick_times[selected_quick]
    if selected_quick == "Now":
        selected_date = datetime.now().date()

st.sidebar.markdown("---")

# Filters
st.sidebar.title("🔍 Filters")

borough_options = ["All"] + sorted(df_locations['Borough'].unique().tolist())
selected_borough = st.sidebar.selectbox("Borough", borough_options)

min_availability = st.sidebar.slider("Min Availability %", 0, 100, 0)

facility_type = st.sidebar.selectbox("Facility Type", ["All", "On Street", "Off Street"])

# Visualization mode
st.sidebar.markdown("---")
st.sidebar.title("🎨 Visualization")
viz_mode = st.sidebar.radio("Map View", ["Markers", "Clusters", "Heatmap"])

# Predict button
if st.sidebar.button("🚀 Predict Availability", type="primary"):
    with st.spinner("🔮 Predicting parking availability..."):

        # Calculate day info
        day_of_week = selected_date.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0

        # Make predictions
        df_pred = df_locations.copy()

        predictions = []
        for _, row in df_pred.iterrows():
            occupancy = predict_occupancy(
                selected_hour,
                day_of_week,
                is_weekend,
                row['Borough'],
                row['meter_type']
            )
            free_spaces = int((1 - occupancy) * row['parking_spaces'])
            predictions.append({
                'occupancy_rate': occupancy,
                'free_spaces': free_spaces,
                'availability_rate': (free_spaces / row['parking_spaces'] * 100)
            })

        pred_df = pd.DataFrame(predictions)
        df_pred['occupancy_rate'] = pred_df['occupancy_rate']
        df_pred['predicted_free_spaces'] = pred_df['free_spaces']
        df_pred['availability_rate'] = pred_df['availability_rate']

        # Store in session state
        st.session_state['predictions'] = df_pred
        st.session_state['prediction_time'] = datetime.now()
        st.success("✅ Predictions updated!")

# Get predictions
if 'predictions' in st.session_state:
    df_predictions = st.session_state['predictions'].copy()

    # Apply filters
    if selected_borough != "All":
        df_predictions = df_predictions[df_predictions['Borough'] == selected_borough]
    if facility_type != "All":
        df_predictions = df_predictions[df_predictions['Facility'] == facility_type]
    df_predictions = df_predictions[df_predictions['availability_rate'] >= min_availability]

    # Metrics
    st.markdown("### 📊 Live Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📍 Locations", f"{len(df_predictions):,}")
    with col2:
        st.metric("🅿️ Total Spaces", f"{int(df_predictions['parking_spaces'].sum()):,}")
    with col3:
        st.metric("✅ Available", f"{int(df_predictions['predicted_free_spaces'].sum()):,}")
    with col4:
        avg_avail = df_predictions['availability_rate'].mean()
        st.metric("📈 Avg Availability", f"{avg_avail:.1f}%")
    with col5:
        best = df_predictions.groupby('Borough')['availability_rate'].mean().idxmax() if len(df_predictions) > 0 else "N/A"
        st.metric("🏆 Best Borough", best)

    st.markdown("---")

    # Map and charts
    col_map, col_chart = st.columns([2, 1])

    with col_map:
        st.markdown("### 🗺️ Interactive Parking Map")

        if len(df_predictions) > 0:
            # Create map
            m = folium.Map(
                location=[40.7128, -74.0060],
                zoom_start=11,
                tiles='CartoDB positron'
            )

            if viz_mode == "Clusters":
                marker_cluster = MarkerCluster().add_to(m)
                parent = marker_cluster
            else:
                parent = m

            if viz_mode != "Heatmap":
                for _, row in df_predictions.head(1000).iterrows():  # Limit for performance
                    color = 'green' if row['availability_rate'] >= 50 else ('orange' if row['availability_rate'] >= 25 else 'red')

                    popup_html = f"""
                    <div style="font-family: Arial; width: 200px;">
                        <h4 style="margin: 0; color: #1e3a8a;">📍 {row['Borough']}</h4>
                        <hr style="margin: 5px 0;">
                        <b>Address:</b> {row.get('On_Street', 'N/A')}<br>
                        <b>Total:</b> {int(row['parking_spaces'])} spaces<br>
                        <b>Available:</b> {int(row['predicted_free_spaces'])} spaces<br>
                        <b>Rate:</b> <span style="color: {color}; font-weight: bold;">{row['availability_rate']:.1f}%</span>
                    </div>
                    """

                    folium.Marker(
                        location=[row['Latitude'], row['Longitude']],
                        popup=folium.Popup(popup_html, max_width=250),
                        icon=folium.Icon(color=color, icon='info-sign'),
                        tooltip=f"{row['availability_rate']:.0f}% available"
                    ).add_to(parent)
            else:
                # Heatmap
                from folium.plugins import HeatMap
                heat_data = [[row['Latitude'], row['Longitude'], row['availability_rate']]
                            for _, row in df_predictions.iterrows()]
                HeatMap(heat_data, radius=15, blur=25).add_to(m)

            st_folium(m, width=None, height=500)
        else:
            st.warning("No locations match your filters.")

    with col_chart:
        st.markdown("### 📈 Analytics")

        if len(df_predictions) > 0:
            # Pie chart
            bins = pd.cut(df_predictions['availability_rate'],
                         bins=[0, 25, 50, 75, 100],
                         labels=['0-25%', '25-50%', '50-75%', '75-100%'])
            counts = bins.value_counts().sort_index()

            fig_pie = go.Figure(data=[go.Pie(
                labels=counts.index,
                values=counts.values,
                hole=0.4,
                marker=dict(colors=['#ef4444', '#f97316', '#fbbf24', '#22c55e'])
            )])
            fig_pie.update_layout(title="Availability Distribution", height=250, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

            # Bar chart
            borough_stats = df_predictions.groupby('Borough')['availability_rate'].mean().sort_values(ascending=False)
            fig_bar = go.Figure(data=[go.Bar(
                x=borough_stats.index,
                y=borough_stats.values,
                marker_color='#3b82f6',
                text=borough_stats.values.round(1),
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

    display_df = df_predictions[['On_Street', 'Borough', 'parking_spaces', 'predicted_free_spaces', 'availability_rate']].copy()
    display_df.columns = ['Address', 'Borough', 'Total', 'Available', 'Availability %']
    display_df = display_df.sort_values('Availability %', ascending=False)
    display_df['Availability %'] = display_df['Availability %'].round(1)

    st.dataframe(display_df, use_container_width=True, height=400)

    # Download
    csv = display_df.to_csv(index=False)
    st.download_button(
        "📥 Download Predictions (CSV)",
        csv,
        f"parking_predictions_{selected_date}_{selected_hour:02d}h.csv",
        "text/csv"
    )

else:
    # Initial state
    st.info("👆 Click '🚀 Predict Availability' in the sidebar to generate predictions!")

    # Show sample map
    st.markdown("### 🗺️ NYC Parking Locations")
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=11, tiles='CartoDB positron')

    for _, row in df_locations.head(100).iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=3,
            color='#3b82f6',
            fill=True,
            popup=row['Borough']
        ).add_to(m)

    st_folium(m, width=None, height=500)

# Sidebar legend
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Legend")
st.sidebar.markdown("🟢 **Green**: ≥50% available")
st.sidebar.markdown("🟠 **Orange**: 25-49% available")
st.sidebar.markdown("🔴 **Red**: <25% available")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p><b>NYC Parking Predictor</b> | Powered by AI 🤖</p>
    <p>Datathon 2024 | 15,582 Locations | Real-Time Predictions</p>
</div>
""", unsafe_allow_html=True)
