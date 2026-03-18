import streamlit as st
import pandas as pd
from datetime import datetime


# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="System Grafik PRO", layout="centered")


st.title("🛡️ System Zarządzania Grafikami v7.0")


# --- SŁOWNIK ŚWIĄT ---
SLOWNIK_SWIAT = {
    "Wszystkich Świętych": "01.11",
    "Święto Niepodległości": "11.11",
    "Boże Narodzenie": "25.12",
    "Drugi Dzień Świąt": "26.12",
    "Nowy Rok": "01.01",
    "Trzech Króli": "06.01"
}


# --- BOCZNY PANEL: WGRYWANIE PLIKU ---
st.sidebar.header("📁 Zarządzanie Bazą")
uploaded_file = st.sidebar.file_uploader("Wgraj plik grafik.txt", type=["txt"])


# --- FUNKCJA PRZETWARZANIA DANYCH ---
@st.cache_data # Przyspiesza działanie przy dużej bazie
def wczytaj_dane(file):
    rows = []
    content = file.read().decode("utf-8")
    for line in content.splitlines():
        if '|' in line:
            p = [i.strip() for i in line.split('|')]
            if len(p) >= 3:
                try:
                    dt = datetime.strptime(p[0], "%d.%m.%Y")
                    status = p[2].upper()
                    rows.append({
                        'Data': p[0],
                        'Data_Obj': dt,
                        'Miesiac_Rok': dt.strftime("%m.%Y"),
                        'Pracownik': p[1].upper(),
                        'Status': status,
                        'Czy_D': 'D' in status and 'HDK' not in status,
                        'Weekend': dt.weekday() >= 5
                    })
                except: continue
    df = pd.DataFrame(rows).drop_duplicates(subset=['Data', 'Pracownik'])
    return df


# --- GŁÓWNA LOGIKA APLIKACJI ---
if uploaded_file:
    df = wczytaj_dane(uploaded_file)
    st.success(f"Wczytano {len(df)} rekordów!")


    # 1. ILOŚĆ DYŻURÓW (Combobox w Streamlit to selectbox z filtrem)
    st.subheader("1. Ilość dyżurów")
    pracownicy = sorted(df['Pracownik'].unique())
    wybrany_pracownik = st.selectbox("Wybierz lub wpisz pracownika:", [""] + pracownicy)
    
    if wybrany_pracownik:
        wynik_osoba = df[(df['Pracownik'] == wybrany_pracownik) & (df['Czy_D'])]
        st.metric("Łączna liczba dyżurów (D)", len(wynik_osoba))
        st.dataframe(wynik_osoba[['Data', 'Status']], use_container_width=True)


    st.divider()


    # 2. KTO MA DZIŚ DYŻUR
    if st.button("2. Sprawdź: Kto ma dziś dyżur?"):
        dzis = datetime.now().strftime("%d.%m.%Y")
        # dzis = "18.03.2026" # Do testów
        wynik_dzis = df[(df['Data'] == dzis) & (df['Czy_D'])]
        if not wynik_dzis.empty:
            st.write(f"📅 Dyżury na dzień {dzis}:")
            st.table(wynik_dzis[['Pracownik', 'Status']])
        else:
            st.info(f"Nikt nie ma dyżuru na dzień {dzis}")


    st.divider()


    # 3. PRACA W WEEKENDY
    st.subheader("3. Praca w weekendy")
    miesiace = sorted(df['Miesiac_Rok'].unique(), reverse=True)
    wybrany_miesiac = st.selectbox("Wybierz miesiąc i rok:", ["-- Wybierz --"] + miesiace)
    
    if wybrany_miesiac != "-- Wybierz --":
        wynik_week = df[(df['Miesiac_Rok'] == wybrany_miesiac) & (df['Weekend']) & (df['Czy_D'])]
        st.dataframe(wynik_week[['Data', 'Pracownik', 'Status']].sort_values('Data'), use_container_width=True)


    st.divider()


    # 4. ŚWIĘTA (HISTORIA)
    st.subheader("4. Święta (historia lat)")
    wybrane_swieto = st.selectbox("Wybierz święto:", ["-- Wybierz --"] + list(SLOWNIK_SWIAT.keys()))
    
    if wybrane_swieto != "-- Wybierz --":
        kod = SLOWNIK_SWIAT[wybrane_swieto]
        wynik_swieta = df[(df['Data'].str.startswith(kod)) & (df['Czy_D'])]
        st.dataframe(wynik_swieta[['Data', 'Pracownik', 'Status']].sort_values('Data_Obj', ascending=False), use_container_width=True)


else:
    st.info("👈 Wgraj plik .txt w panelu bocznym, aby uruchomić system.")
