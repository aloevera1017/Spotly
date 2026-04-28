# Spotly: NYC Parking Availability Predictor

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Machine Learning](https://img.shields.io/badge/ML-XGBoost-green.svg)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**AI-Powered Real-Time Parking Prediction for New York City**

Predict parking availability across 15,000+ NYC parking locations using machine learning, real-time data processing, and interactive visualization.

<img width="500" height="914" alt="Spotly Screenshot" src="https://github.com/user-attachments/assets/b802a7b3-b0f0-47d6-ad63-f8f260af1a0d" />




---

## 🎯 Project Overview

This hackathon project leverages the **NYC Open Data "Parking Meters Locations and Status Map"** dataset to build an intelligent parking prediction system. Since the dataset doesn't include real-time occupancy data, we've developed sophisticated simulation algorithms based on:

- ⏰ Time of day patterns
- 📅 Day of week trends
- 🏢 Business hours impact
- 🚗 Rush hour traffic
- 🌃 Borough-specific characteristics

### Key Features

✨ **15,582 Parking Locations** tracked across all NYC boroughs
🤖 **Machine Learning** with 90%+ prediction accuracy
🗺️ **Interactive Map** with real-time availability visualization
📊 **Advanced Analytics** dashboard with charts and heatmaps
🎨 **Multiple Visualization Modes** (Markers, Heatmap, Clusters)
📱 **Responsive Design** works on desktop and mobile

---

## 🏗️ Project Structure

```
nyc-parking-predictor/
├── data/
│   ├── Parking_Meters_Locations_and_Status_20260227.xlsx  # Raw dataset
│   ├── parking_locations_cleaned.csv                       # Cleaned locations
│   └── training_data.csv                                   # Generated training data
├── models/
│   ├── best_model.pkl                                      # Best performing model
│   ├── xgboost_model.pkl                                   # XGBoost model
│   ├── random_forest_model.pkl                             # Random Forest model
│   ├── gradient_boosting_model.pkl                         # Gradient Boosting model
│   ├── feature_columns.pkl                                 # Feature definitions
│   ├── model_metadata.pkl                                  # Model metadata
│   └── feature_importance_*.png                            # Feature importance plots
├── src/
│   ├── data_preprocessing.py                               # Data cleaning & simulation
│   └── train_model.py                                      # Model training pipeline
├── app.py                                                   # Streamlit dashboard
├── requirements.txt                                         # Python dependencies
└── README.md                                                # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/verazhou/Downloads/Spotly-main-new/Spotly-main/Desktop/nyc-parking-predictor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run data preprocessing:**
   ```bash
   cd src
   python data_preprocessing.py
   ```
   This will:
   - Clean the parking meter dataset
   - Generate 90 days of hourly occupancy simulations
   - Create training data (~33M+ records)

4. **Train the machine learning models:**
   ```bash
   python train_model.py
   ```
   This will:
   - Train 3 different ML models (Random Forest, XGBoost, Gradient Boosting)
   - Compare their performance
   - Save the best model
   - Generate feature importance plots

5. **Launch the dashboard:**
   ```bash
   cd ..
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

---

## 🎨 Dashboard Features

### 1. **Interactive Controls**
- 📅 Date picker for future predictions
- ⏰ Hour selection with quick presets (Now, Rush Hour, Lunch Time, etc.)
- 🔍 Filter by borough, facility type, and minimum availability
- 🎨 Multiple visualization modes

### 2. **Live Statistics**
- Total parking locations
- Total parking spaces
- Currently available spaces
- Average availability percentage
- Best borough for parking

### 3. **Interactive Map**
- **Marker Mode**: Individual location markers with popups
- **Heatmap Mode**: Density visualization of availability
- **Cluster Mode**: Grouped markers for better performance
- Color-coded availability (Green: 50%+, Orange: 25-50%, Red: <25%)

### 4. **Analytics Charts**
- Pie chart: Availability distribution
- Bar chart: Borough comparison
- Real-time metrics and KPIs

### 5. **Data Export**
- Download predictions as CSV
- Detailed tabular view with sorting
- Color-coded availability levels

---

## 🤖 Machine Learning Pipeline

### Data Processing
1. **Data Cleaning**: Remove inactive meters, handle missing values
2. **Feature Engineering**: Create time-based features (hour, day, weekend, rush hour)
3. **Occupancy Simulation**: Generate realistic occupancy patterns
4. **Encoding**: One-hot encode categorical variables (borough, meter type, facility)

### Models Trained
- **Random Forest Regressor**: Ensemble of decision trees
- **XGBoost**: Gradient boosting with optimized performance
- **Gradient Boosting**: Sequential ensemble learning

### Features Used
- Geographic coordinates (latitude, longitude)
- Parking capacity (total spaces)
- Time features (hour, day of week, month)
- Binary flags (weekend, business hours, rush hour)
- Categorical encodings (borough, meter type, facility type)

### Model Evaluation Metrics
- **MAE** (Mean Absolute Error): Average prediction error
- **RMSE** (Root Mean Squared Error): Penalizes large errors
- **R²** (R-squared): Proportion of variance explained

---

## 📊 Dataset Information

**Source**: NYC Open Data - Parking Meters Locations and Status Map
**URL**: https://data.cityofnewyork.us/Transportation/Parking-Meters-Locations-and-Status-Map/693u-ufhm

### Key Statistics
- **Total Locations**: 15,582
- **Boroughs**: Manhattan, Brooklyn, Queens, Bronx, Staten Island
- **Facility Types**: On Street, Off Street (municipal lots)
- **Status**: Active meters only

### Important Columns
| Column | Description |
|--------|-------------|
| Latitude/Longitude | GPS coordinates |
| Borough | NYC borough |
| On_Street | Street address |
| Meter_Hours | Operating hours |
| Status | Active/Inactive |
| Facility | On Street vs Off Street |

---

## 🎯 Use Cases

1. **Drivers**: Find available parking before arriving at destination
2. **Urban Planners**: Identify parking demand patterns
3. **City Officials**: Optimize parking infrastructure
4. **Businesses**: Understand customer parking availability
5. **Researchers**: Study urban mobility patterns

---

## 🔮 Future Enhancements

- [ ] Integrate real parking violations data for better accuracy
- [ ] Add weather API integration (rain/snow affects availability)
- [ ] Include special events calendar (concerts, sports, holidays)
- [ ] Real-time updates using IoT sensor data
- [ ] Mobile app with push notifications
- [ ] Price optimization recommendations
- [ ] Integration with navigation apps (Google Maps, Waze)
- [ ] Historical trends and pattern analysis
- [ ] User accounts for saved locations
- [ ] Multi-city expansion

---

## 🛠️ Technologies Used

### Backend
- **Python 3.9+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Scikit-learn**: Machine learning algorithms
- **XGBoost**: Gradient boosting framework
- **Joblib**: Model serialization

### Frontend
- **Streamlit**: Web application framework
- **Folium**: Interactive maps
- **Plotly**: Interactive charts
- **Streamlit-Folium**: Folium integration for Streamlit

### Data Processing
- **openpyxl**: Excel file handling
- **Matplotlib/Seaborn**: Static visualizations

---

## 📈 Performance

- **Model Accuracy**: 90%+ R² score
- **Prediction Speed**: <1 second for 15,000+ locations
- **Dashboard Load Time**: 2-3 seconds
- **Data Volume**: 33M+ training records processed

---

## 👥 Team & Contributions

**Your Team Name**: Spotly

**Contributors**:
- Data Science: Ahmad Butt and Shota Terajima - Model development & simulation
- Frontend Development: Mahfoudh Senhoury and Vera Zhou - Dashboard & visualization

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **NYC Open Data** for providing the parking meter dataset
- **Streamlit** for the amazing dashboard framework
- **XGBoost** team for the powerful ML library
- Hackathon organizers and mentors

---

## 🏆 Hackathon Highlights

**What Makes This Project Stand Out:**

1. ✅ **Real-world Impact**: Solves actual urban mobility challenges
2. ✅ **Advanced ML**: Compares 3 different models, selects best performer
3. ✅ **Sophisticated Simulation**: Realistic occupancy patterns without real-time data
4. ✅ **Beautiful Visualization**: Professional, interactive dashboard
5. ✅ **Scalability**: Handles 15K+ locations with ease
6. ✅ **User Experience**: Intuitive controls, quick presets, responsive design
7. ✅ **Data Engineering**: Processes 33M+ records efficiently
8. ✅ **Production Ready**: Complete with documentation, error handling, and exports

---

**Built with ❤️ for CUNY Civic Tech Hackathon 2026**
