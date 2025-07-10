import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from urllib.parse import parse_qs, urlparse
import requests
import io

dim_detail = {
    'Dimensi 1': 'LEADERSHIP & STRATEGI',
    'Dimensi 2': 'DATA & INFRASTRUKTUR',
    'Dimensi 3': 'USE CASE AI',
    'Dimensi 4': 'TATA KELOLA & ETIKA',
    'Dimensi 5': 'SDM & KOMPETENSI'
}

# Set page config
st.set_page_config(
    page_title="Dashboard Hasil Survey",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Force light mode */
    .stApp {
        background-color: white !important;
        color: black !important;
    }
    
    /* Force light mode for all elements */
    .stApp > div {
        background-color: white !important;
    }
    
    /* Ensure text is always dark */
    .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }
    
    /* Force light background for containers */
    .main, .block-container, [data-testid="stAppViewContainer"] {
        background-color: white !important;
    }
    
    /* Force light mode for metrics and other components */
    [data-testid="metric-container"] {
        background-color: white !important;
        color: black !important;
    }
    
    /* Force light mode for selectbox and other inputs */
    .stSelectbox, .stButton, .stCheckbox {
        background-color: white !important;
        color: black !important;
    }
    
    /* Force light mode for dataframes */
    .stDataFrame {
        background-color: white !important;
    }
    
    /* Hide sidebar completely */
    .css-1d391kg {display: none;}
    .css-1rs6os {display: none;}
    .css-17ziqus {display: none;}
    [data-testid="stSidebar"] {display: none;}
    .css-1lcbmhc {display: none;}
    .css-1outpf7 {display: none;}
    
    /* Adjust main content area */
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: none;
        background-color: white !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79 !important;
        text-align: center;
        margin-bottom: 2rem;
        background-color: white !important;
    }
    .submission-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2e7d32 !important;
        margin-bottom: 1rem;
        background-color: white !important;
    }
    .info-card {
        background-color: #f5f5f5 !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: black !important;
    }
    .metric-card {
        background-color: #e3f2fd !important;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
        color: black !important;
    }
    
    /* Force light mode for alerts/notifications */
    .stAlert, .stSuccess, .stError, .stWarning, .stInfo {
        background-color: white !important;
        color: black !important;
    }
    
    /* Force light mode for expanders */
    .streamlit-expanderHeader {
        background-color: white !important;
        color: black !important;
    }
    
    /* Force light mode for progress bars */
    .stProgress {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Memuat data dari Google Sheets - selalu update real-time"""
    try:
        # Google Sheets URL from Streamlit secrets
        try:
            sheet_id = st.secrets["GOOGLE_SHEETS_ID"]
        except KeyError:
            raise Exception("GOOGLE_SHEETS_ID tidak ditemukan di Streamlit secrets")
        
        # Convert to CSV export URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        # Fetch the data with headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(csv_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Check if we got HTML instead of CSV (indicates access denied)
        if response.text.strip().startswith('<'):
            raise Exception("Google Sheets tidak dapat diakses. Sheet harus dipublikasikan atau dibuat public.")
        
        # Read CSV data
        csv_data = io.StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Validate required columns - check for both old and new format
        new_format_columns = ['Submission ID', 'Skor Dimensi 1', 'Skor Dimensi 2', 'Skor Dimensi 3', 'Skor Dimensi 4', 'Skor Dimensi 5']
        old_format_columns = ['Submission ID', 'Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']
        
        # Check if new format exists
        if all(col in df.columns for col in new_format_columns):
            # Rename new format columns to match the expected format
            df = df.rename(columns={
                'Skor Dimensi 1': 'Dimensi 1',
                'Skor Dimensi 2': 'Dimensi 2', 
                'Skor Dimensi 3': 'Dimensi 3',
                'Skor Dimensi 4': 'Dimensi 4',
                'Skor Dimensi 5': 'Dimensi 5',
                'Lokasi RS:': 'Lokasi Rumah Sakit',
                'Nama Responden:': 'Nama Responden',
                'Jabatan:': 'Jabatan',
                'Nama Rumah Sakit:': 'Nama Rumah Sakit',
                'Jumlah Tempat Tidur:': 'Jumlah Tempat Tidur'
            })
        elif not all(col in df.columns for col in old_format_columns):
            missing_columns = [col for col in old_format_columns if col not in df.columns]
            raise Exception(f"Kolom yang diperlukan tidak ditemukan: {', '.join(missing_columns)}")
        
        if df.empty:
            # Return empty DataFrame instead of raising exception
            return pd.DataFrame()
        
        # Check if DataFrame has data rows (not just headers)
        if len(df) == 0:
            return pd.DataFrame()
        
        return df
        
    except Exception as e:
        # st.error(f"Data Tidak dapat memuat data: {e}")
        st.info("**Data masih kosong**")
        return pd.DataFrame()  # Return empty DataFrame instead of None

def create_spider_chart(dimensions_data, submission_id):
    """Membuat spider chart untuk 5 dimensi"""
    
    categories = [
        'LEADERSHIP & STRATEGI', 
        'DATA & INFRASTRUKTUR',
        'USE CASE AI',
        'TATA KELOLA & ETIKA',
        'SDM & KOMPETENSI',
    ]
    values = [
        dimensions_data['Dimensi 1'],
        dimensions_data['Dimensi 2'], 
        dimensions_data['Dimensi 3'],
        dimensions_data['Dimensi 4'],
        dimensions_data['Dimensi 5']
    ]
    
    # Add the first value at the end to close the spider chart
    values += values[:1]
    categories += categories[:1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=f'Hasil Survei',
        line=dict(color='rgb(46, 125, 50)', width=3),
        fillcolor='rgba(46, 125, 50, 0.3)'
    ))
    
    # Find max value for better scaling
    max_val = max([dimensions_data['Dimensi 1'], dimensions_data['Dimensi 2'], 
                   dimensions_data['Dimensi 3'], dimensions_data['Dimensi 4'], 
                   dimensions_data['Dimensi 5']])
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_val + 2],
                tickfont=dict(size=10),
                gridcolor='lightgray'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color='#1f4e79'),
                direction='clockwise',            )
        ),
        showlegend=False,
        title=dict(
            text=f"Analisis Dimensi",
            x=0.5,
            font=dict(size=16, color='#1f4e79')
        ),
        font=dict(size=10),
        paper_bgcolor='white',
        plot_bgcolor='white',
        autosize=True,
        margin=dict(l=100, r=100, t=80, b=80),
    )
    
    return fig

def display_submission_details(submission_data):
    """Menampilkan informasi detail tentang submission"""
    
    # Basic Information
    st.markdown('<div class="submission-header">Detail Submission</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**👤 Informasi Responden**")
        st.write(f"**Nama:** {submission_data['Nama Responden']}")
        st.write(f"**Jabatan:** {submission_data['Jabatan']}")
        # st.markdown('</div>', unsafe_allow_html=True)
        
        # st.markdown("**🏥 Informasi Rumah Sakit**")
        st.write(f"**Nama Rumah Sakit:** {submission_data['Nama Rumah Sakit']}")
        # st.write(f"**Lokasi:** {submission_data['Lokasi Rumah Sakit']}")
        # st.write(f"**Jumlah Tempat Tidur:** {submission_data['Jumlah Tempat Tidur']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # with col2:
    #     # Dimensions Overview
    #     st.markdown("**📊 Ringkasan Dimensi**")
        
    #     dim_cols = st.columns(5)
    #     for i, dim in enumerate(['Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']):
    #         with dim_cols[i]:
    #             st.metric(
    #                 label=dim + f": {dim_detail[dim]}",
    #                 value=submission_data[dim],
    #                 delta=None
    #             )
    #     st.markdown('</div>', unsafe_allow_html=True)

def calculate_ai_maturity_score(submission_data):
    """Menghitung skor AI maturity berdasarkan dimensi dan bobotnya"""
    
    # Definisi bobot untuk setiap dimensi
    weights = {
        'Dimensi 1': 0.25,  # Leadership & Strategi - 25%
        'Dimensi 2': 0.25,  # Data & Infrastruktur - 25%
        'Dimensi 3': 0.20,  # Use Case AI - 20%
        'Dimensi 4': 0.10,   # Tata Kelola & Etika - 10%
        'Dimensi 5': 0.20  # SDM & Kompetensi - 20%
    }
    
    # Nama dimensi yang lebih deskriptif
    dimension_names = {
        'Dimensi 1': 'Leadership & Strategi',
        'Dimensi 2': 'Data & Infrastruktur',
        'Dimensi 3': 'Use Case AI',
        'Dimensi 4': 'Tata Kelola & Etika',
        'Dimensi 5': 'SDM & Kompetensi'
    }
    
    # Hitung skor mentah total (dari 75 poin maksimal)
    raw_total = sum([submission_data[f'Dimensi {i}'] for i in range(1, 6)])
    
    # Hitung skor tertimbang untuk setiap dimensi
    weighted_scores = {}
    total_weighted_score = 0
    
    for i in range(1, 6):
        dim_key = f'Dimensi {i}'
        raw_score = submission_data[dim_key]
        weighted_score = raw_score * weights[dim_key]
        weighted_scores[dim_key] = {
            'raw': raw_score,
            'weighted': weighted_score,
            'weight_percent': weights[dim_key] * 100,
            'name': dimension_names[dim_key]
        }
        total_weighted_score += weighted_score
    
    return {
        'raw_total': raw_total,
        'weighted_total': total_weighted_score,
        'weighted_scores': weighted_scores
    }

def get_ai_maturity_level(score):
    """Menentukan level AI maturity berdasarkan skor"""
    # Convert weighted score (0-15) to percentage scale (0-100) for easier comparison
    # Then map to the original 15-75 scale for level determination
    percentage = (score / 15) * 100
    scaled_score = (percentage / 100) * 60 + 15  # Scale to 15-75 range
    
    if percentage <= 35:
        return {
            'level': 1,
            'name': 'Awareness',
            'description': 'RS baru menyadari potensi AI',
            'characteristics': [
                'Belum ada inisiatif konkret atau pilot project',
                'Fokus: Education dan awareness building'
            ],
            'next_steps': [
                'Edukasi manajemen dan staf mengenai potensi AI di layanan kesehatan melalui workshop atau webinar',
                'Lakukan benchmarking ke RS lain yang sudah menggunakan AI',
                'Petakan area sederhana yang cocok untuk dijadikan pilot project'
            ],
            'color': '#ff6b6b'
        }
    elif percentage <= 55:
        return {
            'level': 2,
            'name': 'Exploration',
            'description': 'Pilot project terbatas dan uji coba awal',
            'characteristics': [
                'Investasi minimal untuk proof of concept (PoC)',
                'Fokus: Learning dan experimentation'
            ],
            'next_steps': [
                'Evaluasi hasil 1-2 pilot project dan dokumentasikan lessons learned',
                'Buat business case untuk scaling solusi AI yang berhasil',
                'Tingkatkan infrastruktur IT untuk mendukung implementasi yang lebih luas'
            ],
            'color': '#ffa726'
        }
    elif percentage <= 75:
        return {
            'level': 3,
            'name': 'Implementation',
            'description': 'Beberapa solusi AI berjalan operasional',
            'characteristics': [
                'Mulai ada governance dan standar penggunaan AI',
                'Fokus: Standardisasi dan integrasi sistem'
            ],
            'next_steps': [
                'Standardisasi proses implementasi AI di seluruh departemen',
                'Integrasikan sistem AI dengan workflow yang sudah ada',
                'Kembangkan policy dan SOP penggunaan AI yang lebih komprehensif'
            ],
            'color': '#66bb6a'
        }
    elif percentage <= 90:
        return {
            'level': 4,
            'name': 'Scale-Up',
            'description': 'AI terintegrasi dalam operasional utama',
            'characteristics': [
                'Ada strategy roadmap dan resource yang dedicated untuk AI',
                'Fokus: Optimisasi dan ekspansi'
            ],
            'next_steps': [
                'Optimalisasi ROI dari investasi AI yang sudah ada',
                'Ekspansi ke use case AI yang lebih advanced dan kompleks',
                'Bangun sistem pemantauan berkala untuk mengevaluasi impact dari AI'
            ],
            'color': '#42a5f5'
        }
    elif percentage <= 100:
        return {
            'level': 5,
            'name': 'Transformation',
            'description': 'AI menjadi core competitive advantage',
            'characteristics': [
                'Continuous innovation dan improvement culture',
                'Fokus: Leadership dan best practices'
            ],
            'next_steps': [
                'Menjadi center of excellence untuk AI implementation di healthcare',
                'Kolaborasi dengan institusi penelitian untuk mengembangkan AI baru',
                'Mentoring dan knowledge sharing dengan rumah sakit lain dalam ekosistem'
            ],
            'color': '#ab47bc'
        }
    else:
        return {
            'level': 0,
            'name': 'Invalid',
            'description': f'Skor tidak valid: {percentage:.2f} (dari score: {score:.2f})',
            'characteristics': [f'Score range should be 15-75, got {scaled_score:.2f}'],
            'next_steps': 'Periksa kembali perhitungan skor',
            'color': '#757575'
        }

def display_ai_maturity_analysis(submission_data):
    """Menampilkan analisis AI maturity lengkap"""
    
    # Hitung skor
    scores = calculate_ai_maturity_score(submission_data)
    maturity_level = get_ai_maturity_level(scores['weighted_total'])
    
    st.markdown("---")
    st.markdown('<div class="submission-header">Perhitungan Skor AI Maturity</div>', unsafe_allow_html=True)
    
    # Tabel perhitungan skor
    st.markdown("### PERHITUNGAN SKOR AKHIR")
    
    # Create a detailed scoring table
    scoring_data = []
    for dim_key, data in scores['weighted_scores'].items():
        scoring_data.append({
            'Dimensi': data['name'],
            'Skor': f"{data['raw']}/15",
            'Bobot': f"{data['weight_percent']:.0f}%",
            'Skor Tertimbang': f"{data['weighted']:.2f}"
        })
    
    df_scoring = pd.DataFrame(scoring_data)
    st.dataframe(df_scoring, use_container_width=True, hide_index=True)
    
    # Total scores
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="TOTAL SKOR MURNI",
            value=f"{scores['raw_total']}/75",
            help="Total dari semua jawaban (5 dimensi × 15 poin maksimal)"
        )
    
    with col2:
        st.metric(
            label="TOTAL SKOR TERTIMBANG",
            value=f"{scores['weighted_total']:.2f}/15",
            help="Skor yang sudah dikalikan dengan bobot masing-masing dimensi"
        )
    
    with col3:
        st.metric(
            label="PERSENTASE",
            value=f"{(scores['weighted_total']/15)*100:.1f}%",
            help="Persentase pencapaian dari skor maksimal"
        )
    
    # AI Maturity Level Analysis
    st.markdown("---")
    st.markdown('<div class="submission-header">🏆 Interpretasi Hasil</div>', unsafe_allow_html=True)
    
    # Display current level with styling
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, {maturity_level['color']}22, {maturity_level['color']}44);
        border-left: 5px solid {maturity_level['color']};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    ">
        <h4 style="color: {maturity_level['color']}; margin: 0;">
            🎯 Level AI Maturity RS Anda: 
        </h4>
        <h3 style="color: {maturity_level['color']}; margin: 0;">
            <tab></tab>Level {maturity_level['level']} - {maturity_level['name']}
        </h3>
        <p style="margin: 0.5rem 0; font-size: 1.1rem;">
            {maturity_level['description']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Current level details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Karakteristik Level Anda:")
        for char in maturity_level['characteristics']:
            st.write(f"• {char}")
    
    with col2:
        st.markdown("#### Langkah Selanjutnya:")
        for step in maturity_level['next_steps']:
            st.write(f"• {step}")
    
    # All levels reference
    st.markdown("---")
    st.markdown("### 📚 REFERENSI LEVEL AI MATURITY")
    
    all_levels = [
        (1, "Awareness", "20-35", "#ff6b6b"),
        (2, "Exploration", "36-55", "#ffa726"),
        (3, "Implementation", "56-75", "#66bb6a"),
        (4, "Scale-Up", "76-90", "#42a5f5"),
        (5, "Transformation", "91-100", "#ab47bc")
    ]
    
    for level_num, level_name, score_range, color in all_levels:
        is_current = level_num == maturity_level['level']
        border_style = f"border: 3px solid {color};" if is_current else f"border: 1px solid {color};"
        opacity = "1" if is_current else "0.7"
        
        # Convert raw score range (15-75) to weighted score range (0-15) for proper level calculation
        percentage_avg = (int(score_range.split('-')[0]) + int(score_range.split('-')[1])) / 2
        weighted_score_avg = (percentage_avg) / 100 * 15  # Convert 15-75 range to 0-15 range
        level_info = get_ai_maturity_level(weighted_score_avg)
        
        st.markdown(f"""
        <div style="
            {border_style}
            background-color: {color}22;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            opacity: {opacity};
        ">
            <h4 style="color: {color}; margin: 0;">
                Level {level_num}: {level_name} (Skor {score_range}%)
            </h4>
            <p style="margin: 0.3rem 0;"><strong>{level_info['description']}</strong></p>
            <ul style="margin: 0.3rem 0; padding-left: 1.2rem;">
                {''.join([f'<li>{char}</li>' for char in level_info['characteristics']])}
            </ul>
            <p style="margin: 0.3rem 0;"><strong>Next Steps:</strong></p>
            <ul style="margin: 0.3rem 0; padding-left: 1.2rem;">
                {''.join([f'<li>{step}</li>' for step in level_info['next_steps']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    return scores, maturity_level

def calculate_all_submissions_average(df):
    """Menghitung rata-rata dari semua submission"""
    # Calculate averages for each dimension
    dimension_averages = {}
    for i in range(1, 6):
        dim_key = f'Dimensi {i}'
        dimension_averages[dim_key] = df[dim_key].mean()
    
    # Create a pseudo submission data with averages
    avg_submission = {
        'Dimensi 1': dimension_averages['Dimensi 1'],
        'Dimensi 2': dimension_averages['Dimensi 2'],
        'Dimensi 3': dimension_averages['Dimensi 3'],
        'Dimensi 4': dimension_averages['Dimensi 4'],
        'Dimensi 5': dimension_averages['Dimensi 5'],
        'Nama Responden': 'RATA-RATA SEMUA SUBMISSION',
        'Submission ID': 'AVG',
        'total_submissions': len(df)
    }
    
    return avg_submission, dimension_averages

def display_all_submissions_overview(df):
    """Menampilkan overview semua submission dengan rata-rata"""
    
    avg_submission, dimension_averages = calculate_all_submissions_average(df)
    avg_scores = calculate_ai_maturity_score(avg_submission)
    
    st.markdown("---")
    st.markdown('<div class="submission-header">Overview Semua Submission</div>', unsafe_allow_html=True)
    
    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Submission",
            value=len(df),
            help="Jumlah total submission yang terkumpul"
        )
    
    with col2:
        # overall_avg = sum([avg_submission[f'Dimensi {i}'] for i in range(1, 6)]) / 5
        st.metric(
            label="Rata-rata Skor",
            value=f"{avg_scores['weighted_total']:.2f}/15",
            help="Rata-rata skor dari semua dimensi"
        )
    
    with col3:
        # Calculate average AI maturity level
        avg_maturity = get_ai_maturity_level(avg_scores['weighted_total'])
        st.metric(
            label="Level Rata-rata",
            value=f"Level {avg_maturity['level']}",
            help=f"{avg_maturity['name']} - {avg_maturity['description']}"
        )
    
    with col4:
        percentage = (avg_scores['weighted_total'] / 15) * 100
        st.metric(
            label="Persentase Skor Rata-rata",
            value=f"{percentage:.1f}%",
            help="Persentase pencapaian rata-rata dari skor maksimal"
        )
    
    # Display dimensions analysis
    st.markdown("### Analisis Dimensi Rata-rata")
    
    # Create spider chart for averages on top
    spider_fig = create_spider_chart(avg_submission, "Rata-rata")
    spider_fig.update_layout(
        title="Rata-rata Semua Submission"
    )
    st.plotly_chart(spider_fig, use_container_width=True)
    
    # Dimension scores below
    st.markdown("#### Skor Rata-rata per Dimensi")
    for dim in ['Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']:
        avg_value = dimension_averages[dim]
        min_value = df[dim].min()
        max_value = df[dim].max()
        std_value = df[dim].std()
        
        # Create a progress bar visualization
        progress = avg_value / 15
        
        # Create columns for metric and statistics
        metric_col, stats_col = st.columns([1, 1])
        
        with metric_col:
            st.metric(
                label=dim.upper() + f": {dim_detail[dim]}",
                value=f"{avg_value:.1f}/15",
                help=f"Rata-rata: {avg_value:.1f} | Min: {min_value} | Max: {max_value} | Std: {std_value:.1f}"
            )
            st.progress(progress)
        
        # with stats_col:
        #     st.write(f"**Range:** {min_value} - {max_value}")
        #     st.write(f"**Std Dev:** {std_value:.1f}")
    
    # AI Maturity Analysis for averages
    # st.markdown("### 🏆 Interpretasi Rata-rata AI Maturity")
    
    # # Display average level with styling
    # st.markdown(f"""
    # <div style="
    #     background: linear-gradient(90deg, {avg_maturity['color']}22, {avg_maturity['color']}44);
    #     border-left: 5px solid {avg_maturity['color']};
    #     padding: 1rem;
    #     border-radius: 8px;
    #     margin: 1rem 0;
    # ">
    #     <h4 style="color: {avg_maturity['color']}; margin: 0;">
    #         🎯 Level AI Maturity Rata-rata: 
    #     </h4>
    #     <h3 style="color: {avg_maturity['color']}; margin: 0;">
    #         Level {avg_maturity['level']} - {avg_maturity['name']}
    #     </h3>
    #     <p style="margin: 0.5rem 0; font-size: 1.1rem;">
    #         {avg_maturity['description']}
    #     </p>
    #     <p style="margin: 0.5rem 0; font-style: italic;">
    #         Berdasarkan rata-rata dari {len(df)} submission
    #     </p>
    # </div>
    # """, unsafe_allow_html=True)
    
    # Distribution of submissions by level
    st.markdown("### Jumlah Submission per Level")
    
    # Calculate level for each submission
    level_distribution = {}
    for idx, row in df.iterrows():
        scores = calculate_ai_maturity_score(row)
        maturity = get_ai_maturity_level(scores['weighted_total'])
        level_name = f"Level {maturity['level']} - {maturity['name']}"
        level_distribution[level_name] = level_distribution.get(level_name, 0) + 1
    
    # Display distribution
    dist_cols = st.columns(5)
    for i, (level_name, count) in enumerate(level_distribution.items()):
        with dist_cols[i % 5]:
            percentage = (count / len(df)) * 100
            st.metric(
                label=level_name,
                value=f"{count}",
                # delta=f"{percentage:.1f}%"
            )
    
    return avg_submission, avg_scores, avg_maturity

def get_submission_id_from_url():
    """Mengambil submission ID dari parameter URL"""
    try:
        # For Streamlit 1.28.1, use experimental method
        query_params = st.experimental_get_query_params()
        submission_id = query_params.get('submission_id', [None])[0]
        return submission_id
    except Exception as e:
        return None

def display_empty_data_state():
    """Menampilkan halaman ketika data masih kosong"""
    st.markdown('<div class="submission-header">📊 Dashboard Belum Memiliki Data</div>', unsafe_allow_html=True)
    
    # Empty state illustration
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            margin: 2rem 0;
            border: 2px dashed #1976d2;
        ">
            <h1 style="font-size: 4rem; margin: 0; color: #1976d2;">📊</h1>
            <h3 style="color: #1976d2; margin: 1rem 0;">Data Survey Belum Tersedia</h3>
            <p style="color: #666; font-size: 1.1rem; margin: 0;">
                Saat ini belum ada data survey yang masuk ke dalam sistem.<br>
                Silakan tunggu hingga ada responden yang mengisi survey.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Information cards
    st.markdown("### ℹ️ Informasi")
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        <div style="
            background-color: #f8f9fa;
            border-left: 4px solid #17a2b8;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        ">
            <h4 style="color: #17a2b8; margin: 0 0 0.5rem 0;">🔄 Data Real-time</h4>
            <p style="margin: 0; color: #555;">
                Dashboard ini terhubung langsung dengan Google Sheets dan akan otomatis menampilkan data begitu ada submission baru.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown("""
        <div style="
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        ">
            <h4 style="color: #28a745; margin: 0 0 0.5rem 0;">📈 Fitur Dashboard</h4>
            <p style="margin: 0; color: #555;">
                Setelah ada data, Anda dapat melihat analisis AI maturity, spider chart, dan statistik lengkap.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # What to expect section
    st.markdown("---")
    st.markdown("### 🎯 Yang Akan Ditampilkan Setelah Ada Data")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        **📊 Overview Semua Submission**
        - Total submission
        - Rata-rata skor per dimensi
        - Level AI maturity rata-rata
        - Distribusi submission per level
        """)
    
    with feature_col2:
        st.markdown("""
        **🕷️ Spider Chart**
        - Visualisasi 5 dimensi AI maturity
        - Perbandingan skor antar dimensi
        - Grafik yang mudah dipahami
        """)
    
    with feature_col3:
        st.markdown("""
        **🏆 Analisis Maturity**
        - Level AI maturity (1-5)
        - Karakteristik setiap level
        - Rekomendasi langkah selanjutnya
        """)
    
    # Refresh button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()

def main():
    # Load data
    df = load_data()
    if df is None or df.empty:
        # Display empty state instead of error
        display_empty_data_state()
        return
    
    # Main header
    st.markdown('<div class="main-header">Hasil Survei AI Maturity Assesment Rumah Sakit</div>', unsafe_allow_html=True)
    
    # Check if submission_id is provided in URL
    submission_id_from_url = get_submission_id_from_url()
    
    # Get list of submission IDs
    submission_ids = df['Submission ID'].astype(str).tolist()
    
    # If no query params, show only all submissions overview
    if not submission_id_from_url:
        # Display all submissions overview only
        avg_submission, avg_scores, avg_maturity = display_all_submissions_overview(df)
        
        # Add link to access individual submissions
        # st.markdown("---")
        # st.markdown("### 🔗 Akses Hasil Individual")
        # st.info("💡 Untuk melihat hasil individual, gunakan URL: `?submission_id=<ID>` di akhir URL ini")
        
        # # Show available submission IDs
        # with st.expander("� Daftar Submission ID yang tersedia"):
        #     for i, sub_id in enumerate(submission_ids):
        #         col1, col2 = st.columns([1, 3])
        #         with col1:
        #             st.code(sub_id)
        #         with col2:
        #             # Get responder name for this submission
        #             responder_name = df[df['Submission ID'].astype(str) == sub_id]['Nama Responden'].iloc[0]
        #             st.write(f"**{responder_name}**")
        
        # Add dropdown to access individual submissions
        # st.markdown("---")
        # st.markdown("### 🔗 Akses Hasil Individual")
        
        # # Create options for dropdown with submission ID and responder name
        # submission_options = ["Pilih submission individual"]
        # submission_mapping = {}
        
        # for sub_id in submission_ids:
        #     responder_name = df[df['Submission ID'].astype(str) == sub_id]['Nama Responden'].iloc[0]
        #     option_text = f"{responder_name} (ID: {sub_id})"
        #     submission_options.append(option_text)
        #     submission_mapping[option_text] = sub_id
        
        # # Dropdown selection
        # selected_option = st.selectbox(
        #     "Pilih submission yang ingin dilihat:",
        #     options=submission_options,
        #     key="submission_selector"
        # )
        
        # # Navigate to selected submission
        # if selected_option != "Pilih submission individual":
        #     selected_submission_id = submission_mapping[selected_option]
        #     query_params = st.experimental_get_query_params()
        #     query_params['submission_id'] = selected_submission_id
        #     st.experimental_set_query_params(**query_params)
        #     st.rerun()
    
    # If query params exist, show only individual submission
    else:
        # Validate submission ID
        if submission_id_from_url not in submission_ids:
            st.error(f"❌ Submission ID '{submission_id_from_url}' tidak ditemukan!")
            st.markdown("### Refresh untuk mencoba lagi")
            # for sub_id in submission_ids:
            #     st.code(sub_id)
            return
        
        # Get the selected submission data
        submission_data = df[df['Submission ID'].astype(str) == submission_id_from_url].iloc[0]
        
        # Add back to overview link
        # st.markdown("### 🏠 [← Kembali ke Overview Semua Submission](?)")
        
        # Display submission details
        display_submission_details(submission_data)
        
        # Create and display spider chart
        st.markdown("---")
        st.markdown('<div class="submission-header">Analisis Dimensi</div>', unsafe_allow_html=True)
        
        # Spider chart on top
        spider_fig = create_spider_chart(submission_data, submission_id_from_url)
        st.plotly_chart(spider_fig, use_container_width=True)
        
        metric_col, stats_col = st.columns([1, 1])
        
        with metric_col:
        # Dimension scores below
            st.markdown("### Skor per Dimensi")
            for dim in ['Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']:
                value = submission_data[dim]
                # Create a simple progress bar visualization
                progress = value / 15
                st.metric(
                    label=dim.upper() + f": {dim_detail[dim]}",
                    value=f"{value}/15",
                    help=f"Skor: {value}"
                )
                st.progress(progress)
        
        # AI Maturity Analysis
        display_ai_maturity_analysis(submission_data)
        
        # Raw data section (expandable)
        # with st.expander("🔍 Lihat Data Survey Lengkap"):
        #     # Filter out dimension columns for better readability
        #     display_columns = [col for col in df.columns if not col.startswith('Dimensi') and col != 'Submission ID']
        #     display_data = submission_data[display_columns].to_frame().T
        #     st.dataframe(display_data, use_container_width=True)

if __name__ == "__main__":
    main()
