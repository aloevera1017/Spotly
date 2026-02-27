import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from PIL import Image
import base64
from io import BytesIO

# Page config
st.set_page_config(
    page_title="Community Insights - Spotly",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .insight-card {
        background-color: #f8fafc;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .contribute-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .insight-meta {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .stats-box {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Data file paths
INSIGHTS_FILE = "community_data/insights.json"
IMAGES_DIR = "community_data/images"

# Create directories if they don't exist
os.makedirs("community_data/images", exist_ok=True)

# Load insights
def load_insights():
    """Load all community insights from JSON file"""
    if os.path.exists(INSIGHTS_FILE):
        with open(INSIGHTS_FILE, 'r') as f:
            return json.load(f)
    return []

# Save insights
def save_insights(insights):
    """Save insights to JSON file"""
    with open(INSIGHTS_FILE, 'w') as f:
        json.dump(insights, f, indent=2)

# Save uploaded image
def save_uploaded_image(uploaded_file, insight_id):
    """Save uploaded image and return file path"""
    if uploaded_file is not None:
        # Create unique filename
        ext = uploaded_file.name.split('.')[-1]
        filename = f"{insight_id}.{ext}"
        filepath = os.path.join(IMAGES_DIR, filename)

        # Save image
        img = Image.open(uploaded_file)
        # Resize if too large
        max_size = (1200, 1200)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(filepath)

        return filepath
    return None

# Get image as base64 for display
def get_image_base64(image_path):
    """Convert image to base64 for display"""
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

# Title
st.markdown('<h1 class="main-header">🌐 Community Insights</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.1rem;'>Share real parking conditions & help the community find spaces faster!</p>", unsafe_allow_html=True)

st.markdown("---")

# Load existing insights
insights = load_insights()

# Statistics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="stats-box"><h3>📸</h3><p style="font-size: 1.5rem; font-weight: bold;">{}</p><p>Total Insights</p></div>'.format(len(insights)), unsafe_allow_html=True)
with col2:
    today_count = len([i for i in insights if i.get('date', '').startswith(datetime.now().strftime('%Y-%m-%d'))])
    st.markdown(f'<div class="stats-box"><h3>🔥</h3><p style="font-size: 1.5rem; font-weight: bold;">{today_count}</p><p>Shared Today</p></div>', unsafe_allow_html=True)
with col3:
    locations = len(set([i.get('location', '') for i in insights]))
    st.markdown(f'<div class="stats-box"><h3>📍</h3><p style="font-size: 1.5rem; font-weight: bold;">{locations}</p><p>Locations Covered</p></div>', unsafe_allow_html=True)
with col4:
    avg_rating = sum([i.get('availability_rating', 3) for i in insights]) / len(insights) if insights else 0
    st.markdown(f'<div class="stats-box"><h3>⭐</h3><p style="font-size: 1.5rem; font-weight: bold;">{avg_rating:.1f}/5</p><p>Avg Availability</p></div>', unsafe_allow_html=True)

st.markdown("---")

# Create tabs
tab1, tab2 = st.tabs(["📸 Contribute Insight", "👁️ View Community Insights"])

# ==================== CONTRIBUTE TAB ====================
with tab1:
    st.markdown("""
    <div class="contribute-section">
        <h2>📸 Share Your Parking Experience</h2>
        <p style="font-size: 1.1rem;">Help fellow drivers by sharing real-time parking conditions in your area. Upload a photo and add details!</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("contribute_form", clear_on_submit=True):
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### 📍 Location Details")
            location_input = st.text_input(
                "Location / Address*",
                placeholder="e.g., Times Square, E 42nd St & Broadway"
            )

            borough = st.selectbox(
                "Borough*",
                ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
            )

            col_time1, col_time2 = st.columns(2)
            with col_time1:
                observation_date = st.date_input("Date*", datetime.now())
            with col_time2:
                observation_time = st.time_input("Time*", datetime.now().time())

        with col_right:
            st.markdown("#### 📊 Parking Conditions")
            availability_rating = st.select_slider(
                "Parking Availability*",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: ["🔴 Very Full", "🟠 Limited", "🟡 Moderate", "🟢 Available", "✅ Plenty"][x-1]
            )

            traffic_level = st.selectbox(
                "Traffic Level",
                ["Light", "Moderate", "Heavy", "Very Heavy"]
            )

            parking_type = st.selectbox(
                "Parking Type",
                ["Street Parking", "Parking Lot", "Garage", "Other"]
            )

        st.markdown("#### 📝 Additional Information")
        description = st.text_area(
            "Description / Notes",
            placeholder="E.g., 'Many open spots on the north side', 'Construction blocking some spaces', 'Event nearby affecting parking'...",
            height=100
        )

        st.markdown("#### 📸 Upload Photo")
        uploaded_file = st.file_uploader(
            "Upload a photo of the parking area (optional)",
            type=['png', 'jpg', 'jpeg'],
            help="Share a photo showing parking conditions"
        )

        col_name, col_anonymous = st.columns([3, 1])
        with col_name:
            contributor_name = st.text_input(
                "Your Name (optional)",
                placeholder="Anonymous"
            )
        with col_anonymous:
            st.write("")
            st.write("")
            anonymous = st.checkbox("Post anonymously", value=False)

        # Submit button
        submitted = st.form_submit_button("🚀 Share Insight", type="primary", use_container_width=True)

        if submitted:
            if not location_input:
                st.error("❌ Please enter a location!")
            else:
                # Create insight ID
                insight_id = f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(insights)}"

                # Save image if uploaded
                image_path = None
                if uploaded_file is not None:
                    image_path = save_uploaded_image(uploaded_file, insight_id)

                # Create insight object
                new_insight = {
                    "id": insight_id,
                    "location": location_input,
                    "borough": borough,
                    "date": observation_date.strftime('%Y-%m-%d'),
                    "time": observation_time.strftime('%H:%M'),
                    "availability_rating": availability_rating,
                    "traffic_level": traffic_level,
                    "parking_type": parking_type,
                    "description": description,
                    "contributor": "Anonymous" if anonymous else (contributor_name or "Anonymous"),
                    "image_path": image_path,
                    "timestamp": datetime.now().isoformat(),
                    "likes": 0,
                    "helpful_count": 0
                }

                # Add to insights
                insights.append(new_insight)
                save_insights(insights)

                st.success("✅ Thank you! Your insight has been shared with the community!")
                st.balloons()

# ==================== VIEW INSIGHTS TAB ====================
with tab2:
    st.markdown("### 👁️ Community Parking Insights")

    if not insights:
        st.info("🎯 No insights yet! Be the first to contribute and help the community.")
    else:
        # Filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            filter_borough = st.selectbox(
                "Filter by Borough",
                ["All"] + sorted(list(set([i['borough'] for i in insights])))
            )

        with col_filter2:
            filter_rating = st.select_slider(
                "Min Availability",
                options=[1, 2, 3, 4, 5],
                value=1,
                format_func=lambda x: f"{x}⭐+"
            )

        with col_filter3:
            sort_by = st.selectbox(
                "Sort by",
                ["Most Recent", "Highest Rating", "Most Helpful"]
            )

        st.markdown("---")

        # Filter insights
        filtered_insights = insights.copy()

        if filter_borough != "All":
            filtered_insights = [i for i in filtered_insights if i['borough'] == filter_borough]

        filtered_insights = [i for i in filtered_insights if i['availability_rating'] >= filter_rating]

        # Sort insights
        if sort_by == "Most Recent":
            filtered_insights.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == "Highest Rating":
            filtered_insights.sort(key=lambda x: x['availability_rating'], reverse=True)
        else:  # Most Helpful
            filtered_insights.sort(key=lambda x: x['helpful_count'], reverse=True)

        st.markdown(f"**Showing {len(filtered_insights)} insights**")

        # Display insights
        for insight in filtered_insights:
            with st.container():
                st.markdown('<div class="insight-card">', unsafe_allow_html=True)

                # Header
                col_header1, col_header2, col_header3 = st.columns([3, 1, 1])

                with col_header1:
                    st.markdown(f"### 📍 {insight['location']}")
                    st.markdown(f"<p class='insight-meta'>🏙️ {insight['borough']} | 📅 {insight['date']} at {insight['time']}</p>", unsafe_allow_html=True)

                with col_header2:
                    rating_display = ["🔴", "🟠", "🟡", "🟢", "✅"][insight['availability_rating']-1]
                    st.markdown(f"<h2 style='text-align: center;'>{rating_display}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 0.9rem;'>{insight['availability_rating']}/5 Available</p>", unsafe_allow_html=True)

                with col_header3:
                    st.markdown(f"**Traffic:** {insight['traffic_level']}")
                    st.markdown(f"**Type:** {insight['parking_type']}")

                # Image
                if insight.get('image_path') and os.path.exists(insight['image_path']):
                    st.image(insight['image_path'], use_container_width=True, caption=f"Photo from {insight['contributor']}")

                # Description
                if insight.get('description'):
                    st.markdown(f"**💬 Note:** {insight['description']}")

                # Footer
                col_footer1, col_footer2, col_footer3 = st.columns([2, 1, 1])

                with col_footer1:
                    st.markdown(f"<p class='insight-meta'>👤 Shared by: {insight['contributor']}</p>", unsafe_allow_html=True)

                with col_footer2:
                    if st.button(f"👍 Helpful ({insight['helpful_count']})", key=f"helpful_{insight['id']}"):
                        # Increment helpful count
                        for i in insights:
                            if i['id'] == insight['id']:
                                i['helpful_count'] += 1
                        save_insights(insights)
                        st.rerun()

                with col_footer3:
                    if st.button(f"❤️ Like ({insight['likes']})", key=f"like_{insight['id']}"):
                        # Increment likes
                        for i in insights:
                            if i['id'] == insight['id']:
                                i['likes'] += 1
                        save_insights(insights)
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p><b>Spotly Community</b> - Powered by Real Drivers, For Real Drivers</p>
    <p>Help make NYC parking easier for everyone! 🅿️</p>
</div>
""", unsafe_allow_html=True)
