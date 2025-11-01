import streamlit as st
import pandas as pd
import numpy as np
import io
import json
import datetime
import plotly.express as px

st.set_page_config(page_title="AI — Микробиом (КОЕ/г)",
                   page_icon="🧫", layout="centered")

# Logo centered at top
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.image("logo.png", width=160)
st.markdown("</div>", unsafe_allow_html=True)

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

# Baseline (примерные референсные значения, КОЕ/г)
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

# Antibiotics group (multiple allowed)
ab_factors = st.multiselect(
    "Антибиотики (можно несколько):",
    [
        "Антибиотики (широкого спектра)",
        "Антибиотики (узкого спектра)"
    ]
)

# Other medications
med_factors = st.multiselect(
    "Другие лекарства (можно несколько):",
    [
        "Приём антацидов / PPI",
        "Иммунодефицит / химиотерапия"
    ]
)

# Lifestyle and conditions
other_factors = st.multiselect(
    "Образ жизни и состояние:",
    [
        "Пробиотики (курс)",
        "Неправильное питание (высокожировая, мало клетчатки)",
        "Здоровая диета (богатая клетчаткой)",
        "Хронический стресс",
        "Недосып / нерегулярный сон",
        "Интенсивная физ. нагрузка",
        "Длительная госпитализация / ИВЛ"
    ]
)

# Merge selected factors
factors = ab_factors + med_factors + other_factors

# Sliders duration for antibiotics and probiotics
col1, col2 = st.columns(2)
with col1:
    ab_days = st.slider("Длительность антибиотиков (если выбраны)", 0, 21, 7)
with col2:
    probiotic_course_days = st.slider("Длительность курса пробиотиков (если выбраны)", 0, 30, 14)

# Effects dictionary (UNCHANGED)
effects = {
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

# Duration scaling (UNCHANGED)
def duration_scale_ab(days):
    return min(1.0, days / 14.0)

def duration_scale_pro(days):
    return min(1.0, days / 14.0)

# Simulation logic (UNCHANGED)
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
            applied = effects[f]
            scale = duration_scale_pro(probiotic_days)
            for k, v in applied.items():
                mult[k] *= (1 + (v - 1) * scale)
        else:
            eff = effects[f]
            for k, v in eff.items():
                mult[k] *= v

    for k in result:
        result[k] = max(0.0, result[k] * mult[k])

    return result, mult

simulated, multipliers = simulate(baseline, factors, ab_days, probiotic_course_days)

# Data output (UNCHANGED)
df = pd.DataFrame([
    {"Bacteria": k,
     "Baseline (KOE/g)": baseline[k],
     "Multiplier": multipliers[k],
     "Simulated (KOE/g)": simulated[k]}
    for k in baseline.keys()
])

def sci(x):
    return "{:.3e}".format(x)

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
             log_y=True,
             height=450)
st.plotly_chart(fig, use_container_width=True)

# Conclusion (UNCHANGED)
def analyze(updated_dict):
    msgs = []
    for k in baseline:
        base = baseline[k]
        val = updated_dict[k]
        if val <= base * 0.2:
            msgs.append(f"Резкое снижение {k} (≤20% от базового уровня).")
        elif val <= base * 0.6:
            msgs.append(f"Умеренное снижение {k} (20–60% от базового).")
        elif val >= base * 5:
            msgs.append(f"Выраженное увеличение {k} (≥5× базового) — возможна переколонизация условно-патогенных микроорганизмов.")
        elif val >= base * 1.5:
            msgs.append(f"Умеренное увеличение {k} (1.5–5× базового).")

    conclusions = []
    lacto = updated_dict["Lactobacillus spp."]
    bifi = updated_dict["Bifidobacterium spp."]
    clost = updated_dict["Clostridium spp."]
    proteo = updated_dict["Proteobacteria (проч.)"]
    candida = updated_dict["Candida spp. (дрожжепод.)"]

    if lacto < baseline["Lactobacillus spp."] * 0.5 and bifi < baseline["Bifidobacterium spp."] * 0.5:
        conclusions.append("Патерн: снижение основных симбионтов (Lactobacillus и Bifidobacterium) — риск дисбактериоза.")
    if proteo > baseline["Proteobacteria (проч.)"] * 2.0:
        conclusions.append("Увеличение Proteobacteria — маркер воспаления/дисбиоза.")
    if candida > baseline["Candida spp. (дрожжепод.)"] * 5:
        conclusions.append("Сильный рост Candida — риск кандидоза.")
    if clost > baseline["Clostridium spp."] * 5:
        conclusions.append("Увеличение Clostridium — риск токсигенного разрастания.")

    if not conclusions:
        conclusions.append("Серьёзных отклонений не выявлено.")

    final = "Автоматическое заключение:\n\n"
    final += "\n".join(msgs[:6]) + ("\n\n" if msgs else "")
    final += "\n".join(conclusions)
    final += "\n\nРекомендации:\n- Коррекция факторов (диета/сон/стресс).\n- При выраженных отклонениях: консультация и углублённая диагностика.\n"
    return final

conclusion_text = analyze(simulated)

st.subheader("Интерпретация и рекомендации")
st.write(conclusion_text)

# Downloads (UNCHANGED)
csv_buf = io.StringIO()
df.to_csv(csv_buf, index=False)
csv_bytes = csv_buf.getvalue().encode()

report = {
    "author": "Камалов Жандос",
    "group": "Мед24-015",
    "university": "Медицинский университет имени С. Д. Асфендиярова",
    "datetime": datetime.datetime.utcnow().isoformat() + "Z",
    "factors": factors,
    "antibiotics_days": ab_days,
    "probiotic_days": probiotic_course_days,
    "results": {row["Bacteria"]: row["Simulated (KOE/g)"] for _, row in df.iterrows()},
    "conclusion": conclusion_text
}
report_txt = f"Отчёт по симуляции\nАвтор: {report['author']} ({report['group']})\n{report['university']}\nДата (UTC): {report['datetime']}\n\nФакторы: {', '.join(factors) if factors else '—'}\n\nРезультаты (Simulated КОЕ/г):\n"
for k, v in report["results"].items():
    report_txt += f" - {k}: {v:.3e} КОЕ/г\n"
report_txt += "\n" + report["conclusion"]

st.download_button("⬇ Скачать CSV результатов", data=csv_bytes, file_name="microbiome_results.csv", mime="text/csv")
st.download_button("⬇ Скачать отчёт (.txt)", data=report_txt, file_name="microbiome_report.txt", mime="text/plain")

st.markdown("<hr><div style='text-align:center; color:gray'>Учебный симулятор — не клиническое заключение.</div>", unsafe_allow_html=True)

