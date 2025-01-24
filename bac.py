import streamlit as st
from boozelib import (
    get_blood_alcohol_content,
    get_blood_alcohol_degradation,
)

st.set_page_config(page_title="Calcolo Tasso Alcolemico", page_icon="🍺")

# Titolo dell'applicazione
st.title("🍻 **Calcolo del Tasso Alcolemico**")
st.write("""
Questa applicazione stima il tasso alcolemico (per mille) usando la libreria `boozelib`. 
Puoi aggiungere più bevande e vedere come cambiano i risultati nel tempo.
""")

# Input dati personali con icone
st.sidebar.header("⚙️ **Dati personali**")
age = st.sidebar.number_input("🎂 Età (anni)", min_value=18, max_value=100, value=30, step=1)
weight = st.sidebar.number_input("⚖️ Peso (kg)", min_value=30, max_value=200, value=70, step=1)
height = st.sidebar.number_input("📏 Altezza (cm)", min_value=120, max_value=250, value=170, step=1)
sex = st.sidebar.radio("👤 Sesso", ["Maschio ♂️", "Femmina ♀️"]).startswith("Femmina")

# Input parametro limite con icone
st.sidebar.header("🚦 **Parametri Limite**")
limite_bac = st.sidebar.number_input(
    "🔴 Limite tasso alcolemico (per mille)",
    min_value=0.0,
    max_value=1.0,
    value=0.4,
    step=0.01
)

# Gestione bevande con aggiornamento dinamico
st.header("🍹 **Bevande consumate**")

# Numero di bevande
if "numero_bevande" not in st.session_state:
    st.session_state.numero_bevande = 1

numero_bevande = st.number_input(
    "📋 Numero di bevande",
    min_value=1,
    max_value=20,
    value=st.session_state.numero_bevande,
    step=1,
    on_change=lambda: st.session_state.update({"numero_bevande": numero_bevande}),
)

# Inserimento dinamico delle bevande
bevande = []
for i in range(st.session_state.numero_bevande):
    st.write(f"🍹 **Bevanda {i + 1}**")
    volume = st.number_input(
        f"📏 Volume (ml) della bevanda {i + 1}",
        min_value=0,
        max_value=2000,
        value=500,
        step=10,
        key=f"volume_{i}"
    )
    percent = st.number_input(
        f"🍷 Gradazione alcolica (%) della bevanda {i + 1}",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.1,
        key=f"percent_{i}"
    )
    bevande.append({"volume": volume, "percent": percent})

# Tempo trascorso
tempo_ore = st.number_input("⏱️ Tempo trascorso dall'assunzione (ore)", min_value=0.0, max_value=24.0, value=2.0, step=0.1)

# Funzione per calcolare il tempo necessario per scendere sotto un certo limite
def calcola_tempo_per_limite(tasso_iniziale, limite, degr_per_ora, margine=0.075):
    if tasso_iniziale <= limite:
        return 0, 0  # Se il tasso è già sotto il limite, non è necessario alcun tempo
    tempo_ore = (tasso_iniziale - limite) / degr_per_ora
    tempo_minimo = max(tempo_ore * (1 - margine), 0)  # Margine inferiore
    tempo_massimo = tempo_ore * (1 + margine)  # Margine superiore
    return tempo_minimo, tempo_massimo  # Restituisce un range di tempo

# Funzione per convertire ore decimali in ore e minuti
def ore_minuti(tempo_ore):
    ore = int(tempo_ore)
    minuti = int((tempo_ore - ore) * 60)
    return ore, minuti

# Calcolo tasso alcolemico
bac_totale = 0
for bevanda in bevande:
    bac = get_blood_alcohol_content(
        age=age,
        weight=weight,
        height=height,
        sex=sex,
        volume=bevanda["volume"],
        percent=bevanda["percent"]
    )
    bac_totale += bac

# Calcolo riduzione nel tempo
minuti = int(tempo_ore * 60)
degradazione = get_blood_alcohol_degradation(
    age=age,
    weight=weight,
    height=height,
    sex=sex,
    minutes=minuti
)
bac_finale = max(bac_totale - degradazione, 0)

# Output risultati
st.subheader(f"📊 **Tasso Alcolemico Iniziale**: {bac_totale:.3f} per mille")
st.subheader(f"📉 **Tasso Alcolemico dopo {tempo_ore:.1f} ore**: {bac_finale:.3f} per mille")

# Messaggi sul limite legale
if bac_finale < 0.5:
    st.success("✅ Sei al di sotto del limite legale per la guida (0.5 per mille in Italia).")
elif 0.5 <= bac_finale < 0.8:
    st.warning("⚠️ Sei sopra il limite legale per la guida. Non metterti alla guida!")
else:
    st.error("🚨 Sei molto sopra il limite legale. Guidare è estremamente pericoloso!")

# Calcolo tempo per scendere sotto il limite
degr_per_ora = 0.15  # Velocità di degradazione media (g/L per ora)
tempo_min, tempo_max = calcola_tempo_per_limite(bac_finale, limite_bac, degr_per_ora)

if tempo_min > 0:
    ore_min, minuti_min = ore_minuti(tempo_min)
    ore_max, minuti_max = ore_minuti(tempo_max)
    st.write(f"⏳ Per arrivare sotto il limite di {limite_bac:.2f} per mille impiegherai circa tra "
             f"**{ore_min} ore e {minuti_min} minuti** e **{ore_max} ore e {minuti_max} minuti**.")
else:
    st.write(f"✅ Sei già sotto il limite di {limite_bac:.2f} per mille!")

st.write("**Nota:** Questo è solo un calcolo stimato e non tiene conto di tutti i fattori individuali.")
