import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from urllib.parse import parse_qs, urlparse
import os
import requests
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

dim_detail = {
    'Dimensi 1': 'DATA & INFRASTRUKTUR',
    'Dimensi 2': 'SDM & KOMPETENSI',
    'Dimensi 3': 'LEADERSHIP & STRATEGI',
    'Dimensi 4': 'IMPLEMENTASI USE CASE AI',
    'Dimensi 5': 'TATA KELOLA & ETIKA'
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
    """Memuat data dari Google Sheets dengan fallback ke file CSV lokal - selalu update real-time"""
    try:
        # Google Sheets URL from environment variable
        sheet_id = os.getenv('GOOGLE_SHEETS_ID')
        
        if not sheet_id:
            raise Exception("GOOGLE_SHEETS_ID tidak ditemukan di file .env")
        
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
            raise Exception("Google Sheets kosong atau tidak memiliki data.")
        
        return df
        
    except Exception as e:
        st.warning(f"⚠️ Tidak dapat mengakses Google Sheets: {e}")
        
        # Fallback to local CSV file
        try:
            # Try new format file first
            df = pd.read_csv('SURVEY AI MATURITY ASSESSMENT RUMAH SAKIT - Form responses.csv')
            st.info("📁 Menggunakan file CSV lokal (format baru) sebagai fallback")
            
            # Apply same column renaming for local file
            if 'Skor Dimensi 1' in df.columns:
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
            
            return df
        except FileNotFoundError:
            # Try old format file as secondary fallback
            try:
                df = pd.read_csv('Test Survey - Form responses.csv')
                st.info("📁 Menggunakan file CSV lokal (format lama) sebagai fallback")
                return df
            except FileNotFoundError:
                st.error("❌ File CSV lokal juga tidak ditemukan.")
                st.info("💡 **Cara mengatasi masalah ini:**")
                st.info("1. Pastikan Google Sheets dapat diakses publik:")
                st.info("   - Buka sheet → File → Share → 'Anyone with the link can view'")
                st.info("   - Atau: File → Publish to the web → Publish")
                st.info("2. Atau letakkan file 'SURVEY AI MATURITY ASSESSMENT RUMAH SAKIT - Form responses.csv' di direktori aplikasi")
                return None

def create_spider_chart(dimensions_data, submission_id):
    """Membuat spider chart untuk 5 dimensi"""
    
    categories = ['Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']
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
    max_val = max(dimensions_data[['Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']].values)
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_val + 2],
                tickfont=dict(size=12),
                gridcolor='lightgray'
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color='#1f4e79')
            )
        ),
        showlegend=True,
        title=dict(
            text=f"Analisis Dimensi",
            x=0.5,
            font=dict(size=18, color='#1f4e79')
        ),
        font=dict(size=12),
        paper_bgcolor='white',
        plot_bgcolor='white'
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
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("**🏥 Informasi Rumah Sakit**")
        st.write(f"**Nama RS:** {submission_data['Nama Rumah Sakit']}")
        st.write(f"**Lokasi:** {submission_data['Lokasi Rumah Sakit']}")
        st.write(f"**Jumlah Tempat Tidur:** {submission_data['Jumlah Tempat Tidur']}")
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
        'Dimensi 1': 0.25,  # Data & Infrastruktur - 25%
        'Dimensi 2': 0.20,  # SDM & Kompetensi - 20%
        'Dimensi 3': 0.25,  # Leadership & Strategi - 25%
        'Dimensi 4': 0.20,  # Implementasi Use Case AI - 20%
        'Dimensi 5': 0.10   # Tata Kelola & Etika - 10%
    }
    
    # Nama dimensi yang lebih deskriptif
    dimension_names = {
        'Dimensi 1': 'Data & Infrastruktur',
        'Dimensi 2': 'SDM & Kompetensi',
        'Dimensi 3': 'Leadership & Strategi',
        'Dimensi 4': 'Implementasi Use Case AI',
        'Dimensi 5': 'Tata Kelola & Etika'
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
    
    if 15 <= scaled_score <= 27:
        return {
            'level': 1,
            'name': 'Awareness',
            'description': 'RS baru menyadari potensi AI',
            'characteristics': [
                'Belum ada inisiatif konkret',
                'Fokus: Education dan awareness building'
            ],
            'next_steps': [
                'Edukasi manajemen dan staf mengenai potensi AI di layanan kesehatan',
                'Selenggarakan workshop atau webinar pengenalan AI',
                'Petakan area sederhana yang cocok untuk dijadikan pilot project'
            ],
            'color': '#ff6b6b'
        }
    elif 28 <= scaled_score <= 39:
        return {
            'level': 2,
            'name': 'Exploration',
            'description': 'Pilot project terbatas dan eksperimen awal',
            'characteristics': [
                'Investasi minimal untuk proof of concept',
                'Fokus: Learning dan experimentation'
            ],
            'next_steps': [
                'Implementasikan 1–2 pilot project AI di area terbatas',
                'Tinjau hasil dan dokumentasikan pembelajaran yang diperoleh',
                'Susun strategi awal untuk pengembangan AI ke depan'
            ],
            'color': '#ffa726'
        }
    elif 40 <= scaled_score <= 51:
        return {
            'level': 3,
            'name': 'Implementation',
            'description': 'Beberapa solusi AI berjalan operasional',
            'characteristics': [
                'Mulai ada governance dan standar',
                'Fokus: Standardisasi dan integrasi sistem'
            ],
            'next_steps': [
                'Standarkan proses AI yang sudah berjalan agar lebih stabil',
                'Bentuk tim internal yang bertanggung jawab atas tata kelola AI',
                'Perluas penerapan AI ke unit atau proses lainnya'
            ],
            'color': '#66bb6a'
        }
    elif 52 <= scaled_score <= 63:
        return {
            'level': 4,
            'name': 'Scale-Up',
            'description': 'AI terintegrasi dalam operasional utama',
            'characteristics': [
                'Ada strategy roadmap dan resource dedicated',
                'Fokus: Optimisasi dan ekspansi'
            ],
            'next_steps': [
                'Susun roadmap strategis untuk implementasi AI secara menyeluruh',
                'Perkuat kompetensi SDM melalui pelatihan dan perekrutan khusus',
                'Bangun sistem pemantauan berkala untuk mengevaluasi dampak AI'
            ],
            'color': '#42a5f5'
        }
    elif 64 <= scaled_score <= 75:
        return {
            'level': 5,
            'name': 'Transformation',
            'description': 'AI menjadi core competitive advantage',
            'characteristics': [
                'Continuous innovation dan improvement',
                'Fokus: Leadership dan best practices'
            ],
            'next_steps': [
                'Jadikan RS sebagai pusat unggulan (center of excellence) untuk AI',
                'Bentuk unit riset atau laboratorium AI internal',
                'Berkolaborasi dengan RS lain dan institusi riset untuk berbagi praktik terbaik'
            ],
            'color': '#ab47bc'
        }
    else:
        return {
            'level': 0,
            'name': 'Invalid',
            'description': f'Skor tidak valid: {scaled_score:.2f} (dari weighted: {score:.2f})',
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
            label="SKOR MENTAH TOTAL",
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
        (1, "Awareness", "15-27", "#ff6b6b"),
        (2, "Exploration", "28-39", "#ffa726"),
        (3, "Implementation", "40-51", "#66bb6a"),
        (4, "Scale-Up", "52-63", "#42a5f5"),
        (5, "Transformation", "64-75", "#ab47bc")
    ]
    
    for level_num, level_name, score_range, color in all_levels:
        is_current = level_num == maturity_level['level']
        border_style = f"border: 3px solid {color};" if is_current else f"border: 1px solid {color};"
        opacity = "1" if is_current else "0.7"
        
        # Convert raw score range (15-75) to weighted score range (0-15) for proper level calculation
        raw_score_avg = (int(score_range.split('-')[0]) + int(score_range.split('-')[1])) / 2
        weighted_score_avg = (raw_score_avg - 15) / 60 * 15  # Convert 15-75 range to 0-15 range
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
                Level {level_num}: {level_name} (Skor {score_range})
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

def get_submission_id_from_url():
    """Mengambil submission ID dari parameter URL"""
    try:
        # For Streamlit 1.28.1, use experimental method
        query_params = st.experimental_get_query_params()
        submission_id = query_params.get('submission_id', [None])[0]
        return submission_id
    except Exception as e:
        return None

def main():
    # Load data
    df = load_data()
    if df is None:
        st.error("Tidak dapat memuat data. Silakan periksa koneksi internet dan coba lagi.")
        if st.button("🔄 Coba Lagi"):
            st.rerun()
        return
    
    # Main header
    st.markdown('<div class="main-header">Hasil Survei AI Maturity Assesment Rumah Sakit</div>', unsafe_allow_html=True)
    
    # Check if submission_id is provided in URL
    submission_id_from_url = get_submission_id_from_url()
    
    # Get list of submission IDs
    submission_ids = df['Submission ID'].astype(str).tolist()
    
    # Determine which submission to show
    if submission_id_from_url and submission_id_from_url in submission_ids:
        selected_submission = submission_id_from_url
    else:
        if submission_id_from_url:
            st.error(f"❌ Submission ID '{submission_id_from_url}' tidak ditemukan!")
        
        # Create a selection interface at the top
        st.markdown("### 🔍 Pilih Submission")
        selected_submission = st.selectbox(
            "Pilih Submission ID:",
            options=submission_ids,
            index=0,
            format_func=lambda x: f"Submission {x}"
        )
    
    # URL info and statistics
    # col1, col2 = st.columns([2, 1])
    # with col1:
    #     current_url = f"http://localhost:8501"
    #     example_url = f"{current_url}/?submission_id={selected_submission}"
    
    # Get the selected submission data
    submission_data = df[df['Submission ID'].astype(str) == selected_submission].iloc[0]
    
    # Display submission details
    display_submission_details(submission_data)
    
    # Create and display spider chart
    st.markdown("---")
    st.markdown('<div class="submission-header">Analisis Dimensi</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
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
            
    with col2:
        spider_fig = create_spider_chart(submission_data, selected_submission)
        st.plotly_chart(spider_fig, use_container_width=True)
    
    
    # AI Maturity Analysis
    display_ai_maturity_analysis(submission_data)
    
    # Raw data section (expandable)
    with st.expander("🔍 Lihat Data Survey Lengkap"):
        # Filter out dimension columns for better readability
        display_columns = [col for col in df.columns if not col.startswith('Dimensi') and col != 'Submission ID']
        display_data = submission_data[display_columns].to_frame().T
        st.dataframe(display_data, use_container_width=True)
    
    # All submissions overview
    # st.markdown("---")
    # st.markdown("### 📊 Ringkasan Semua Submission")
    
    # if st.checkbox("Tampilkan perbandingan semua submission"):
    #     # Create comparison chart
    #     fig_comparison = go.Figure()
        
    #     for idx, row in df.iterrows():
    #         values = [row['Dimensi 1'], row['Dimensi 2'], row['Dimensi 3'], row['Dimensi 4'], row['Dimensi 5']]
    #         values += values[:1]  # Close the chart
    #         categories = ['Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5'] + ['Dimensi 1']
            
    #         fig_comparison.add_trace(go.Scatterpolar(
    #             r=values,
    #             theta=categories,
    #             fill='toself',
    #             name=f"{row['Nama Responden']} ({row['Submission ID']})",
    #             opacity=0.7
    #         ))
        
    #     fig_comparison.update_layout(
    #         polar=dict(
    #             radialaxis=dict(
    #                 visible=True,
    #                 range=[0, df[['Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']].max().max() + 2]
    #             )
    #         ),
    #         showlegend=True,
    #         title="Perbandingan Semua Submission",
    #         height=600
    #     )
        
    #     st.plotly_chart(fig_comparison, use_container_width=True)

if __name__ == "__main__":
    main()
