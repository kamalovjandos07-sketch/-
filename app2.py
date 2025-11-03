# app.py
import streamlit as st
import pandas as pd
import numpy as np
import io
import datetime
import plotly.express as px

st.set_page_config(page_title="Клинический симулятор АБТ",
                   page_icon="🩺", layout="centered")

# Медицинский стиль
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
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .success-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True
)

# Заголовок
st.markdown(
    """
    <div class="medical-header">
        <h2 style="margin:0; color:white; font-weight:bold;">🏥 Медицинский университет имени С. Д. Асфендиярова</h2>
        <div style="font-size:18px; margin-top:15px; font-weight:bold;">Камалов Жандос — Мед24-015</div>
        <div style="font-size:14px; margin-top:10px; opacity:0.9;">Клинический симулятор рациональной антибиотикотерапии</div>
    </div>
    """, unsafe_allow_html=True
)

# Основной заголовок
st.markdown('<div class="section-header"><h1 style="margin:0; color:#006400;">🩺 Клинический симулятор антибиотикотерапии</h1></div>', unsafe_allow_html=True)

st.write("**Система оценки необходимости и подбора антибиотиков на основе клинической картины**")

# РАЗДЕЛ 1: ДИАГНОСТИКА ПАЦИЕНТА
st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">🔍 Диагностика пациента</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Клиническая картина")
    symptoms = st.multiselect(
        "Симптомы пациента:",
        ["Лихорадка >38°C", "Озноб", "Кашель с гнойной мокротой", 
         "Боль в горле с налетами", "Заложенность носа", "Насморк",
         "Головная боль", "Слабость", "Одышка",
         "Боль при мочеиспускании", "Частые позывы", "Кожные высыпания",
         "Боль в ухе", "Диарея", "Тошнота/рвота"]
    )
    
    temperature = st.slider("Температура тела (°C):", 36.0, 41.0, 37.0, 0.1)

with col2:
    st.subheader("Данные обследования")
    
    lab_data = st.selectbox(
        "Результаты анализов:",
        ["Не проводились", "Лейкоцитоз (>10×10⁹/л)", "Повышение СРБ (>5 мг/л)", 
         "Посев: выявлен возбудитель", "Анализы в норме", "Лимфоцитоз"]
    )
    
    diagnosis_presumptive = st.selectbox(
        "Предполагаемый диагноз:",
        ["ОРВИ", "Острый бронхит", "Пневмония", "Ангина/тонзиллит",
         "Острый синусит", "Отит", "Инфекция МВП", 
         "Кожная инфекция", "Кишечная инфекция", "Другое"]
    )

# РАЗДЕЛ 2: ОЦЕНКА НЕОБХОДИМОСТИ АНТИБИОТИКОВ
st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">📊 Оценка необходимости антибиотикотерапии</h3></div>', unsafe_allow_html=True)

def assess_antibiotic_need(symptoms, lab_data, diagnosis, temperature):
    score = 0
    recommendations = []
    
    # Критерии необходимости АБ
    if temperature >= 38.5:
        score += 2
        recommendations.append("Высокая лихорадка (>38.5°C)")
    
    if "Лихорадка >38°C" in symptoms and temperature >= 38.0:
        score += 1
    
    if "Кашель с гнойной мокротой" in symptoms:
        score += 2
        recommendations.append("Гнойная мокрота")
    
    if "Боль в горле с налетами" in symptoms:
        score += 2
        recommendations.append("Налеты на миндалинах")
    
    if lab_data in ["Лейкоцитоз (>10×10⁹/л)", "Повышение СРБ (>5 мг/л)"]:
        score += 2
        recommendations.append("Воспалительные изменения в анализах")
    
    if lab_data == "Посев: выявлен возбудитель":
        score += 3
        recommendations.append("Подтвержденный возбудитель")
    
    # Диагностические критерии
    if diagnosis in ["Пневмония", "Ангина/тонзиллит", "Пиелонефрит"]:
        score += 3
        recommendations.append(f"Диагноз '{diagnosis}' требует АБТ")
    
    if diagnosis in ["Острый бронхит", "Острый синусит", "Отит"]:
        score += 2
        recommendations.append(f"Диагноз '{diagnosis}' - рассмотреть АБТ")
    
    if diagnosis == "ОРВИ":
        score -= 2
        recommendations.append("ОРВИ - антибиотики не показаны")
    
    # Оценка результата
    if score >= 6:
        return {
            "decision": "🔴 Антибиотикотерапия ОБОСНОВАНА",
            "score": score,
            "recommendations": recommendations,
            "color": "red"
        }
    elif score >= 3:
        return {
            "decision": "🟡 Рассмотреть антибиотики после дообследования",
            "score": score, 
            "recommendations": recommendations,
            "color": "orange"
        }
    else:
        return {
            "decision": "🟢 Антибиотики НЕ ПОКАЗАНЫ - симптоматическая терапия",
            "score": score,
            "recommendations": recommendations,
            "color": "green"
        }

