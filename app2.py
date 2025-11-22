import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Настройки страницы
st.set_page_config(
    page_title="Antibiotic Stewardship System",
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стили с Inter шрифтом
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1a1a1a;
        letter-spacing: -0.02em;
    }
    
    .main {
        background-color: #f8f9fa;
    }
    
    .stButton>button {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    .stSelectbox, .stMultiselect, .stNumberInput, .stSlider {
        font-family: 'Inter', sans-serif;
    }
    
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .crisis-alert {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin: 20px 0;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .stats-box {
        background: white;
        padding: 24px;
        border-radius: 12px;
        border-left: 6px solid #228b22;
        margin: 15px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    .antibiotic-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
    }
    
    .no-antibiotic-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4caf50;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.1);
    }
    
    .diagnosis-card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .sidebar-section {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .pulse-alert {
        animation: pulse 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

# 🏥 БАЗА ЗАБОЛЕВАНИЙ И ЛЕЧЕНИЯ
MEDICAL_KNOWLEDGE_BASE = {
    "community_acquired_pneumonia": {
        "diagnosis_criteria": ["Лихорадка >38°C", "Кашель", "Одышка", "Боль в груди", "Лейкоцитоз", "Повышение СРБ"],
        "required_criteria": 3,
        "treatments": {
            "antibiotics": ["Амоксициллин/клавуланат 875/125 мг 2 раза/сут × 7-10 дней", "Азитромицин 500 мг/сут × 3-5 дней"],
            "symptomatic": ["Парацетамол 500 мг при температуре", "Муколитики (АЦЦ 600 мг/сут)", "Ингаляции с физраствором"],
            "supportive": ["Постельный режим", "Обильное питье", "Контроль сатурации"]
        },
        "referral": "При тяжелом течении - госпитализация",
        "source": "IDSA/ATS Guidelines 2019"
    },
    
    "streptococcal_pharyngitis": {
        "diagnosis_criteria": ["Боль в горле", "Лихорадка >38°C", "Налеты на миндалинах", "Увеличение шейных лимфоузлов", "Отсутствие кашля"],
        "required_criteria": 4,
        "treatments": {
            "antibiotics": ["Феноксиметилпенициллин 500 мг 3 раза/сут × 10 дней", "Азитромицин 500 мг/сут × 3 дня при аллергии"],
            "symptomatic": ["Парацетамол 500 мг при боли", "Местные антисептики (Гексорал, Тантум Верде)", "Полоскание содо-солевым раствором"],
            "supportive": ["Щадящая диета", "Теплое питье", "Голосовой покой"]
        },
        "referral": "При рецидивирующем течении - консультация ЛОРа",
        "source": "IDSA Pharyngitis Guidelines"
    },
    
    "urinary_tract_infection": {
        "diagnosis_criteria": ["Дизурия", "Учащенное мочеиспускание", "Боль в надлобковой области", "Лихорадка", "Лейкоциты в моче"],
        "required_criteria": 2,
        "treatments": {
            "antibiotics": ["Нитрофурантоин 100 мг 3 раза/сут × 5 дней", "Фосфомицин 3 г однократно", "Цефтриаксон 1 г/сут в/м при осложнениях"],
            "symptomatic": ["Ибупрофен 400 мг при боли", "Спазмолитики (Но-шпа 40-80 мг/сут)", "Уросептики (Фитолизин)"],
            "supportive": ["Обильное питье", "Клюквенные морсы", "Исключение острой пищи"]
        },
        "referral": "При рецидивах - уролог, при беременности - срочно к врачу",
        "source": "IDSA UTI Guidelines"
    },
    
    "acute_bronchitis": {
        "diagnosis_criteria": ["Кашель <3 недель", "Может быть продуктивным", "Отсутствие лихорадки >38°C", "Отсутствие одышки", "Нормальные показатели воспаления"],
        "required_criteria": 3,
        "treatments": {
            "antibiotics": ["Антибиотики НЕ ПОКАЗАНЫ при вирусной этиологии"],
            "symptomatic": ["Противокашлевые (Синекод) при сухом кашле", "Муколитики (Амброксол 30 мг 3 раза/сут)", "Бронходилататоры (Сальбутамол) при бронхоспазме"],
            "supportive": ["Увлажнение воздуха", "Теплое питье", "Ингаляции", "Отказ от курения"]
        },
        "referral": "При сохранении симптомов >3 недель - пульмонолог",
        "source": "NICE Bronchitis Guidelines"
    },
    
    "influenza": {
        "diagnosis_criteria": ["Внезапное начало", "Лихорадка", "Головная боль", "Мышечные боли", "Слабость", "Сезонность"],
        "required_criteria": 3,
        "treatments": {
            "antivirals": ["Осельтамивир 75 мг 2 раза/сут × 5 дней", "Занамивир ингаляционно"],
            "symptomatic": ["Парацетамол 500 мг при температуре", "Ибупрофен 400 мг при боли", "Сосудосуживающие капли при рините"],
            "supportive": ["Постельный режим", "Обильное питье", "Витамин C", "Проветривание помещения"]
        },
        "referral": "При тяжелом течении, беременным, пожилым - срочно к врачу",
        "source": "WHO Influenza Guidelines"
    },
    
    "acute_gastroenteritis": {
        "diagnosis_criteria": ["Тошнота", "Рвота", "Диарея", "Боль в животе", "Слабость", "Возможна субфебрильная температура"],
        "required_criteria": 3,
        "treatments": {
            "rehydration": ["Регидрон 1 пакет на 1 л воды", "Оральные солевые растворы", "Частое дробное питье"],
            "symptomatic": ["Смекта 3 пакета/сут", "Энтеросорбенты (Полисорб)", "Противорвотные (Метоклопрамид) только по назначению"],
            "diet": ["Голод 4-6 часов", "Затем щадящая диета (рис, сухари, бананы)", "Исключение молочного, жирного, острого"]
        },
        "referral": "При признаках дегидратации, крови в стуле - срочно к врачу",
        "source": "ESPID Gastroenteritis Guidelines"
    },
    
    "hypertensive_crisis": {
        "diagnosis_criteria": ["АД >180/120 мм рт.ст.", "Головная боль", "Тошнота", "Нарушение зрения", "Одышка", "Боль в груди"],
        "required_criteria": 2,
        "treatments": {
            "emergency": ["Немедленный вызов скорой помощи", "Каптоприл 25 мг сублингвально", "Нифедипин 10 мг (только по назначению)"],
            "monitoring": ["Контроль АД каждые 15 минут", "Покой, полусидячее положение", "Доступ свежего воздуха"]
        },
        "referral": "ЭКГ, госпитализация в кардиологическое отделение",
        "source": "ESC Hypertension Guidelines"
    }
}

# 🔍 ДИАГНОСТИЧЕСКАЯ СИСТЕМА
def medical_diagnosis_system(symptoms, lab_data, vital_signs, temperature, bp_systolic, bp_diastolic, wbc, crp):
    symptom_score = {}
    
    # Проверяем критические состояния первыми
    if bp_systolic > 180 and bp_diastolic > 120:
        if any(symptom in ["Головная боль", "Тошнота", "Нарушение зрения", "Одышка", "Боль в груди"] for symptom in symptoms):
            return "hypertensive_crisis", 10
    
    # Определяем лабораторные показатели
    has_leukocytosis = "Лейкоцитоз" in lab_data or wbc > 10.0
    has_elevated_crp = "Повышение СРБ" in lab_data or crp > 5.0
    has_urinary_leuko = "Лейкоциты в моче" in lab_data
    
    # Пневмония
    pneumonia_score = sum([
        2 if "Лихорадка >38°C" in symptoms and temperature > 38 else 0,
        2 if "Кашель с мокротой" in symptoms else 1 if "Кашель" in symptoms else 0,
        2 if "Одышка" in symptoms else 0,
        2 if "Боль в груди" in symptoms else 0,
        2 if has_leukocytosis else 0,
        2 if has_elevated_crp else 0
    ])
    symptom_score["community_acquired_pneumonia"] = pneumonia_score
    
    # Ангина
    pharyngitis_score = sum([
        2 if "Боль в горле" in symptoms else 0,
        2 if "Налеты на миндалинах" in symptoms else 0,
        2 if "Лихорадка >38°C" in symptoms and temperature > 38 else 0,
        2 if "Увеличение лимфоузлов" in symptoms else 0,
        -2 if "Кашель" in symptoms else 1,
        1 if "Головная боль" in symptoms else 0
    ])
    symptom_score["streptococcal_pharyngitis"] = pharyngitis_score
    
    # ИМП
    uti_score = sum([
        3 if "Дизурия" in symptoms else 0,
        2 if "Учащенное мочеиспускание" in symptoms else 0,
        2 if "Боль в надлобковой области" in symptoms else 0,
        2 if has_urinary_leuko else 0,
        2 if "Лихорадка >38°C" in symptoms and temperature > 38 else 0
    ])
    symptom_score["urinary_tract_infection"] = uti_score
    
    # Бронхит
    bronchitis_score = sum([
        2 if "Кашель" in symptoms else 0,
        2 if "Кашель с мокротой" in symptoms else 0,
        -2 if "Лихорадка >38°C" in symptoms and temperature > 38 else 1,
        -2 if "Одышка" in symptoms else 1,
        -2 if has_leukocytosis else 1,
        1 if "Слабость" in symptoms else 0
    ])
    symptom_score["acute_bronchitis"] = bronchitis_score
    
    # Грипп
    influenza_score = sum([
        2 if "Лихорадка >38°C" in symptoms and temperature > 38 else 0,
        2 if "Головная боль" in symptoms else 0,
        2 if "Мышечные боли" in symptoms else 0,
        2 if "Слабость" in symptoms else 0,
        2 if "Внезапное начало" in symptoms else 0,
        1 if "Сезонность" in symptoms else 0
    ])
    symptom_score["influenza"] = influenza_score
    
    # Гастроэнтерит
    gastroenteritis_score = sum([
        3 if "Тошнота" in symptoms else 0,
        3 if "Рвота" in symptoms else 0,
        3 if "Диарея" in symptoms else 0,
        2 if "Боль в животе" in symptoms else 0,
        1 if "Слабость" in symptoms else 0,
        1 if "Субфебрильная температура" in symptoms and 37 < temperature < 38 else 0
    ])
    symptom_score["acute_gastroenteritis"] = gastroenteritis_score
    
    # Находим наиболее вероятный диагноз
    sorted_diagnoses = sorted(symptom_score.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_diagnoses[0][0], sorted_diagnoses

# 🎯 ОСНОВНОЙ ИНТЕРФЕЙС
def main():
    # ЗАГОЛОВОК С МЕСТОМ ДЛЯ ЛОГОТИПА
    col1, col2 = st.columns([1, 4])
    with col1:
        # 👇 МЕСТО ДЛЯ ТВОЕГО ЛОГОТИПА
        st.image("logo.png", width=180)
    with col2:
        st.markdown("""
        <div class="header-section">
            <h1 style="margin:0; font-size:2.8rem; font-weight:700;">Antibiotic Stewardship System</h1>
            <p style="font-size:1.3rem; margin:15px 0 0 0; opacity:0.9;">
                Борьба с антибиотикорезистентностью через рациональную диагностику
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # СТАТИСТИКА ПРОБЛЕМЫ
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="stats-box">
            <h3 style="color:#228b22; margin:0">1.2M</h3>
            <p style="margin:5px 0 0 0; color:#666">смертей в год от резистентности</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-box">
            <h3 style="color:#228b22; margin:0">50%</h3>
            <p style="margin:5px 0 0 0; color:#666">нерациональных назначений антибиотиков</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-box">
            <h3 style="color:#228b22; margin:0">$100T</h3>
            <p style="margin:5px 0 0 0; color:#666">мировые потери к 2050 году</p>
        </div>
        """, unsafe_allow_html=True)
    
    # МЕСТО ДЛЯ ГРАФИКОВ И ФОТО
    st.markdown("---")
    st.subheader("Визуализация проблемы антибиотикорезистентности")
    
    col1, col2 = st.columns(2)
    with col1:
        # 👇 МЕСТО ДЛЯ ПЕРВОЙ КАРТИНКИ
        # st.image("resistance_graph.png", use_column_width=True, caption="Рост резистентности")
        st.info("📊 Место для графика резистентности")
    with col2:
        # 👇 МЕСТО ДЛЯ ВТОРОЙ КАРТИНКИ
        # st.image("bacteria_image.jpg", use_column_width=True, caption="Механизмы резистентности")
        st.info("🦠 Место для фото бактерий")
    
    # ОСНОВНОЙ ИНТЕРФЕЙС ДИАГНОСТИКИ
    st.markdown("---")
    st.header("Клиническая диагностика")
    st.write("Система поддержки врачебных решений для рационального назначения антибиотиков")
    
    # ВВОД ДАННЫХ
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Клиническая картина")
        
        symptoms = st.multiselect(
            "Симптомы пациента:",
            [
                "Лихорадка >38°C", "Озноб", "Кашель", "Кашель с мокротой", 
                "Одышка", "Боль в груди", "Боль в горле", "Налеты на миндалинах", 
                "Увеличение лимфоузлов", "Дизурия", "Учащенное мочеиспускание",
                "Боль в надлобковой области", "Тошнота", "Рвота", "Диарея",
                "Боль в животе", "Головная боль", "Мышечные боли", "Слабость",
                "Внезапное начало", "Сезонность", "Субфебрильная температура"
            ]
        )
        
        temperature = st.slider("Температура тела (°C):", 35.0, 42.0, 37.0, 0.1)
        
    with col2:
        st.subheader("Лабораторные показатели")
        
        wbc = st.number_input("Лейкоциты (×10⁹/л):", min_value=1.0, max_value=50.0, value=6.0, step=0.1,
                             help="Норма: 4.0-9.0 ×10⁹/л")
        
        crp = st.number_input("СРБ (мг/л):", min_value=0.0, max_value=200.0, value=2.0, step=0.1,
                             help="Норма: <5 мг/л")
        
        lab_data = st.multiselect(
            "Другие результаты анализов:",
            [
                "Лейкоциты в моче", "Нитриты в моче", "Анализы в норме"
            ]
        )
        
        st.subheader("Артериальное давление")
        bp_col1, bp_col2 = st.columns(2)
        with bp_col1:
            bp_systolic = st.number_input("Систолическое (мм рт.ст.):", 80, 250, 120)
        with bp_col2:
            bp_diastolic = st.number_input("Диастолическое (мм рт.ст.):", 50, 150, 80)
    
    # ДИАГНОСТИКА
    if st.button("Запустить диагностику", type="primary", use_container_width=True):
        if not symptoms:
            st.warning("Пожалуйста, введите симптомы пациента")
            return
            
        with st.spinner("Проводим анализ по клиническим рекомендациям..."):
            # Диагностика
            vital_signs = f"Температура: {temperature}°C, АД: {bp_systolic}/{bp_diastolic} мм рт.ст."
            main_diagnosis, all_diagnoses = medical_diagnosis_system(
                symptoms, lab_data, vital_signs, temperature, bp_systolic, bp_diastolic, wbc, crp
            )
            
            # РЕЗУЛЬТАТЫ
            st.markdown("---")
            st.header("Результаты диагностики")
            
            # Основной диагноз
            diagnosis_info = MEDICAL_KNOWLEDGE_BASE[main_diagnosis]
            diagnosis_name = main_diagnosis.replace('_', ' ').title()
            
            st.markdown(f"""
            <div class="diagnosis-card">
                <h2 style="color:#2c3e50; margin:0 0 15px 0">{diagnosis_name}</h2>
                <p><strong>Баллы диагностики:</strong> {all_diagnoses[0][1]}/10</p>
                <p><strong>Источник рекомендаций:</strong> {diagnosis_info['source']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # КРИТИЧЕСКИЕ СОСТОЯНИЯ
            if main_diagnosis == "hypertensive_crisis":
                st.markdown("""
                <div class="crisis-alert pulse-alert">
                    <h3 style="margin:0; color:white">Критическое состояние!</h3>
                    <p style="margin:10px 0 0 0; color:white; font-size:1.1rem">
                    Немедленный вызов скорой помощи • Контроль АД каждые 15 минут • Покой, полусидячее положение
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # ЛЕЧЕНИЕ
            st.subheader("Рекомендации по лечению")
            
            treatments = diagnosis_info["treatments"]
            
            if "antibiotics" in treatments:
                st.markdown("""
                <div class="antibiotic-box">
                    <h4 style="margin:0 0 10px 0; color:#1565c0">Антибактериальная терапия</h4>
                """, unsafe_allow_html=True)
                for med in treatments["antibiotics"]:
                    st.write(f"• {med}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            if "antivirals" in treatments:
                st.markdown("""
                <div class="antibiotic-box">
                    <h4 style="margin:0 0 10px 0; color:#1565c0">Противовирусная терапия</h4>
                """, unsafe_allow_html=True)
                for med in treatments["antivirals"]:
                    st.write(f"• {med}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            if "antibiotics" not in treatments and "Антибиотики НЕ ПОКАЗАНЫ" in str(treatments.get("antibiotics", [])):
                st.markdown("""
                <div class="no-antibiotic-box">
                    <h4 style="margin:0 0 10px 0; color:#2e7d32">Рациональная антибиотикотерапия</h4>
                    <p style="margin:0; font-weight:500">Антибиотики не показаны - сохранение эффективности препаратов для будущих поколений</p>
                </div>
                """, unsafe_allow_html=True)
            
            # СИМПТОМАТИЧЕСКОЕ ЛЕЧЕНИЕ
            if "symptomatic" in treatments or "supportive" in treatments or "rehydration" in treatments:
                st.markdown("""
                <div class="stats-box">
                    <h4 style="margin:0 0 15px 0; color:#2c3e50">Симптоматическое и вспомогательное лечение</h4>
                """, unsafe_allow_html=True)
                
                if "symptomatic" in treatments:
                    st.write("**Симптоматическое:**")
                    for med in treatments["symptomatic"]:
                        st.write(f"• {med}")
                
                if "supportive" in treatments:
                    st.write("**Вспомогательное:**")
                    for action in treatments["supportive"]:
                        st.write(f"• {action}")
                
                if "rehydration" in treatments:
                    st.write("**Регидратация:**")
                    for med in treatments["rehydration"]:
                        st.write(f"• {med}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # НАПРАВЛЕНИЯ
            st.markdown("""
            <div class="stats-box">
                <h4 style="margin:0 0 10px 0; color:#2c3e50">Дальнейшие действия</h4>
                <p style="margin:0">{}</p>
            </div>
            """.format(diagnosis_info["referral"]), unsafe_allow_html=True)
            
            # ДИФФЕРЕНЦИАЛЬНАЯ ДИАГНОСТИКА
            st.subheader("Дифференциальная диагностика")
            for i, (diagnosis, score) in enumerate(all_diagnoses[1:4], 1):
                diag_name = diagnosis.replace('_', ' ').title()
                st.write(f"{i}. **{diag_name}** ({score} баллов)")
    
    # БОКОВАЯ ПАНЕЛЬ С МЕСТОМ ДЛЯ ЛОГОТИПА
    with st.sidebar:
        # 👇 МЕСТО ДЛЯ ЛОГОТИПА В SIDEBAR
        # st.image("logo.png", width=120)
        st.markdown("""
        <div class="sidebar-section">
            <h4 style="margin:0 0 10px 0;">📍 Место для логотипа университета</h4>
            <p style="margin:0; color:#666">Медицинский университет им. С.Д. Асфендиярова</p>
            <p style="margin:5px 0 0 0; color:#666">Камалов Жандос — Мед24-015</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div class="sidebar-section">
            <h3 style="margin:0 0 15px 0">О системе</h3>
            <p style="margin:0 0 15px 0; color:#666">
            Образовательная платформа для борьбы с антибиотикорезистентностью 
            через рациональную диагностику и назначение терапии.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <h4 style="margin:0 0 12px 0">Диагностируемые состояния</h4>
            <ul style="margin:0; padding-left:20px; color:#666">
            <li>Пневмония</li>
            <li>Стрептококковая ангина</li>
            <li>Инфекции мочевых путей</li>
            <li>Острый бронхит</li>
            <li>Грипп</li>
            <li>Острый гастроэнтерит</li>
            <li>Гипертонический криз</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <h4 style="margin:0 0 12px 0; color:#d32f2f">Важно</h4>
            <p style="margin:0; color:#666; font-size:0.9rem">
            Данная система предназначена для образовательных целей 
            и не заменяет консультацию врача. При критических состояниях 
            немедленно обращайтесь за медицинской помощью.
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()





