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

# ✅ LOGO centered
st.markdown("""
    <div style='text-align:center; margin-top:10px;'>
        <img src='logo.png' width='120'>
    </div>
""", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div style="text-align:center">
        <h3>Медицинский университет имени С. Д. Асфендиярова</h3>
        <div style="font-size:16px"><b>Камалов Жандос — Мед24-015</b></div>
    </div>
    <hr>
    """, unsafe_allow_html=True
)

st.title("🧬 Симулятор состава кишечного микробиома (КОЕ/г)")

st.write("Выбери факторы (несколько) — приложение покажет изменившиеся концентрации основных групп бактерий в КОЕ/г и выдаст диагностическое заключение.")

# Baseline values
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

# ✅ конкретные лекарства
factors = st.multiselect(
    "Факторы (выбери один или несколько):",
    [
        # ✅ антибиотики
        "Амоксициллин",
        "Ципрофлоксацин",
        "Азитромицин",

        # ✅ другие лекарства
        "Ибупрофен",
        "Метформин",
        "Антациды / PPI",

        # остальное как было
        "Пробиотики (курс)",
        "Неправильное питание (высокожировая, мало клетчатки)",
        "Здоровая диета (богатая клетчаткой)",
        "Хронический стресс",
        "Недосып / нерегулярный сон",
        "Интенсивная физ. нагрузка",
        "Длительная госпитализация / ИВЛ",
        "Иммунодефицит / химиотерапия"
    ]
)

col1, col2 = st.columns(2)
with col1:
    ab_days = st.slider("Длительность антибиотиков (если выбраны)", 0, 21, 7)
with col2:
    probiotic_course_days = st.slider("Длительность курса пробиотиков (если выбраны)", 0, 30, 14)

# ✅ Обновлённые эффекты антибиотиков/лекарств
effects = {
    "Амоксициллин": {
        "Lactobacillus spp.": 0.3,
        "Bifidobacterium spp.": 0.4,
        "Firmicutes (общие)": 0.8,
        "Proteobacteria (проч.)": 1.5,
        "Candida spp. (дрожжепод.)": 3.0
    },
    "Ципрофлоксацин": {
        "Lactobacillus spp.": 0.2,
        "Bifidobacterium spp.": 0.2,
        "Escherichia coli (комменсаль)": 0.1,
        "Proteobacteria (проч.)": 2.5,
        "Candida spp. (дрожжепод.)": 4.0
    },
    "Азитромицин": {
        "Lactobacillus spp.": 0.5,
        "Bifidobacterium spp.": 0.6,
        "Proteobacteria (проч.)": 2.0,
        "Clostridium spp.": 1.5,
        "Candida spp. (дрожжепод.)": 3.0
    },
    "Ибупрофен": {
        "Proteobacteria (проч.)": 1.4,
        "Clostridium spp.": 1.3
    },
    "Метформин": {
        "Bifidobacterium spp.": 1.4,
        "Firmicutes (общие)": 0.9
    },
    "Антациды / PPI": {
        "Proteobacteria (проч.)": 1.6,
        "Escherichia coli (комменсаль)": 1.3,
        "Candida spp. (дрожжепод.)": 2.0
    },
    "Пробиотики (курс)": {
        "Lactobacillus spp.": 2.0,
        "Bifidobacterium spp.": 1.6,
        "Firmicutes (общие)": 1.05
    },
    "Неправильное питание (высокожировая, мало клетчатки)": {
        "Lactobacillus spp.": 0.6,
        "Bifidobacterium spp.": 0.5
    },
    "Здоровая диета (богатая клетчаткой)": {
        "Lactobacillus spp.": 1.3,
        "Bifidobacterium spp.": 1.5
    },
    "Хронический стресс": {
        "Lactobacillus spp.": 0.8
    },
    "Недосып / нерегулярный сон": {
        "Lactobacillus spp.": 0.9
    },
    "Интенсивная физ. нагрузка": {
        "Firmicutes (общие)": 1.05
    },
    "Длительная госпитализация / ИВЛ": {
        "Proteobacteria (проч.)": 3.0
    },
    "Иммунодефицит / химиотерапия": {
        "Lactobacillus spp.": 0.5,
        "Proteobacteria (проч.)": 2.5
    }
}

def duration_scale_ab(days):
    return min(1.0, days / 14.0)

def duration_scale_pro(days):
    return min(1.0, days / 14.0)

def simulate(baseline, factors, ab_days=0, probiotic_days=0):
    result = baseline.copy()
    mult = {k: 1.0 for k in baseline.keys()}

    for f in factors:
        if f in ["Амоксициллин", "Ципрофлоксацин", "Азитромицин"]:
            scale = duration_scale_ab(ab_days)
            for k, v in effects[f].items():
                mult[k] *= (1 + (v - 1) * scale)
        elif f == "Пробиотики (курс)":
            scale = duration_scale_pro(probiotic_days)
            for k, v in effects[f].items():
                mult[k] *= (1 + (v - 1) * scale)
        else:
            for k, v in effects.get(f, {}).items():
                mult[k] *= v

    for k in baseline:
        result[k] = baseline[k] * mult[k]

    return result, mult

simulated, multipliers = simulate(baseline, factors, ab_days, probiotic_course_days)

df = pd.DataFrame([
    {"Bacteria": k,
     "Baseline (KOE/g)": baseline[k],
     "Multiplier": multipliers[k],
     "Simulated (KOE/g)": simulated[k]}
    for k in baseline.keys()
])

def sci(x): return "{:.3e}".format(x)

df_display = df.copy()
df_display["Baseline (KOE/g)"] = df_display["Baseline (KOE/g)"].apply(sci)
df_display["Simulated (KOE/g)"] = df_display["Simulated (KOE/g)"].apply(sci)
df_display["Multiplier"] = df_display["Multiplier"].apply(lambda x: f"{x:.2f}×")

st.subheader("Результаты (таблица)")
st.dataframe(df_display.set_index("Bacteria"))

st.subheader("Графическое распределение (логарифмическая шкала)")
plot_df = df[["Bacteria", "Simulated (KOE/g)"]].copy()
plot_df["Simulated (KOE/g)"] = plot_df["Simulated (KOE/g)"].astype(float)
fig = px.bar(plot_df, x="Bacteria", y="Simulated (KOE/g)",
             labels={"Simulated (KOE/g)": "КОЕ/г"},
             log_y=True, height=450)
st.plotly_chart(fig, use_container_width=True)

def analyze(updated_dict):
    msgs = []
    for k in baseline:
        base = baseline[k]
        val = updated_dict[k]
        if val <= base * 0.2:
            msgs.append(f"Резкое снижение {k} (≤20% от базового уровня).")

    final = "Автоматическое заключение:\n\n"
    final += "\n".join(msgs) + "\n"
    return final

conclusion_text = analyze(simulated)

st.subheader("Интерпретация и рекомендации")
st.write(conclusion_text)

csv_buf = io.StringIO()
df.to_csv(csv_buf, index=False)
csv_bytes = csv_buf.getvalue().encode()

st.download_button("⬇ Скачать CSV результатов", data=csv_bytes,
                   file_name="microbiome_results.csv", mime="text/csv")

st.markdown("<hr><div style='text-align:center; color:gray'>Учебный симулятор — не клиническое заключение.</div>", unsafe_allow_html=True)