assessment = assess_antibiotic_need(symptoms, lab_data, diagnosis_presumptive, temperature)

# Отображение результата оценки
if assessment["color"] == "red":
    st.error(f"**Заключение:** {assessment['decision']}")
elif assessment["color"] == "orange":
    st.warning(f"**Заключение:** {assessment['decision']}")
else:
    st.success(f"**Заключение:** {assessment['decision']}")

st.write(f"**Баллы по шкале:** {assessment['score']}/10")
if assessment["recommendations"]:
    st.write("**Критерии:**")
    for rec in assessment["recommendations"]:
        st.write(f"- {rec}")

# РАЗДЕЛ 3: ПОДБОР АНТИБИОТИКОВ (только если показаны)
if assessment["color"] in ["red", "orange"]:
    st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">💊 Рекомендации по антибиотикотерапии</h3></div>', unsafe_allow_html=True)
    
    def recommend_antibiotics(diagnosis, symptoms):
        recommendations = []
        
        if diagnosis == "Пневмония":
            recommendations.append({
                "drug": "Амоксициллин/клавуланат",
                "dose": "875/125 мг 2 раза/сут",
                "duration": "7-10 дней",
                "reason": "Препарат выбора при внебольничной пневмонии"
            })
            recommendations.append({
                "drug": "Азитромицин", 
                "dose": "500 мг 1 раз/сут",
                "duration": "3-5 дней",
                "reason": "При подозрении на атипичную флору"
            })
            
        elif diagnosis == "Ангина/тонзиллит":
            recommendations.append({
                "drug": "Амоксициллин",
                "dose": "500 мг 3 раза/сут", 
                "duration": "10 дней",
                "reason": "Препарат выбора при стрептококковой ангине"
            })
            
        elif diagnosis == "Инфекция МВП":
            recommendations.append({
                "drug": "Цефтриаксон",
                "dose": "1 г 1 раз/сут в/м",
                "duration": "7 дней", 
                "reason": "При осложненных ИМП"
            })
            recommendations.append({
                "drug": "Левофлоксацин",
                "dose": "500 мг 1 раз/сут",
                "duration": "5-7 дней",
                "reason": "Альтернативный препарат"
            })
            
        elif diagnosis in ["Острый бронхит", "Острый синусит", "Отит"]:
            recommendations.append({
                "drug": "Амоксициллин/клавуланат",
                "dose": "625 мг 3 раза/сут",
                "duration": "5-7 дней",
                "reason": "При бактериальной этиологии"
            })
            
        else:
            recommendations.append({
                "drug": "Требуется консультация специалиста",
                "dose": "-",
                "duration": "-", 
                "reason": "Для уточнения тактики лечения"
            })
            
        return recommendations
    
    ab_recommendations = recommend_antibiotics(diagnosis_presumptive, symptoms)
    
    for i, rec in enumerate(ab_recommendations, 1):
        with st.container():
            st.markdown(f"**Вариант {i}: {rec['drug']}**")
            st.write(f"Дозировка: {rec['dose']}")
            st.write(f"Длительность: {rec['duration']}") 
            st.write(f"Обоснование: {rec['reason']}")
            st.markdown("---")

# РАЗДЕЛ 4: СИМУЛЯТОР ВОЗДЕЙСТВИЯ НА МИКРОБИОМ
st.markdown('<div class="section-header"><h3 style="margin:0; color:#006400;">🧬 Влияние на микробиом</h3></div>', unsafe_allow_html=True)

