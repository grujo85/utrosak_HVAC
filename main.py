import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime
from masinski_sistem import MasinskiSistem

# Konfiguracija stranice
st.set_page_config(page_title="MAŠINSKI-LOG PRO", layout="wide", initial_sidebar_state="expanded")

# Inicijalizacija klase
ms = MasinskiSistem()

# ==========================================
# SIDEBAR - ADMIN PANEL (Backup, Restore, Delete)
# ==========================================
with st.sidebar:
    st.header("⚙️ ADMINISTRACIJA")
    
    # BACKUP MEHANIZAM
    if os.path.exists(ms.db_name):
        with open(ms.db_name, "rb") as f:
            st.download_button(
                label="📥 PREUZMI BACKUP (.db)",
                data=f,
                file_name=f"backup_masinski_{datetime.now().strftime('%d_%m_%Y')}.db",
                mime="application/x-sqlite3",
                use_container_width=True
            )
    
    st.divider()
    
    # RESTORE MEHANIZAM
    uploaded_file = st.file_uploader("Restore baze", type="db")
    if uploaded_file is not None:
        if st.button("⚠️ POTVRDI RESTORE", use_container_width=True):
            with open(ms.db_name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Baza uspešno zamenjena!")
            st.rerun()
            
    st.divider()
    
    # BRISANJE SVEGA
    st.warning("Opasna zona")
    potvrda_brisanja = st.checkbox("Potvrđujem brisanje svih podataka")
    if potvrda_brisanja:
        if st.button("🔴 OBRIŠI CELU BAZU", use_container_width=True):
            ms.obrisi_sve()
            st.success("Baza je ispražnjena.")
            st.rerun()

# ==========================================
# GLAVNI EKRAN - UNOS PODATAKA
# ==========================================
st.title("🏗️ MAŠINSKI-LOG: Engineering Tracker")

with st.expander("📝 UNOS NOVE POZICIJE", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        datum = st.date_input("Datum", datetime.now()).strftime("%d.%m.%Y")
        sistem = st.selectbox("Sistem", list(ms.nomenklatura.keys()))
    with c2:
        pozicija = st.text_input("Lokacija/Pozicija (npr. Kotlarnica)")
        stavka = st.selectbox("Stavka materijala/rada", ms.nomenklatura[sistem])
    with c3:
        kol = st.number_input("Količina", min_value=0.0, step=0.1)
        jed = st.selectbox("Jedinica", ["m", "kom", "m²", "set", "kg", "h"])
    
    napomena = st.text_area("Napomena / Tehnički detalji")
    
    if st.button("💾 SAČUVAJ U BAZU", use_container_width=True):
        if pozicija:
            ms.dodaj_unos((datum, sistem, pozicija, stavka, kol, jed, napomena))
            st.rerun()
        else:
            st.error("Polje 'Pozicija' ne sme biti prazno!")

# ==========================================
# TABELA, EDITOVANJE I PDF
# ==========================================
with sqlite3.connect(ms.db_name) as conn:
    df_prikaz = pd.read_sql_query("SELECT * FROM dnevnik ORDER BY id DESC", conn)

if not df_prikaz.empty:
    st.divider()
    
    # KPI Metrike
    m1, m2, m3 = st.columns(3)
    m1.metric("Ukupno cevi", f"{df_prikaz[df_prikaz['jedinica'] == 'm']['kolicina'].sum():.1f} m")
    m2.metric("Ukupno m² kanala", f"{df_prikaz[df_prikaz['jedinica'] == 'm²']['kolicina'].sum():.1f} m²")
    m3.metric("Broj stavki", len(df_prikaz))
    
    # Interaktivni Editor
    edited_df = st.data_editor(
        df_prikaz, 
        use_container_width=True, 
        hide_index=True,
        num_rows="dynamic"
    )
    
    c_save, c_pdf = st.columns(2)
    
    if c_save.button("✅ SAČUVAJ IZMENE U TABELI", use_container_width=True):
        ms.azuriraj_bazu(edited_df)
        st.success("Promene sačuvane!")
        st.rerun()
        
    if c_pdf.button("📄 GENERIŠI I PREUZMI PDF", use_container_width=True):
        pdf_out = ms.generisi_pdf(edited_df)
        st.download_button(
            label="⬇️ Klikni za preuzimanje PDF-a",
            data=bytes(pdf_out),
            file_name=f"Izvestaj_{datetime.now().strftime('%d_%m')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.info("Baza podataka je prazna. Unesite podatke iznad.")
