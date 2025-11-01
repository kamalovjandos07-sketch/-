# ---------------------- IMPORTS ----------------------
import streamlit as st
import pandas as pd
import numpy as np
import io
import datetime
import plotly.express as px

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="AI — Микробиом (КОЕ/г)",
                   page_icon="🧫", layout="centered")

# ---------------------- HEADER ----------------------
try:
    st.image("logo.png", width=120)
except:
    st.write("")

st.markdown(
    """
    <div style="text-align:center">
        <h3>Медицинский университет имени С. Д. Асфендиярова</h3>
        <div style="font-size:16px"><b>Камалов Жандос — Мед24-015</b></div>
        <div style="font-size:14px; color:gray;">
            Микробиология, вирусология кафедрасы<br>
            PhD, доценті Игисенова А.И.
        </div>
    </div>
    <hr>
    """, unsafe_allow_html=True
)

st.title("🧬 Симулятор состава кишечного микробиома (КОЕ/г)")
st.write("Выберите факторы и лекарства — приложение смоделирует изменения микробиоты и риск заболеваний.")

# ---------------------- BASELINE ----------------------
baseline = {
    "Lactobacillus spp.": 1e8,
    "Bifidobacterium spp.": 5e9,
    "Firmicutes (общие)": 1e10,
    "Bacteroides spp.": 5e9,
    "Clostridium spp.": 1e6,
    "Escherichia coli (комменсаль)": 1e7,
    "Proteobacteria (проч.)": 1e6,
    "Candida spp.": 1e4
}

# ---------------------- FACTORS ----------------------
factors = st.multiselect(
    "📌 Общие факторы:",
    [
        "Неправильное питание",
        "Здоровая диета",
        "Стресс",
        "Недосып",
        "Интенсивная физ. нагрузка",
    ]
)

# ---------------------- ANTIBIOTICS ----------------------
antibiotics = st.multiselect(
    "💊 Антибиотики:",
    [
        "Амоксициллин/клавуланат",
        "Цефтриаксон",
        "Азитромицин",
        "Ципрофлоксацин",
        "Доксициклин",
        "Кларитромицин",
        "Ванкомицин",
        "Метронидазол",
        "Левофлоксацин",
        "Карбапенемы",
    ]
)
ab_days = st.slider("Длительность антибиотиков (дни):", 0, 21, 7)

# ---------------------- OTHER DRUGS ----------------------
other_drugs = st.multiselect(
    "💉 Другие лекарства:",
    [
        "ИПП (омепразол/пантопразол)",
        "НПВС (ибупрофен/диклофенак)",
        "Глюкокортикоиды",
        "СИОЗС (антидепрессанты)",
        "Антигистаминные",
        "Флуконазол",
        "Метформин",
        "Антипсихотики",
    ]
)

# ---------------------- EFFECTS DATABASE ----------------------
effects = {
    "Неправильное питание": {
        "Lactobacillus spp.": 0.7, "Bifidobacterium spp.": 0.6,
        "Firmicutes (общие)": 1.3, "Bacteroides spp.": 1.4
    },
    "Здоровая диета": {
        "Lactobacillus spp.": 1.3, "Bifidobacterium spp.": 1.4
    },
    "Стресс": {"Proteobacteria (проч.)": 1.4, "Lactobacillus spp.": 0.8},
    "Недосып": {"Clostridium spp.": 1.2},
    "Интенсивная физ. нагрузка": {"Lactobacillus spp.": 1.1},

    # Antibiotics
    "Амоксициллин/клавуланат": {"Bifidobacterium spp.": 0.2, "Candida spp.": 5},
    "Цефтриаксон": {"Bacteroides spp.": 0.4, "Proteobacteria (проч.)": 2},
    "Азитромицин": {"Lactobacillus spp.": 0.5},
    "Ципрофлоксацин": {"Firmicutes (общие)": 0.5, "Proteobacteria (проч.)": 3},
    "Доксициклин": {"Lactobacillus spp.": 0.6},
    "Кларитромицин": {"Bifidobacterium spp.": 0.5},
    "Ванкомицин": {"Clostridium spp.": 3},
    "Метронидазол": {"Bacteroides spp.": 0.3},
    "Левофлоксацин": {"Proteobacteria (проч.)": 2.5},
    "Карбапенемы": {"Proteobacteria (проч.)": 4, "Candida spp.": 6},

    # Other drugs
    "ИПП (омепразол/пантопразол)": {"Proteobacteria (проч.)": 1.5, "Candida spp.": 2.5},
    "НПВС (ибупрофен/диклофенак)": {"Proteobacteria (проч.)": 1.3},
    "Глюкокортикоиды": {"Candida spp.": 3, "Lactobacillus spp.": 0.7},
    "СИОЗС (антидепрессанты)": {"Lactobacillus spp.": 0.8},
    "Антигистаминные": {"Bifidobacterium spp.": 0.8},
    "Флуконазол": {"Candida spp.": 0.2},
    "Метформин": {"Bacteroides spp.": 1.3},
    "Антипсихотики": {"Proteobacteria (проч.)": 2},
}

def apply_effects(values, selected, duration=1.0):
    for item in selected:
        for k, v in effects.get(item, {}).items():
            values[k] *= (1 + (v - 1) * duration)
    return values

# Simulation
sim = baseline.copy()
sim = apply_effects(sim, factors)
sim = apply_effects(sim, antibiotics, min(1.0, ab_days / 14))
sim = apply_effects(sim, other_drugs, 1.0)

# ---------------------- RESULTS ----------------------
df = pd.DataFrame({"Bacteria": sim.keys(), "Simulated (KOE/g)": sim.values()})

st.subheader("📊 Изменения микробиома")
fig = px.bar(df, x="Bacteria", y="Simulated (KOE/g)", log_y=True, height=450)
st.plotly_chart(fig, use_container_width=True)

# ---------------------- DIAGNOSIS ----------------------
def risks(val, base, name):
    if val < base * 0.4:
        return f"Недостаток {name} → риск дисбактериоза"
    if val > base * 4:
        return f"Избыток {name} → риск инфекции/воспаления"
    return None

risk_list = []
for k, base in baseline.items():
    r = risks(sim[k], base, k)
    if r: risk_list.append(f"- {r}")

st.subheader("⚠ Возможные риски")
if risk_list: st.write("\n".join(risk_list))
else: st.success("Серьёзных рисков не выявлено.")

# ---------------------- FOOTER ----------------------
st.markdown("<hr><div style='text-align:center;color:gray'>Учебный симулятор</div>", unsafe_allow_html=True)
