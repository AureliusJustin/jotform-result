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

2. Set up configuration:
   - Create `.streamlit/secrets.toml` file:
   ```bash
   mkdir -p .streamlit
   ```
   - Edit `.streamlit/secrets.toml` and add your Google Sheets ID:
   ```toml
   GOOGLE_SHEETS_ID = "your_google_sheets_id_here"
   ```
   - The Google Sheets ID can be found in the URL: `https://docs.google.com/spreadsheets/d/[SHEETS_ID]/edit`

## Running the Application

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. The application will be available at `http://localhost:8501`

## Data Source

The application fetches data directly from Google Sheets:
- **Configuration**: Google Sheets ID is stored in `.streamlit/secrets.toml` file for security
- **Auto-refresh**: Data is cached for 5 minutes and refreshed automatically
- **Manual refresh**: Use the "🔄 Refresh Data" button to force refresh

### Setting up Google Sheets Access

1. Make sure your Google Sheets is publicly accessible:
   - Open your Google Sheets
   - Click "Share" → "Anyone with the link can view"
   - Or: File → Publish to the web → Publish

2. Get your Google Sheets ID:
   - From the URL: `https://docs.google.com/spreadsheets/d/[SHEETS_ID]/edit`
   - Copy the SHEETS_ID part and add it to your `.env` file

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

## Deployment on Streamlit Cloud

To deploy this application on Streamlit Cloud:

1. **Push your code to GitHub** (without the `.streamlit/secrets.toml` file)

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select the repository and branch

3. **Configure secrets in Streamlit Cloud**:
   - In your Streamlit Cloud app dashboard, go to "Settings" → "Secrets"
   - Add your configuration in TOML format:
   ```toml
   GOOGLE_SHEETS_ID = "your_actual_google_sheets_id_here"
   ```

4. **Deploy**: The app will automatically deploy with the new configuration

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
- Google Sheets ID in the `.streamlit/secrets.toml` file

## Configuration

The application uses Streamlit secrets for configuration:
- `GOOGLE_SHEETS_ID`: The ID of your Google Sheets document

Make sure to set these in your `.env` file before running the application.
