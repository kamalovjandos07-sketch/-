import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI — Микробиом", page_icon="🧫")

# ---------- LOGO CENTER ----------
st.markdown(
    """
    <div style="text-align:center">
        <img src="logo.png" width="90">
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- TITLE ----------
st.markdown(
    """
    <div style="text-align:center">
        <h3>Медицинский университет имени С. Д. Асфендиярова</h3>
        <div style="font-size:16px"><b>Камалов Жандос — Мед24-015</b></div>
        <div style="font-size:14px;color:gray">
            Микробиология, вирусология кафедрасы<br>
            PhD, доценті Игисенова А.И.
        </div>
    </div>
    <hr>
    """, unsafe_allow_html=True
)

st.title("🧬 Симулятор микробиома кишечника (КОЕ/г)")

# ---------- BASELINE ----------
baseline = {
    "Lactobacillus spp.": 1e8,
    "Bifidobacterium spp.": 5e9,
    "Firmicutes общие": 1e10,
    "Bacteroides spp.": 5e9,
    "Clostridium spp.": 1e6,
    "E. coli комменсальные": 1e7,
    "Proteobacteria проч.": 1e6,
    "Candida spp.": 1e4,
}

# ---------- FACTORS ----------
factors_choice = st.multiselect(
    "📌 Общие факторы:",
    [
        "Неправильное питание",
        "Здоровая диета",
        "Стресс",
        "Недосып",
        "Интенсивная физ. нагрузка",
    ]
)

# ---------- DRUGS ----------
abx = st.multiselect(
    "💊 Антибиотики:",
    [
        "Амоксициллин/клавуланат",
        "Цефтриаксон",
    ]
)
ab_days = st.slider("Длительность антибиотиков (дни):", 0, 14, 0)

other = st.multiselect(
    "💉 Другие лекарства:",
    ["ИПП", "НПВС", "ГКС"]
)

# ---------- EFFECTS ----------
effects = {
    "Неправильное питание": {"Bifidobacterium spp.": 0.6},
    "Здоровая диета": {"Bifidobacterium spp.": 1.4},
    "Стресс": {"Lactobacillus spp.": 0.8},

    "Амоксициллин/клавуланат": {"Bifidobacterium spp.": 0.2},
    "Цефтриаксон": {"Bacteroides spp.": 0.4},

    "ИПП": {"Candida spp.": 2},
    "НПВС": {"Proteobacteria проч.": 1.3},
    "ГКС": {"Lactobacillus spp.": 0.7},
}

# ---------- SIMULATION ----------
sim = baseline.copy()

def apply_effects(selected, duration=1):
    for item in selected:
        if item in effects:
            for k,v in effects[item].items():
                sim[k] *= (1 + (v - 1)*duration)

apply_effects(factors_choice, 1)
apply_effects(abx, ab_days/14)
apply_effects(other, 1)

# ---------- REPORT TABLE ----------
df = pd.DataFrame({
    "Микроорганизм": sim.keys(),
    "КОЕ/г": sim.values()
})
st.subheader("📋 Симулированные значения")
st.dataframe(df, use_container_width=True)

# ---------- GRAPH ----------
st.subheader("📊 График (логарифмический масштаб)")
fig = px.bar(df, x="Микроорганизм", y="КОЕ/г", log_y=True)
st.plotly_chart(fig, use_container_width=True)

# ---------- FOOTER ----------
st.markdown("<hr><center><i>Учебный симулятор</i></center>", unsafe_allow_html=True)