# Baseline микробиома
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

# Эффекты антибиотиков
effects = {
    "Амоксициллин/клавуланат": {
        "Lactobacillus spp.": 0.1, "Bifidobacterium spp.": 0.15, "Firmicutes (общие)": 0.5,
        "Bacteroides spp.": 0.4, "Clostridium spp.": 2.0, "Escherichia coli (комменсаль)": 1.5,
        "Proteobacteria (проч.)": 2.0, "Candida spp. (дрожжепод.)": 5.0
    },
    "Азитромицин": {
        "Lactobacillus spp.": 0.5, "Bifidobacterium spp.": 0.6, "Firmicutes (общие)": 0.8,
        "Bacteroides spp.": 0.7, "Clostridium spp.": 1.5, "Escherichia coli (комменсаль)": 1.2,
        "Proteobacteria (проч.)": 1.4, "Candida spp. (дрожжепод.)": 2.0
    },
    "Цефтриаксон": {
        "Lactobacillus spp.": 0.3, "Bifidobacterium spp.": 0.4, "Firmicutes (общие)": 0.7,
        "Bacteroides spp.": 0.6, "Clostridium spp.": 3.0, "Escherichia coli (комменсаль)": 0.8,
        "Proteobacteria (проч.)": 1.8, "Candida spp. (дрожжепод.)": 4.0
    },
    "Левофлоксацин": {
        "Lactobacillus spp.": 0.7, "Bifidobacterium spp.": 0.8, "Firmicutes (общие)": 0.9,
        "Bacteroides spp.": 0.8, "Clostridium spp.": 1.2, "Escherichia coli (комменсаль)": 0.5,
        "Proteobacteria (проч.)": 0.7, "Candida spp. (дрожжепод.)": 1.8
    }
}

# Симуляция воздействия
if assessment["color"] in ["red", "orange"] and ab_recommendations[0]["drug"] != "Требуется консультация специалиста":
    selected_ab = st.selectbox(
        "Выберите антибиотик для оценки влияния на микробиом:",
        [rec["drug"] for rec in ab_recommendations if rec["drug"] in effects]
    )
    
    if selected_ab in effects:
        # Симуляция
        simulated = baseline.copy()
        for bacteria, effect in effects[selected_ab].items():
            simulated[bacteria] = max(0.0, simulated[bacteria] * effect)
        
        # Визуализация
        plot_df = pd.DataFrame([
            {"Бактерии": k, "КОЕ/г": v, "Тип": "После АБ"} 
            for k, v in simulated.items()
        ])
        baseline_df = pd.DataFrame([
            {"Бактерии": k, "КОЕ/г": v, "Тип": "До АБ"} 
            for k, v in baseline.items()
        ])
        comparison_df = pd.concat([baseline_df, plot_df])
        
        fig = px.bar(comparison_df, x="Бактерии", y="КОЕ/г", color="Тип",
                     barmode="group", log_y=True, height=400,
                     color_discrete_map={"До АБ": "#228b22", "После АБ": "#ff6b6b"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Анализ изменений
        st.write("**Анализ изменений микробиома:**")
        for bacteria in baseline:
            change = (simulated[bacteria] - baseline[bacteria]) / baseline[bacteria] * 100
            if change < -50:
                st.error(f"🔻 {bacteria}: снижение на {abs(change):.1f}%")
            elif change > 100:
                st.warning(f"🔺 {bacteria}: увеличение в {simulated[bacteria]/baseline[bacteria]:.1f} раз")

# РАЗДЕЛ 5: СТАТИСТИКА ИЗ ОПРОСА (заглушка - потом заменишь)
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Данные опроса Мед24-015")

st.sidebar.markdown("""
**Предварительные результаты (n=0):**

*По мере поступления ответов данные будут обновляться*

- Частота нерациональных назначений: ...
- Самые частые ошибки: ...
- Средняя длительность приема: ...
""")

# ИНФОРМАЦИЯ О ПРОЕКТЕ
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666;">
    <b>Клинический симулятор антибиотикотерапии</b><br>
    Медицинский университет имени С. Д. Асфендиярова • 2024<br>
    <small>Учебное пособие - не заменяет консультацию врача</small>
</div>
""", unsafe_allow_html=True)
