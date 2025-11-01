# app.py
import streamlit as st
import pandas as pd
import numpy as np
import io
import json
import datetime
import plotly.express as px

st.set_page_config(page_title="AI — Микробиом (КОЕ/г)",
                   page_icon="🧫", layout="centered")

# ====== CSS стиль ======
st.markdown("""
<style>
body {
    background-color: #f5f9ff;
}
h1, h2, h3, h4, h5 {
    color: #004b7f;
    text-align: center;
}
hr {
    border: 1px solid #b0d4ff;
}
div.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
.footer {
    text-align:center; 
    color:gray; 
    margin-top:30px;
}
.header-box {
    background-color: #e6f2ff; 
    padding: 15px; 
    border-radius: 15px; 
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.info-box {
    background-color: #f0f8ff; 
    padding: 10px; 
    border-left: 4px solid #0078d7;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ====== Заголовок ======
st.markdown("""
<div class="header-box">
    <h3>Медицинский университет имени С. Д. Асфендиярова</h3>
    <h4 style="margin-top:-10px;">Кафедра микробиологии и вирусологии</h4>
    <div style="font-size:16px;"><b>Камалов Жандос — Мед24-015</b></div>
    <div style="font-size:15px; margin-top:5px;">PhD, доцент — Игисенова А.И.</div>
</div>
<hr>
""", unsafe_allow_html=True)

# ====== Основная часть ======
st.title("🧬 Симулятор состава кишечного микробиома (КОЕ/г)")
st.markdown("""
<div class="info-box">
Выберите несколько факторов, чтобы смоделировать, как изменяются концентрации основных групп бактерий (КОЕ/г).
</div>
""", unsafe_allow_html=True)

# ====== Основная логика (не трогал) ======
baseline = {
    "Lactobacillus spp.": 1e8,
    "Bifidobacterium spp.": 5e9,
    "Firmicutes (общие)": 1e10,
    "Bacteroides spp.": 5e9,
    "Clostridium spp.": 1e6,
    "Escherichia coli (комменсаль)": 1e7,
    "Proteobacteria (проч.)": 1e6,
    "Candida spp. (дрожжепод.)": 1e4
}

factors = st.multiselect(
    "Факторы (выберите один или несколько):",
    [
        "Антибиотики (широкого спектра)",
        "Антибиотики (узкого спектра)",
        "Пробиотики (курс)",
        "Неправильное питание (высокожировая, мало клетчатки)",
        "Здоровая диета (богатая клетчаткой)",
        "Хронический стресс",
        "Недосып / нерегулярный сон",
        "Интенсивная физ. нагрузка",
        "Длительная госпитализация / ИВЛ",
        "Иммунодефицит / химиотерапия",
        "Приём антацидов / PPI"
    ],
    help="Можно выбрать несколько факторов — их эффекты комбинируются."
)

col1, col2 = st.columns(2)
with col1:
    ab_days = st.slider("Длительность антибиотиков (если выбраны)", 0, 21, 7)
with col2:
    probiotic_course_days = st.slider("Длительность курса пробиотиков (если выбраны)", 0, 30, 14)

# ====== Вся логика расчёта — та же ======
effects = {  # тот же словарь эффектов, что у тебя
    "Антибиотики (широкого спектра)": {
        "Lactobacillus spp.": 0.1,
        "Bifidobacterium spp.": 0.15,
        "Firmicutes (общие)": 0.5,
        "Bacteroides spp.": 0.4,
        "Clostridium spp.": 2.0,
        "Escherichia coli (комменсаль)": 1.5,
        "Proteobacteria (проч.)": 2.0,
        "Candida spp. (дрожжепод.)": 5.0
    },
    "Антибиотики (узкого спектра)": {
        "Lactobacillus spp.": 0.6,
        "Bifidobacterium spp.": 0.7,
        "Firmicutes (общие)": 0.9,
        "Bacteroides spp.": 0.9,
        "Clostridium spp.": 1.1,
        "Escherichia coli (комменсаль)": 1.1,
        "Proteobacteria (проч.)": 1.2,
        "Candida spp. (дрожжепод.)": 1.5
    },
    "Пробиотики (курс)": {
        "Lactobacillus spp.": 2.0,
        "Bifidobacterium spp.": 1.6,
        "Firmicutes (общие)": 1.05
    },
    "Неправильное питание (высокожировая, мало клетчатки)": {
        "Lactobacillus spp.": 0.6,
        "Bifidobacterium spp.": 0.5,
        "Firmicutes (общие)": 1.3,
        "Bacteroides spp.": 1.4,
        "Escherichia coli (комменсаль)": 1.2
    },
    "Здоровая диета (богатая клетчаткой)": {
        "Bifidobacterium spp.": 1.5,
        "Lactobacillus spp.": 1.3,
        "Firmicutes (общие)": 1.1,
        "Clostridium spp.": 0.8
    },
    "Хронический стресс": {
        "Lactobacillus spp.": 0.8,
        "Bifidobacterium spp.": 0.85,
        "Proteobacteria (проч.)": 1.4
    },
    "Недосып / нерегулярный сон": {
        "Lactobacillus spp.": 0.9,
        "Clostridium spp.": 1.1
    },
    "Интенсивная физ. нагрузка": {
        "Lactobacillus spp.": 1.1,
        "Bifidobacterium spp.": 1.1,
        "Firmicutes (общие)": 1.05
    },
    "Длительная госпитализация / ИВЛ": {
        "Proteobacteria (проч.)": 3.0,
        "Clostridium spp.": 2.0,
        "Candida spp. (дрожжепод.)": 10.0
    },
    "Иммунодефицит / химиотерапия": {
        "Lactobacillus spp.": 0.5,
        "Bifidobacterium spp.": 0.5,
        "Proteobacteria (проч.)": 2.5,
        "Candida spp. (дрожжепод.)": 5.0
    },
    "Приём антацидов / PPI": {
        "Proteobacteria (проч.)": 1.5,
        "Escherichia coli (комменсаль)": 1.3,
        "Candida spp. (дрожжепод.)": 2.0
    }
}

def duration_scale_ab(days): return min(1.0, days / 14.0)
def duration_scale_pro(days): return min(1.0, days / 14.0)

def simulate(baseline, factors, ab_days=0, probiotic_days=0):
    result = baseline.copy()
    mult = {k: 1.0 for k in baseline.keys()}
    for f in factors:
        if f.startswith("Антибиотики"):
            eff = effects[f]
            for k, v in eff.items():
                applied = 1 + (v - 1) * duration_scale_ab(ab_days)
                mult[k] *= applied
        elif f == "Пробиотики (курс)":
            eff = effects[f]
            for k, v in eff.items():
                mult[k] *= (1 + (v - 1) * duration_scale_pro(probiotic_days))
        else:
            eff = effects[f]
            for k, v in eff.items():
                mult[k] *= v
    for k in result:
        result[k] = max(0.0, result[k] * mult.get(k, 1.0))
    return result, mult

simulated, multipliers = simulate(baseline, factors, ab_days, probiotic_course_days)

df = pd.DataFrame([
    {"Bacteria": k, "Baseline (КОЕ/г)": baseline[k], "Multiplier": multipliers[k], "Simulated (КОЕ/г)": simulated[k]}
    for k in baseline.keys()
])
df_display = df.copy()
df_display["Baseline (КОЕ/г)"] = df_display["Baseline (КОЕ/г)"].apply(lambda x: f"{x:.3e}")
df_display["Simulated (КОЕ/г)"] = df_display["Simulated (КОЕ/г)"].apply(lambda x: f"{x:.3e}")
df_display["Multiplier"] = df_display["Multiplier"].apply(lambda x: f"{x:.2f}×")

st.subheader("📊 Таблица результатов")
st.dataframe(df_display.set_index("Bacteria"))

st.subheader("📈 Логарифмическая шкала распределения")
fig = px.bar(df, x="Bacteria", y="Simulated (КОЕ/г)", log_y=True, height=450)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<div class='footer'>Учебный симулятор — не клиническое заключение © Камалов Жандос</div>", unsafe_allow_html=True)

