import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

# ---------------------------
# Настройки страницы
# ---------------------------
st.set_page_config(page_title="Микробиом человека", page_icon="🧫", layout="centered")

# ---------------------------
# Заголовок и информация
# ---------------------------
st.markdown(
    """
    <h1 style='text-align: center; color: #00BFFF;'>МИКРОБИОМ ЧЕЛОВЕКА</h1>
    <h3 style='text-align: center; color: #00BFFF;'>Кафедра микробиологии и вирусологии</h3>
    <h4 style='text-align: center; color: #00BFFF;'>PhD, доцент Игисенова А.И.</h4>
    <h4 style='text-align: center; color: #00BFFF;'>Камалов Жандос, Мед24-015</h4>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Ввод данных
# ---------------------------
st.subheader("Выберите факторы, влияющие на микробиом:")

factors = st.multiselect(
    "Факторы:",
    [
        "Антибиотики",
        "Стресс",
        "Питание с низким содержанием клетчатки",
        "Высокое потребление сахара",
        "Физическая активность",
        "Здоровое питание",
        "Пробиотики",
        "Хронические заболевания",
    ]
)

# ---------------------------
# Базовые значения микрофлоры
# ---------------------------
normal_microbiota = {
    "Lactobacillus": 1e8,
    "Bifidobacterium": 1e8,
    "Clostridium": 1e6,
    "Escherichia": 1e6,
    "Enterococcus": 1e5,
}

microbiota = normal_microbiota.copy()

# Изменяем показатели в зависимости от факторов
for f in factors:
    if f == "Антибиотики":
        microbiota["Lactobacillus"] *= 0.4
        microbiota["Bifidobacterium"] *= 0.5
        microbiota["Clostridium"] *= 1.5
    elif f == "Стресс":
        microbiota["Lactobacillus"] *= 0.7
        microbiota["Bifidobacterium"] *= 0.8
    elif f == "Питание с низким содержанием клетчатки":
        microbiota["Bifidobacterium"] *= 0.6
    elif f == "Высокое потребление сахара":
        microbiota["Clostridium"] *= 1.4
        microbiota["Escherichia"] *= 1.5
    elif f == "Физическая активность":
        microbiota["Lactobacillus"] *= 1.2
        microbiota["Bifidobacterium"] *= 1.1
    elif f == "Здоровое питание":
        microbiota["Lactobacillus"] *= 1.3
        microbiota["Bifidobacterium"] *= 1.2
    elif f == "Пробиотики":
        microbiota["Lactobacillus"] *= 1.5
        microbiota["Bifidobacterium"] *= 1.4
    elif f == "Хронические заболевания":
        microbiota["Enterococcus"] *= 1.6
        microbiota["Clostridium"] *= 1.5

# ---------------------------
# Результаты
# ---------------------------
st.subheader("Результаты анализа микробиоты (КОЕ/г):")
df = pd.DataFrame(list(microbiota.items()), columns=["Бактерии", "Количество, КОЕ/г"])
st.dataframe(df)

# ---------------------------
# Шкала нормальности
# ---------------------------
normality = np.mean([
    min(microbiota[b] / normal_microbiota[b], 1.0) for b in normal_microbiota
]) * 100

st.subheader("Общая оценка микробиома:")
fig = px.bar(
    x=["Нормальность микробиома"],
    y=[normality],
    range_y=[0, 100],
    color=["Нормальность микробиома"],
    color_discrete_sequence=["#00BFFF"],
    text=[f"{normality:.1f}%"]
)
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Заключение
# ---------------------------
st.subheader("Заключение:")

if normality > 85:
    st.success("Микробиом в норме. Поддерживайте здоровое питание и активность 💪")
elif normality > 60:
    st.warning("Микробиом слегка нарушен. Рекомендуется больше клетчатки и пробиотиков.")
else:
    st.error("Серьёзный дисбаланс микрофлоры. Возможны последствия для пищеварения и иммунитета.")

# ---------------------------
# Дата отчёта
# ---------------------------
st.write(f"Дата анализа: {datetime.date.today().strftime('%d.%m.%Y')}")

