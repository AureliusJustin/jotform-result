import pandas as pd

# Test loading the new CSV format
try:
    df = pd.read_csv('SURVEY AI MATURITY ASSESSMENT RUMAH SAKIT - Form responses.csv')
    print("Successfully loaded new CSV format")
    print("Columns:", list(df.columns))
    print("\nFirst few columns with 'Skor' or ':':", [col for col in df.columns if 'Skor' in col or ':' in col])
    
    # Test the renaming logic
    if 'Skor Dimensi 1' in df.columns:
        df_renamed = df.rename(columns={
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
        
        print("\nAfter renaming, expected columns exist:")
        required_cols = ['Submission ID', 'Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']
        for col in required_cols:
            print(f"  {col}: {'✓' if col in df_renamed.columns else '✗'}")
        
        print("\nSample data:")
        print(df_renamed[['Nama Responden', 'Dimensi 1', 'Dimensi 2', 'Dimensi 3', 'Dimensi 4', 'Dimensi 5']].head())
        
except Exception as e:
    print(f"Error loading CSV: {e}")
