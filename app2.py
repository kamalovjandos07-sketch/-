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

# ===== HEADER WITH LOGO (CENTERED) =====
st.markdown(
    """
    <div style="text-align:center">
        <img src="logo.png" width="120">
        <h3>Медицинский университет имени С. Д. Асфендиярова</h3>
        <div style="font-size:16px"><b>Камалов Жандос — Мед24-015</b></div>
    </div>
    <hr>
    """, unsafe_allow_html=True
)

st.title("🧬 Симулятор состава кишечного микробиома (КОЕ/г)")
st.write("Выбери факторы — приложение покажет изменившиеся концентрации основных групп бактерий и выдаст интерпретацию.")

# ===== BASELINE =====
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

# ===== MULTISELECT FACTORS =====
st.subheader("Антибиотики")
antibiotics = st.multiselect(
    "Выбери используемые антибиотики:",
    [
        "Амоксициллин/Клавуланат",
        "Цефтриаксон",
        "Ципрофлоксацин",
        "Азитромицин",
        "Кларитромицин"
    ]
)

st.subheader("Другие лекарства")
other_meds = st.multiselect(
    "Выбери другие лекарства:",
    [
        "Ингибиторы протонной помпы (PPI)",
        "Глюкокортикоиды",
        "Химиотерапия"
    ]
)

st.subheader("Образ жизни / состояние")
factors = st.multiselect(
    "Факторы:",
    [
        "Неправильное питание",
        "Здоровая диета",
        "Хронический стресс",
        "Недосып",
        "Интенсивная физнагрузка",
        "Госпитализация/ИВЛ",
        "Иммунодефицит"
    ]
)

# ===== SLIDERS =====
col1, col2 = st.columns(2)
with col1:
    ab_days = st.slider("Длительность антибиотиков", 0, 21, 7)
with col2:
    probiotic_course_days = st.slider("Длительность пробиотиков", 0, 30, 14)

# ===== EFFECTS =====
effects = {
    "Амоксициллин/Клавуланат": {
        "Lactobacillus spp.": 0.3,
        "Bifidobacterium spp.": 0.4,
        "Proteobacteria (проч.)": 2.0,
        "Candida spp. (дрожжепод.)": 3.0
    },
    "Цефтриаксон": {
        "Lactobacillus spp.": 0.2,
        "Bifidobacterium spp.": 0.2,
        "Clostridium spp.": 3.0,
        "Proteobacteria (проч.)": 2.5,
        "Candida spp. (дрожжепод.)": 5.0
    },
    "Ципрофлоксацин": {
        "Firmicutes (общие)": 0.5,
        "Bacteroides spp.": 0.4,
        "Proteobacteria (проч.)": 3.0
    },
    "Азитромицин": {
        "Lactobacillus spp.": 0.5,
        "Bifidobacterium spp.": 0.5
    },
    "Кларитромицин": {
        "Lactobacillus spp.": 0.6,
        "Bifidobacterium spp.": 0.7
    },

    "Ингибиторы протонной помпы (PPI)": {
        "Proteobacteria (проч.)": 1.8,
        "Candida spp. (дрожжепод.)": 2.0
    },
    "Глюкокортикоиды": {
        "Proteobacteria (проч.)": 1.5,
        "Clostridium spp.": 1.5
    },
    "Химиотерапия": {
        "Lactobacillus spp.": 0.4,
        "Bifidobacterium spp.": 0.4,
        "Candida spp. (дрожжепод.)": 5.0
    },

    "Пробиотики": {
        "Lactobacillus spp.": 2.0,
        "Bifidobacterium spp.": 1.7
    },

    "Неправильное питание": {
        "Lactobacillus spp.": 0.6,
        "Bifidobacterium spp.": 0.5,
        "Firmicutes (общие)": 1.3
    },
    "Здоровая диета": {
        "Bifidobacterium spp.": 1.6,
        "Lactobacillus spp.": 1.3
    },
    "Хронический стресс": {
        "Lactobacillus spp.": 0.85,
        "Proteobacteria (проч.)": 1.4
    },
    "Недосып": {
        "Clostridium spp.": 1.3,
        "Lactobacillus spp.": 0.9
    },
    "Интенсивная физнагрузка": {
        "Lactobacillus spp.": 1.1,
        "Bifidobacterium spp.": 1.1
    },
    "Госпитализация/ИВЛ": {
        "Proteobacteria (проч.)": 3.0,
        "Candida spp. (дрожжепод.)": 10.0
    },
    "Иммунодефицит": {
        "Candida spp. (дрожжепод.)": 5.0,
        "Proteobacteria (проч.)": 2.5
    }
}

