import sqlite3
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

class MasinskiPDF(FPDF):
    def header(self):
        if os.path.exists("DejaVuSans.ttf"):
            self.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            self.set_font("DejaVu", "", 16)
        else:
            self.set_font("Helvetica", "B", 16)
        self.set_text_color(41, 128, 185)
        self.cell(0, 10, "IZVEŠTAJ MAŠINSKIH INSTALACIJA", ln=True, align="L")
        self.ln(10)

class MasinskiSistem:
    def __init__(self):
        self.db_name = "masinske_instalacije.db"
        self.nomenklatura = {
    "❄️ HVAC - VENTILACIJA": [
        "Pocinkovani kanal pravougaoni (m2)",
        "Spiro cev (okrugli kanal) fi 100-500",
        "Fleksibilno crevo izolovan (Sono)",
        "Protivpožarna klapna (PPK) ručna",
        "Protivpožarna klapna (PPK) sa motorom",
        "Regulaciona klapna (izolovan/neizolovan)",
        "Prigušivač buke (pravougaoni/okrugli)",
        "Anemostat plafonski (kom)",
        "Linijski difuzor (slot)",
        "Spoljna fiksna žaluzina",
        "Kuhinjska hauba (napa)",
        "Ventilator kanalski / krovni",
        "Filter za vazduh (G4/F7/Hepa)",
        "Izolacija samolepljiva guma (m2)"
    ],
    "🌡️ HVAC - KLIMATIZACIJA": [
        "VRF Spoljna jedinica",
        "VRF Unutrašnja (zidna/kasetna/kanalska)",
        "Split sistem (komplet)",
        "Fancoil (parapetni/kasetni/kanalski)",
        "Bakarna cev fi 6.35 - 35.0 (izolovana)",
        "Refnet račva za VRF",
        "Kondenz crevo fi 20/25/32",
        "Kondenzna pumpa",
        "Nosač spoljne jedinice (L-profil)",
        "Dopuna rashladnog fluida (R32/R410A) - kg"
    ],
    "🔥 GREJANJE I PODSTANICA": [
        "Bešavna cev crna DN15 - DN150",
        "AluPex cev (izolovana) fi 16-32",
        "Radijator panelni (tip 22/33)",
        "Radijator cevni - sušač",
        "Podno grejanje - cev PEX fi 16",
        "Razdelnik / Sabirnik sa ormarićem",
        "Termostatski ventil / glava",
        "Cirkulaciona pumpa (Grundfos/Wilo)",
        "Izmenjivač toplote (pločasti)",
        "Ekspanziona posuda (8L - 250L)",
        "Trokraci mešni ventil sa motorom",
        "Kalorimetar (ultrazvučni)",
        "Hvatač nečistoće / Odmuljivač",
        "Automatski odzračni lončić"
    ],
    "💦 VODOVOD I KANALIZACIJA": [
        "PPR cev (hladna/topla voda) fi 20-63",
        "PVC cev (odvodna) fi 50-160",
        "Niskošumna cev za vertikale",
        "Izolacija cevi (EPE / Filc)",
        "Vodokotlić ugradni (Geberit/Tece)",
        "Baterija (slavina) / Tuš usponski",
        "Sifon podni / Tuš kanalica",
        "Bojler električni (50L/80L)",
        "Glavni ventil sa točkom / kugla",
        "Hidrantni ormar (komplet)",
        "Pumpa za podizanje pritiska (Hidropak)"
    ],
    "🚿 SPRINKLER (PP ZAŠTITA)": [
        "Sprinkler cev DN25 - DN150 (bojena)",
        "Sprinkler mlaznica (stajaća/viseća) 68°C",
        "Victaulic spojnica (kruta/fleksibilna)",
        "Alarmni ventil (vlažni/suvi)",
        "Flow switch (indikator protoka)",
        "Test i drenažni ventil",
        "Nosač sprinkler cevi (obujmica)",
        "Hidrantsko crevo sa mlaznicom"
    ],
    "🛠️ MONTAŽA I RADOVI": [
        "Montaža i povezivanje opreme",
        "Zavarivanje (gasno/električno)",
        "Lemljenje bakarnih cevi",
        "Postavljanje izolacije",
        "Ispitivanje na pritisak (Zapisnik)",
        "Vakumiranje i punjenje freonom",
        "Ispiranje i dezinfekcija mreže",
        "Šemiranje komandnog ormana",
        "Bušenje proboja (opeka/beton)",
        "Šlicovanje zidova",
        "Balansiranje i puštanje u rad"
    ]
}
        self.inicijalizuj_db()

    def inicijalizuj_db(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS dnevnik 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                datum TEXT, sistem TEXT, pozicija TEXT, stavka TEXT, 
                kolicina REAL, jedinica TEXT, napomena TEXT)""")

    def dodaj_unos(self, podaci):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("INSERT INTO dnevnik (datum, sistem, pozicija, stavka, kolicina, jedinica, napomena) VALUES (?,?,?,?,?,?,?)", podaci)

    def azuriraj_bazu(self, df):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("DELETE FROM dnevnik")
            df.to_sql("dnevnik", conn, if_exists="append", index=False)

    def generisi_pdf(self, df):
        pdf = MasinskiPDF()
        pdf.add_page()
        font_res = "DejaVu" if os.path.exists("DejaVuSans.ttf") else "Helvetica"
        pdf.set_font(font_res, "", 9)
        # Header tabele
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(30, 10, "Datum", 1, 0, 'C', True)
        pdf.cell(80, 10, "Stavka", 1, 0, 'C', True)
        pdf.cell(30, 10, "Kol.", 1, 0, 'C', True)
        pdf.cell(30, 10, "Jed.", 1, 1, 'C', True)
        
        for _, row in df.iterrows():
            pdf.cell(30, 8, str(row['datum']), 1)
            pdf.cell(80, 8, str(row['stavka']), 1)
            pdf.cell(30, 8, str(row['kolicina']), 1, 0, 'C')
            pdf.cell(30, 8, str(row['jedinica']), 1, 1, 'C')
        return pdf.output()
