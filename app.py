import streamlit as st
import dropbox
import pandas as pd
import re
from datetime import datetime

# --- KONFIGURACIJA ---
DROPBOX_APP_KEY = 'jopzf5dk00jr9q5'
DROPBOX_APP_SECRET = 'fae1bztizc82j1c'
FILENAME_PATTERN = re.compile(r"(.+)_(\d{4}-\d{2}-\d{2})_(\d{4})(?:_(\d+s))?\.zip")

st.set_page_config(page_title="MySQL Monitor", layout="wide")

# CSS za bolji prikaz na mobilnom
st.markdown("""<style> .stDataFrame { width: 100%; } </style>""", unsafe_allow_html=True)

st.title("📊 MySQL Cloud Matrix 2026")

# Sidebar za podešavanja
with st.sidebar:
    st.header("Podešavanja")
    token = st.text_input("Dropbox Refresh Token", type="password")
    folder = st.text_input("Dropbox Folder", value="/")
    if st.button("SAČUVAJ I OSVEŽI"):
        st.rerun()

if not token:
    st.warning("Molimo unesite Dropbox Token u meniju sa leve strane.")
else:
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=token.strip(), 
                               app_key=DROPBOX_APP_KEY, 
                               app_secret=DROPBOX_APP_SECRET)
        
        path = "" if folder == "/" else folder
        res = dbx.files_list_folder(path)
        
        report_data = {}
        servers = set()
        dates = set()

        for entry in res.entries:
            if isinstance(entry, dropbox.files.FileMetadata):
                match = FILENAME_PATTERN.match(entry.name)
                if match:
                    s_name, s_date, s_time, s_dur = match.groups()
                    servers.add(s_name)
                    dates.add(s_date)
                    if s_name not in report_data: report_data[s_name] = {}
                    report_data[s_name][s_date] = f"✅ {entry.size/(1024*1024):.1f}MB"

        # Formiranje tabele (zadnjih 5 dana)
        sorted_dates = sorted(list(dates), reverse=True)[:5]
        table_rows = []
        for s in sorted(list(servers)):
            row = {"SERVER": s.upper()}
            for d in sorted_dates:
                row[d] = report_data.get(s, {}).get(d, "❌ FALI")
            table_rows.append(row)

        df = pd.DataFrame(table_rows)
        st.table(df) # Koristimo st.table za fiksni prikaz na mobilnom

    except Exception as e:
        st.error(f"Greška prilikom povezivanja: {e}")