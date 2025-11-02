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

# Медицинский стиль - бело-зеленый
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fffe 0%, #f0fff0 50%, #f8fffe 100%);
        font-family: 'Arial', sans-serif;
    }
    .medical-header {
        background: linear-gradient(90deg, #228b22 0%, #32cd32 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        border-left: 8px solid #006400;
        box-shadow: 0 4px 8px rgba(0,100,0,0.2);
        margin-bottom: 25px;
    }
    .section-header {
        background: linear-gradient(90deg, #e8f5e8 0%, #f0fff0 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #228b22;
        margin: 20px 0 15px 0;
    }
    .stButton>button {
        background: linear-gradient(90deg, #228b22 0%, #32cd32 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #006400 0%, #228b22 100%);
        color: white;
    }
    .download-btn {
        background: linear-gradient(90deg, #1e90ff 0%, #00bfff 100%) !important;
    }
    .download-btn:hover {
        background: linear-gradient(90deg, #0066cc 0%, #0099cc 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True
)

# Красивый медицинский заголовок
st.markdown(
    """
    <div class="medical-header">
        <h2 style="margin:0; color:white; font-weight:bold;">Медицинский университет имени С. Д. Асфендиярова</h2>
        <div style="font-size:18px; margin-top:15px; font-weight:bold;">Камалов Жандос — Мед24-015</div>
        <div style="font-size:14px; margin-top:10px; opacity:0.9;">Кафедра микробиологии и вирусологии</div>
    </div>
    """, unsafe_allow_html=True
)

# Заголовок приложения
st.markdown('<div class="section-header"><h1 style="margin:0; color:#006400;">Симулятор состава кишечного микробиома (КОЕ/г)</h1></div>', unsafe_allow_html=True)

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

# Factors list с конкретными антибиотиками
st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">Выбор факторов влияния</h3></div>', unsafe_allow_html=True)

factors = st.multiselect(
    "**Факторы (выбери один или несколько):**",
    [
        "Амоксициллин/клавуланат (Аугментин)",
        "Цефтриаксон",
        "Азитромицин",
        "Левофлоксацин",
        "Метронидазол",
        "Ванкомицин (пероральный)",
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
    help="Можно выбрать несколько факторов — их эффекты комбинируются (мультипликативно)."
)

# Дополнительные параметры
st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">Параметры длительности</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    ab_days = st.slider("**Длительность антибиотиков (дни):**", 0, 21, 7, help="Продолжительность курса антибиотикотерапии")
with col2:
    probiotic_course_days = st.slider("**Длительность пробиотиков (дни):**", 0, 30, 14, help="Продолжительность приёма пробиотиков")

# Define multiplicative effects с конкретными антибиотиками
effects = {
    "Амоксициллин/клавуланат (Аугментин)": {
        "Lactobacillus spp.": 0.1, "Bifidobacterium spp.": 0.15, "Firmicutes (общие)": 0.5,
        "Bacteroides spp.": 0.4, "Clostridium spp.": 2.0, "Escherichia coli (комменсаль)": 1.5,
        "Proteobacteria (проч.)": 2.0, "Candida spp. (дрожжепод.)": 5.0
    },
    "Цефтриаксон": {
        "Lactobacillus spp.": 0.3, "Bifidobacterium spp.": 0.4, "Firmicutes (общие)": 0.7,
        "Bacteroides spp.": 0.6, "Clostridium spp.": 3.0, "Escherichia coli (комменсаль)": 0.8,
        "Proteobacteria (проч.)": 1.8, "Candida spp. (дрожжепод.)": 4.0
    },
    "Азитромицин": {
        "Lactobacillus spp.": 0.5, "Bifidobacterium spp.": 0.6, "Firmicutes (общие)": 0.8,
        "Bacteroides spp.": 0.7, "Clostridium spp.": 1.5, "Escherichia coli (комменсаль)": 1.2,
        "Proteobacteria (проч.)": 1.4, "Candida spp. (дрожжепод.)": 2.0
    },
    "Левофлоксацин": {
        "Lactobacillus spp.": 0.7, "Bifidobacterium spp.": 0.8, "Firmicutes (общие)": 0.9,
        "Bacteroides spp.": 0.8, "Clostridium spp.": 1.2, "Escherichia coli (комменсаль)": 0.5,
        "Proteobacteria (проч.)": 0.7, "Candida spp. (дрожжепод.)": 1.8
    },
    "Метронидазол": {
        "Lactobacillus spp.": 0.9, "Bifidobacterium spp.": 0.9, "Firmicutes (общие)": 1.0,
        "Bacteroides spp.": 0.3, "Clostridium spp.": 0.2, "Escherichia coli (комменсаль)": 1.1,
        "Proteobacteria (проч.)": 1.0, "Candida spp. (дрожжепод.)": 1.5
    },
    "Ванкомицин (пероральный)": {
        "Lactobacillus spp.": 1.0, "Bifidobacterium spp.": 1.0, "Firmicutes (общие)": 1.0,
        "Bacteroides spp.": 1.0, "Clostridium spp.": 0.1, "Escherichia coli (комменсаль)": 1.0,
        "Proteobacteria (проч.)": 1.0, "Candida spp. (дрожжепод.)": 1.2
    },
    "Пробиотики (курс)": {
        "Lactobacillus spp.": 2.0, "Bifidobacterium spp.": 1.6, "Firmicutes (общие)": 1.05
    },
    "Неправильное питание (высокожировая, мало клетчатки)": {
        "Lactobacillus spp.": 0.6, "Bifidobacterium spp.": 0.5, "Firmicutes (общие)": 1.3,
        "Bacteroides spp.": 1.4, "Escherichia coli (комменсаль)": 1.2
    },
    "Здоровая диета (богатая клетчаткой)": {
        "Bifidobacterium spp.": 1.5, "Lactobacillus spp.": 1.3, "Firmicutes (общие)": 1.1,
        "Clostridium spp.": 0.8
    },
    "Хронический стресс": {
        "Lactobacillus spp.": 0.8, "Bifidobacterium spp.": 0.85, "Proteobacteria (проч.)": 1.4
    },
    "Недосып / нерегулярный сон": {
        "Lactobacillus spp.": 0.9, "Clostridium spp.": 1.1
    },
    "Интенсивная физ. нагрузка": {
        "Lactobacillus spp.": 1.1, "Bifidobacterium spp.": 1.1, "Firmicutes (общие)": 1.05
    },
    "Длительная госпитализация / ИВЛ": {
        "Proteobacteria (проч.)": 3.0, "Clostridium spp.": 2.0, "Candida spp. (дрожжепод.)": 10.0
    },
    "Иммунодефицит / химиотерапия": {
        "Lactobacillus spp.": 0.5, "Bifidobacterium spp.": 0.5, "Proteobacteria (проч.)": 2.5,
        "Candida spp. (дрожжепод.)": 5.0
    },
    "Приём антацидов / PPI": {
        "Proteobacteria (проч.)": 1.5, "Escherichia coli (комменсаль)": 1.3, "Candida spp. (дрожжепод.)": 2.0
    }
}

# Adjust antibiotic/probiotic strength by duration
def duration_scale_ab(days):
    return min(1.0, days / 14.0)

def duration_scale_pro(days):
    return min(1.0, days / 14.0)

# Apply factors
def simulate(baseline, factors, ab_days=0, probiotic_days=0):
    result = baseline.copy()
    mult = {k: 1.0 for k in baseline.keys()}

    for f in factors:
        if f in ["Амоксициллин/клавуланат (Аугментин)", "Цефтриаксон", "Азитромицин", 
                "Левофлоксацин", "Метронидазол", "Ванкомицин (пероральный)"]:
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
        m = mult.get(k, 1.0)
        result[k] = max(0.0, result[k] * m)

    return result, mult

# Run simulation
if factors:
    simulated, multipliers = simulate(baseline, factors, ab_days, probiotic_course_days)
else:
    simulated, multipliers = baseline, {k: 1.0 for k in baseline.keys()}

# Prepare DataFrame for display
df = pd.DataFrame([
    {"Bacteria": k,
     "Baseline (KOE/g)": baseline[k],
     "Multiplier": multipliers[k],
     "Simulated (KOE/g)": simulated[k]}
    for k in baseline.keys()
])

# Format numbers
def sci(x):
    return "{:.3e}".format(x)

df_display = df.copy()
df_display["Baseline (KOE/g)"] = df_display["Baseline (KOE/g)"].apply(sci)
df_display["Simulated (KOE/g)"] = df_display["Simulated (KOE/g)"].apply(sci)
df_display["Multiplier"] = df_display["Multiplier"].apply(lambda x: f"{x:.2f}×")

# Show results
st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">Результаты анализа</h3></div>', unsafe_allow_html=True)

st.subheader("Таблица концентраций")
st.dataframe(df_display.set_index("Bacteria"), use_container_width=True)

# Bar chart
st.subheader("Графическое распределение (логарифмическая шкала)")
plot_df = df[["Bacteria", "Simulated (KOE/g)"]].copy()
plot_df["Simulated (KOE/g)"] = plot_df["Simulated (KOE/g)"].astype(float)
fig = px.bar(plot_df, x="Bacteria", y="Simulated (KOE/g)",
             labels={"Simulated (KOE/g)": "КОЕ/г"},
             log_y=True,
             height=450,
             color_discrete_sequence=['#228b22'])
fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

# Detailed automatic conclusion logic
def analyze(updated_dict):
    msgs = []
    for k in baseline:
        base = baseline[k]
        val = updated_dict[k]
        if val <= base * 0.2:
            msgs.append(f"Резкое снижение {k} (≤20% от базового уровня)")
        elif val <= base * 0.6:
            msgs.append(f"Умеренное снижение {k} (20–60% от базового)")
        elif val >= base * 5:
            msgs.append(f"Выраженное увеличение {k} (≥5× базового) — возможна переколонизация")
        elif val >= base * 1.5:
            msgs.append(f"Умеренное увеличение {k} (1.5–5× базового)")
    
    conclusions = []
    lacto = updated_dict["Lactobacillus spp."]
    bifi = updated_dict["Bifidobacterium spp."]
    clost = updated_dict["Clostridium spp."]
    proteo = updated_dict["Proteobacteria (проч.)"]
    candida = updated_dict["Candida spp. (дрожжепод.)"]

    if lacto < baseline["Lactobacillus spp."] * 0.5 and bifi < baseline["Bifidobacterium spp."] * 0.5:
        conclusions.append("Патерн: снижение основных симбионтов — риск дисбактериоза")
    if proteo > baseline["Proteobacteria (проч.)"] * 2.0:
        conclusions.append("Увеличение Proteobacteria — маркер воспаления/дисбиоза")
    if candida > baseline["Candida spp. (дрожжепод.)"] * 5:
        conclusions.append("Сильный рост Candida — риск кандидоза/суперинфекции")
    if clost > baseline["Clostridium spp."] * 5:
        conclusions.append("Выраженное увеличение Clostridium — возможна токсигенная колонизация")
    if not conclusions:
        conclusions.append("Серьёзных отклонений не выявлено; микробиом относительно стабилен")

    final = "## Автоматическое заключение:\n\n"
    final += "\n".join(msgs[:6]) + ("\n\n" if msgs else "")
    final += "## Основные выводы:\n" + "\n".join(conclusions)
    final += "\n\n## Рекомендации:\n- Рассмотреть корректировку факторов влияния\n- При выраженных отклонениях — лабораторная диагностика\n- Мониторинг состояния микробиома"
    return final


conclusion_text = analyze(simulated)

st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">Интерпретация и рекомендации</h3></div>', unsafe_allow_html=True)
st.markdown(conclusion_text)

# Download buttons
st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">💾 Экспорт результатов</h3></div>', unsafe_allow_html=True)

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

report_txt = f"""ОТЧЁТ ПО СИМУЛЯЦИИ МИКРОБИОМА
{'='*50}

Автор: {report['author']}
Группа: {report['group']}
Университет: {report['university']}
Дата анализа: {report['datetime']}

ФАКТОРЫ ВЛИЯНИЯ:
{'-'*20}
{chr(10).join(f'• {f}' for f in factors) if factors else '• Факторы не выбраны'}

ПАРАМЕТРЫ:
{'-'*10}
• Длительность антибиотиков: {ab_days} дней
• Длительность пробиотиков: {probiotic_course_days} дней

РЕЗУЛЬТАТЫ (КОЕ/г):
{'-'*20}
"""
for k, v in report["results"].items():
    report_txt += f"• {k}: {v:.3e}\n"

report_txt += f"\n{report['conclusion']}"

col1, col2 = st.columns(2)
with col1:
    st.download_button("📥 Скачать CSV результатов", data=csv_bytes, 
                      file_name="microbiome_results.csv", mime="text/csv",
                      use_container_width=True)
with col2:
    st.download_button("📥 Скачать полный отчёт", data=report_txt.encode('utf-8'),
                      file_name="microbiome_report.txt", mime="text/plain",
                      use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#666; font-size:14px;">
        <b>Учебный симулятор — не является клиническим заключением</b><br>
        Медицинский университет имени С. Д. Асфендиярова • 2024
    </div>
    """, unsafe_allow_html=True
)



