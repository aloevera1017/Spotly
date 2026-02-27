import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Page config
st.set_page_config(
 page_title="Spotly - Find Your Perfect Spot",
 page_icon="",
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
 .search-box {
 padding: 1rem;
 background-color: #f0f9ff;
 border-radius: 0.5rem;
 border: 2px solid #3b82f6;
 margin-bottom: 1rem;
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
 st.error(" Data file not found! Make sure you're in the project directory.")
 st.stop()

# Expand parking lots into individual spaces
@st.cache_data
def expand_to_individual_spaces(df, max_spaces_per_location=50):
 """Create individual parking space records"""
 individual_spaces = []

 for idx, row in df.iterrows():
 num_spaces = min(int(row['parking_spaces']), max_spaces_per_location)

 for space_num in range(1, num_spaces + 1):
 # Add small offset to coordinates for visualization
 lat_offset = np.random.uniform(-0.0001, 0.0001)
 lon_offset = np.random.uniform(-0.0001, 0.0001)

 individual_spaces.append({
 'location_id': row['ObjectID'],
 'space_id': f"{row['ObjectID']}-{space_num}",
 'space_number': space_num,
 'Latitude': row['Latitude'] + lat_offset,
 'Longitude': row['Longitude'] + lon_offset,
 'Latitude_original': row['Latitude'],
 'Longitude_original': row['Longitude'],
 'Borough': row['Borough'],
 'On_Street': row['On_Street'],
 'From_Street': row.get('From_Street', ''),
 'To_Street': row.get('To_Street', ''),
 'Facility': row['Facility'],
 'meter_type': row['meter_type'],
 'total_spaces_at_location': row['parking_spaces']
 })

 return pd.DataFrame(individual_spaces)

# Geocoding function
@st.cache_data
def geocode_address(address):
 """Convert address to coordinates"""
 try:
 geolocator = Nominatim(user_agent="spotly_nyc_parking")
 location = geolocator.geocode(f"{address}, New York City, NY")
 if location:
 return location.latitude, location.longitude
 return None
 except:
 return None

# Find nearby parking
def find_nearby_parking(df, center_lat, center_lon, radius_km=1.0):
 """Find parking within radius of a point"""
 df['distance_km'] = df.apply(
 lambda row: geodesic(
 (center_lat, center_lon),
 (row['Latitude_original'], row['Longitude_original'])
 ).km,
 axis=1
 )
 return df[df['distance_km'] <= radius_km].sort_values('distance_km')

# Prediction function
def predict_individual_space_occupancy(hour, day_of_week, is_weekend, borough, meter_type):
 """Predict if individual space is occupied (0 or 1)"""

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

 # Clamp between 0 and 1
 occupancy_prob = max(0, min(1, base_rate))

 # Random decision for this individual space
 is_occupied = np.random.random() < occupancy_prob

 return is_occupied, occupancy_prob

# Load data
df_locations = load_parking_locations()

# Title
st.markdown('<h1 class="main-header">Spotly - Find Your Perfect Spot</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Find Available Parking Spaces | Real-Time Individual Space Tracking</p>", unsafe_allow_html=True)

# Address Search Bar (Top of page)
st.markdown("---")
st.markdown("### Find Parking Near You")

col_search1, col_search2, col_search3 = st.columns([3, 1, 1])

with col_search1:
 search_address = st.text_input(
 "Enter an address or landmark",
 placeholder="e.g., Times Square, 350 5th Ave, Central Park",
 label_visibility="collapsed"
 )

with col_search2:
 search_radius = st.selectbox(
 "Radius",
 [0.5, 1.0, 2.0, 5.0],
 index=1,
 format_func=lambda x: f"{x} km"
 )

with col_search3:
 search_button = st.button(" Search", type="primary", use_container_width=True)

# Initialize session state
if 'search_location' not in st.session_state:
 st.session_state['search_location'] = None
if 'search_active' not in st.session_state:
 st.session_state['search_active'] = False

# Handle search
if search_button and search_address:
 with st.spinner(f" Searching for '{search_address}'..."):
 coords = geocode_address(search_address)
 if coords:
 st.session_state['search_location'] = coords
 st.session_state['search_active'] = True
 st.success(f" Found! Showing parking near {search_address}")
 else:
 st.error(" Address not found. Try a different address or NYC landmark.")
 st.session_state['search_active'] = False

st.markdown("---")

# Sidebar
st.sidebar.title(" Prediction Controls")

# Date and time selection
col1, col2 = st.sidebar.columns(2)
with col1:
 selected_date = st.date_input(
 " Date",
 datetime.now(),
 min_value=datetime.now().date(),
 max_value=datetime.now().date() + timedelta(days=7)
 )
with col2:
 selected_hour = st.selectbox(
 "Hour",
 range(24),
 index=datetime.now().hour,
 format_func=lambda x: f"{x:02d}:00"
 )

# Quick time buttons
st.sidebar.markdown("#### Quick Select")
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
st.sidebar.title(" Filters")

if not st.session_state['search_active']:
 borough_options = ["All"] + sorted(df_locations['Borough'].unique().tolist())
 selected_borough = st.sidebar.selectbox("Borough", borough_options)
else:
 st.sidebar.info(f" Searching near: {search_address}")
 selected_borough = "All"

show_only_available = st.sidebar.checkbox("Show Only Available Spaces", value=False)

facility_type = st.sidebar.selectbox("Facility Type", ["All", "On Street", "Off Street"])

# Display options
st.sidebar.markdown("---")
st.sidebar.title(" Display")
max_spaces_display = st.sidebar.slider("Max Spaces to Show", 100, 5000, 1000, step=100)

# Predict button
if st.sidebar.button(" Predict Availability", type="primary"):
 with st.spinner(" Analyzing individual parking spaces..."):

 # Calculate day info
 day_of_week = selected_date.weekday()
 is_weekend = 1 if day_of_week >= 5 else 0

 # Apply search filter if active
 if st.session_state['search_active'] and st.session_state['search_location']:
 search_lat, search_lon = st.session_state['search_location']
 df_filtered = df_locations.copy()
 df_filtered['distance_km'] = df_filtered.apply(
 lambda row: geodesic(
 (search_lat, search_lon),
 (row['Latitude'], row['Longitude'])
 ).km,
 axis=1
 )
 df_filtered = df_filtered[df_filtered['distance_km'] <= search_radius].sort_values('distance_km')
 else:
 df_filtered = df_locations.copy()
 if selected_borough != "All":
 df_filtered = df_filtered[df_filtered['Borough'] == selected_borough]

 if facility_type != "All":
 df_filtered = df_filtered[df_filtered['Facility'] == facility_type]

 # Expand to individual spaces
 df_spaces = expand_to_individual_spaces(df_filtered, max_spaces_per_location=50)

 # Predict each space
 predictions = []
 for _, space in df_spaces.iterrows():
 is_occupied, prob = predict_individual_space_occupancy(
 selected_hour,
 day_of_week,
 is_weekend,
 space['Borough'],
 space['meter_type']
 )
 predictions.append({
 'is_occupied': is_occupied,
 'occupancy_probability': prob,
 'status': 'Occupied' if is_occupied else 'Available'
 })

 pred_df = pd.DataFrame(predictions)
 df_spaces['is_occupied'] = pred_df['is_occupied']
 df_spaces['occupancy_probability'] = pred_df['occupancy_probability']
 df_spaces['status'] = pred_df['status']

 # Limit display
 df_spaces = df_spaces.head(max_spaces_display)

 # Store in session state
 st.session_state['space_predictions'] = df_spaces
 st.session_state['prediction_time'] = datetime.now()
 st.success(f" Analyzed {len(df_spaces)} individual parking spaces!")

# Display predictions
if 'space_predictions' in st.session_state:
 df_spaces = st.session_state['space_predictions'].copy()

 # Apply availability filter
 if show_only_available:
 df_spaces = df_spaces[df_spaces['status'] == 'Available']

 # Metrics
 st.markdown("### Individual Space Statistics")
 col1, col2, col3, col4, col5 = st.columns(5)

 total_spaces = len(df_spaces)
 available_spaces = len(df_spaces[df_spaces['status'] == 'Available'])
 occupied_spaces = len(df_spaces[df_spaces['status'] == 'Occupied'])
 availability_rate = (available_spaces / total_spaces * 100) if total_spaces > 0 else 0

 with col1:
 st.metric(" Total Spaces", f"{total_spaces:,}")
 with col2:
 st.metric(" Available", f"{available_spaces:,}", delta=f"{availability_rate:.1f}%")
 with col3:
 st.metric(" Occupied", f"{occupied_spaces:,}")
 with col4:
 unique_locations = df_spaces['location_id'].nunique()
 st.metric(" Locations", f"{unique_locations:,}")
 with col5:
 if st.session_state['search_active']:
 avg_dist = df_spaces['distance_km'].mean()
 st.metric(" Avg Distance", f"{avg_dist:.2f} km")
 else:
 st.metric(" Best Rate", f"{availability_rate:.1f}%")

 st.markdown("---")

 # Map and list
 col_map, col_list = st.columns([2, 1])

 with col_map:
 st.markdown("### Individual Parking Spaces Map")

 if len(df_spaces) > 0:
 # Determine map center
 if st.session_state['search_active'] and st.session_state['search_location']:
 map_center = st.session_state['search_location']
 zoom = 15
 else:
 map_center = [df_spaces['Latitude_original'].mean(), df_spaces['Longitude_original'].mean()]
 zoom = 12

 # Create map
 m = folium.Map(
 location=map_center,
 zoom_start=zoom,
 tiles='CartoDB positron'
 )

 # Add search location marker if active
 if st.session_state['search_active'] and st.session_state['search_location']:
 folium.Marker(
 location=st.session_state['search_location'],
 popup=f" Search Location: {search_address}",
 icon=folium.Icon(color='blue', icon='star', prefix='fa'),
 tooltip="Your search location"
 ).add_to(m)

 # Add radius circle
 folium.Circle(
 location=st.session_state['search_location'],
 radius=search_radius * 1000, # km to meters
 color='blue',
 fill=True,
 fillOpacity=0.1,
 popup=f"{search_radius} km radius"
 ).add_to(m)

 # Group spaces by location for better visualization
 location_groups = df_spaces.groupby(['Latitude_original', 'Longitude_original', 'On_Street', 'Borough'])

 for (lat, lon, street, borough), group in location_groups:
 available = len(group[group['status'] == 'Available'])
 total = len(group)
 rate = available / total * 100

 # Color based on availability rate
 if rate >= 50:
 color = 'green'
 icon = 'ok-sign'
 elif rate >= 25:
 color = 'orange'
 icon = 'warning-sign'
 else:
 color = 'red'
 icon = 'remove-sign'

 # Create detailed popup
 space_list = "<br>".join([
 f"Space #{int(row['space_number'])}: <b style='color: {'green' if row['status']=='Available' else 'red'};'>{row['status']}</b>"
 for _, row in group.head(10).iterrows()
 ])

 if len(group) > 10:
 space_list += f"<br>... and {len(group)-10} more spaces"

 popup_html = f"""
 <div style="font-family: Arial; width: 250px;">
 <h4 style="margin: 0; color: #1e3a8a;"> {street or 'Parking Location'}</h4>
 <p style="margin: 5px 0; color: #64748b;">{borough}</p>
 <hr style="margin: 5px 0;">
 <p><b>Total Spaces:</b> {total}</p>
 <p><b>Available:</b> <span style="color: green; font-weight: bold;">{available}</span></p>
 <p><b>Occupied:</b> <span style="color: red; font-weight: bold;">{total - available}</span></p>
 <p><b>Availability:</b> <span style="color: {color}; font-weight: bold;">{rate:.1f}%</span></p>
 <hr style="margin: 5px 0;">
 <p style="font-size: 0.9em;"><b>Individual Spaces:</b></p>
 <p style="font-size: 0.85em; max-height: 150px; overflow-y: auto;">{space_list}</p>
 </div>
 """

 folium.Marker(
 location=[lat, lon],
 popup=folium.Popup(popup_html, max_width=300),
 icon=folium.Icon(color=color, icon=icon, prefix='glyphicon'),
 tooltip=f"{available}/{total} spaces available ({rate:.0f}%)"
 ).add_to(m)

 st_folium(m, width=None, height=600)
 else:
 st.warning("No spaces found matching your criteria.")

 with col_list:
 st.markdown("### Space Details")

 # Group by location
 location_summary = df_spaces.groupby(['On_Street', 'Borough', 'Latitude_original', 'Longitude_original']).agg({
 'space_id': 'count',
 'status': lambda x: (x == 'Available').sum()
 }).reset_index()
 location_summary.columns = ['Address', 'Borough', 'Lat', 'Lon', 'Total', 'Available']
 location_summary['Availability %'] = (location_summary['Available'] / location_summary['Total'] * 100).round(1)
 location_summary = location_summary.sort_values('Availability %', ascending=False)

 # Display as expandable sections
 for idx, row in location_summary.head(20).iterrows():
 availability_text = "Available" if row['Availability %'] >= 50 else ("Limited" if row['Availability %'] >= 25 else "Full")
 with st.expander(f"[{availability_text}] {row['Address'][:30]}... - {row['Available']}/{row['Total']} spaces"):
 st.write(f"**Borough:** {row['Borough']}")
 st.write(f"**Total Spaces:** {row['Total']}")
 st.write(f"**Available:** {row['Available']}")
 st.write(f"**Availability:** {row['Availability %']}%")

 if st.session_state['search_active']:
 dist = geodesic(
 st.session_state['search_location'],
 (row['Lat'], row['Lon'])
 ).km
 st.write(f"**Distance:** {dist:.2f} km")

 # Show individual spaces
 spaces_at_location = df_spaces[
 (df_spaces['Latitude_original'] == row['Lat']) &
 (df_spaces['Longitude_original'] == row['Lon'])
 ]
 for _, space in spaces_at_location.iterrows():
 status_icon = "" if space['status'] == 'Available' else ""
 st.text(f" {status_icon} Space #{int(space['space_number'])}: {space['status']}")

 # Detailed table
 st.markdown("### All Individual Spaces")

 display_df = df_spaces[['space_id', 'space_number', 'On_Street', 'Borough', 'status', 'occupancy_probability']].copy()
 display_df.columns = ['Space ID', 'Space #', 'Address', 'Borough', 'Status', 'Occupancy Prob']
 display_df['Occupancy Prob'] = (display_df['Occupancy Prob'] * 100).round(1).astype(str) + '%'
 display_df = display_df.sort_values('Status')

 st.dataframe(display_df, use_container_width=True, height=300)

 # Download
 csv = display_df.to_csv(index=False)
 st.download_button(
 " Download Space List (CSV)",
 csv,
 f"individual_spaces_{selected_date}_{selected_hour:02d}h.csv",
 "text/csv"
 )

else:
 st.info(" Set your preferences and click ' Predict Availability' to see individual parking spaces!")

# Sidebar legend
st.sidebar.markdown("---")
st.sidebar.markdown("### Legend")
st.sidebar.markdown("**Green**: ≥50% available")
st.sidebar.markdown("**Orange**: 25-49% available")
st.sidebar.markdown("**Red**: <25% available")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
 <p><b>Spotly - Find Your Perfect Spot</b></p>
 <p>AI-Powered Parking Made Simple | NYC Datathon 2024</p>
</div>
""", unsafe_allow_html=True)