# ===== DURATION SCALING =====
def scale(days):
    return min(1.0, days / 14.0)

# ===== SIMULATION =====
def simulate():
    result = baseline.copy()
    mult = {k: 1.0 for k in baseline}

    # антибиотики
    for ab in antibiotics:
        for k, v in effects[ab].items():
            mult[k] *= (1 + (v - 1) * scale(ab_days))

    # пробиотики
    for k, v in effects["Пробиотики"].items():
        mult[k] *= (1 + (v - 1) * scale(probiotic_course_days))

    # другие лекарства + факторы
    for f in (other_meds + factors):
        for k, v in effects[f].items():
            mult[k] *= v

    for k in baseline:
        result[k] *= mult[k]
        result[k] = max(result[k], 0)

    return result, mult

simulated, multipliers = simulate()

# ===== TABLE =====
df = pd.DataFrame([
    {
        "Микроорганизм": k,
        "Базовый КОЕ/г": baseline[k],
        "Множитель": multipliers[k],
        "Симуляция КОЕ/г": simulated[k]
    }
    for k in baseline
])

def sci(x): return f"{x:.3e}"

df_display = df.copy()
df_display["Базовый КОЕ/г"] = df_display["Базовый КОЕ/г"].apply(sci)
df_display["Симуляция КОЕ/г"] = df_display["Симуляция КОЕ/г"].apply(sci)
df_display["Множитель"] = df_display["Множитель"].apply(lambda x: f"{x:.2f}×")

st.subheader("📊 Таблица результатов")
st.dataframe(df_display.set_index("Микроорганизм"))

# ===== PLOT =====
st.subheader("График (лог-шкала)")
fig = px.bar(df, x="Микроорганизм", y="Симуляция КОЕ/г", log_y=True)
st.plotly_chart(fig, use_container_width=True)

# ===== INTERPRETATION =====
def analyze():
    txt = []
    lacto = simulated["Lactobacillus spp."]
    bifi = simulated["Bifidobacterium spp."]
    cand = simulated["Candida spp. (дрожжепод.)"]
    proteo = simulated["Proteobacteria (проч.)"]
    clost = simulated["Clostridium spp."]

    if lacto < baseline["Lactobacillus spp."] * 0.6:
        txt.append("Снижение Lactobacillus — риск дисбиоза.")
    if bifi < baseline["Bifidobacterium spp."] * 0.6:
        txt.append("Снижение Bifidobacterium — нарушение резистентности.")
    if proteo > baseline["Proteobacteria (проч.)"] * 2:
        txt.append("Рост Proteobacteria — маркер воспаления.")
    if cand > baseline["Candida spp. (дрожжепод.)"] * 5:
        txt.append("Кандидоз-риск (рост Candida).")
    if clost > baseline["Clostridium spp."] * 5:
        txt.append("Подозрение на токсигенную Clostridium.")

    if not txt:
        txt.append("Микробиом выглядит стабильным.")

    return "\n".join(txt)

st.subheader("🩺 Интерпретация")
st.write(analyze())

# ===== DOWNLOAD =====
csv_buf = io.StringIO()
df.to_csv(csv_buf, index=False)

st.download_button(
    "⬇ Скачать CSV",
    data=csv_buf.getvalue().encode(),
    file_name="results.csv",
    mime="text/csv"
)

report_txt = analyze()
st.download_button(
    "⬇ Скачать отчёт",
    file_name="report.txt",
    mime="text/plain",
    data=report_txt
)

st.markdown("<hr><center>Учебный симулятор</center>", unsafe_allow_html=True)

