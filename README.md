# Hospital Survey Results Dashboard

A Streamlit web application that displays hospital survey results with interactive spider charts for dimensional analysis. Data is fetched directly from Google Sheets in real-time.

## Features

- 📊 Interactive spider charts for 5-dimension analysis
- 🔍 Direct access via Submission ID in URL
- 📋 Detailed submission information display
- 📈 Comparison view for all submissions
- 🎨 Modern and responsive UI
- 🔄 Real-time data from Google Sheets
- 🇮🇩 Indonesian language interface

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. The application will be available at `http://localhost:8501`

## Data Source

The application fetches data directly from Google Sheets:
- **Sheet URL**: https://docs.google.com/spreadsheets/d/1fneHP0zuCz2OHXNQqfZCM2aafjxBcNC2FbwYKF00SEw/edit
- **Auto-refresh**: Data is cached for 5 minutes and refreshed automatically
- **Manual refresh**: Use the "🔄 Refresh Data" button to force refresh

## Usage

### Direct Access by Submission ID

You can access specific submissions directly using the URL:
```
http://localhost:8501/?submission_id=6278427714402759740
```

Replace `6278427714402759740` with any valid Submission ID from your data.

### Features Overview

- **Spider Chart**: Visual representation of the 5 dimensions for each submission
- **Submission Details**: Complete information about the respondent and hospital
- **Navigation**: Top-level selection to switch between different submissions
- **Comparison Mode**: View all submissions overlaid on a single spider chart
- **Raw Data View**: Expandable section to view all survey responses
- **Real-time Updates**: Data is automatically refreshed from Google Sheets

## Data Structure

The Google Sheets should contain the following key columns:
- `Nama Responden`: Respondent name
- `Jabatan`: Position/Role
- `Nama Rumah Sakit`: Hospital name
- `Lokasi Rumah Sakit`: Hospital location
- `Jumlah Tempat Tidur`: Number of beds
- `Dimensi 1` through `Dimensi 5`: Dimensional scores
- `Submission ID`: Unique identifier for each submission

## Troubleshooting

### Data Loading Issues
- Ensure the Google Sheets is publicly accessible
- Check your internet connection
- Use the "🔄 Refresh Data" button if data seems outdated
- The sheet must be published to the web or have public viewing permissions

### URL Access Issues
- Make sure submission IDs in URLs match exactly with data in the sheet
- Use the dropdown selector if direct URL access fails

## Customization

You can customize the application by modifying:
- Colors and styling in the CSS section
- Chart appearance in the `create_spider_chart()` function
- Data display format in the `display_submission_details()` function
- Google Sheets URL in the `load_data()` function
