import streamlit as st
import pandas as pd
import datetime
import requests
from streamlit_autorefresh import st_autorefresh
import re
import time

# Auto-refresh para cambiar entre secciones
count = st_autorefresh(interval=60000, key="auto_refresh")
seccion = count % 2

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    body, .stApp {
        background-color: #e3f0fc !important;
    }
    .fade-in {
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .block-container {
        padding-top: 1rem !important;
    }
    h1 {
        margin-top: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# CSS animación 
st.markdown("""
    <style>
    .fade-in {
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .block-container {
        padding-top: 1rem !important;
    }
    h1 {
        margin-top: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

#Título 
st.markdown("<h1 style='text-align: center; color: #19277f;'>Muelles y Frenos Simón Bolívar</h1>", unsafe_allow_html=True)

# Pico y placa por día
pico_placa = {
    'Lunes': ['3', '4'],
    'Martes': ['2', '8'],
    'Miércoles': ['5', '9'],
    'Jueves': ['1', '7'],
    'Viernes': ['0', '6'],
}
dia_actual = datetime.datetime.now().strftime('%A')
dia_traducido = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}[dia_actual]
pico_hoy = pico_placa.get(dia_traducido, [])


# Leer archivo Excel 
df = pd.read_excel("motos.xlsx")
df.columns = df.columns.str.strip().str.upper()  
# Función para extraer el primer número de la placa
def primer_numero(placa):
    match = re.search(r'\d', str(placa))
    return match.group(0) if match else ''

df['RESTRINGIDAS'] = df['PLACA'].apply(
    lambda placa: 'Restringida' if primer_numero(placa) in pico_hoy else 'Disponible'
)
# Función para aplicar estilos a las celdas según disponibilidad
def color_disponibilidad(valor):
    if valor == 'Disponible':
        return 'background-color: #d4edda; color: #155724;'
    elif valor == 'Restringida':
        return 'background-color: #f8d7da; color: #721c24;'
    return ''

df_restringidas = df[df['RESTRINGIDAS'] == 'Restringida']
styled_motos = df_restringidas.style.applymap(color_disponibilidad, subset=['RESTRINGIDAS'])

# Pico y placa por día para carros 
pico_placa_carro = {
    'Lunes': ['3', '4'],
    'Martes': ['2', '8'],
    'Miércoles': ['5', '9'],
    'Jueves': ['1', '7'],
    'Viernes': ['0', '6'],
}
# Obtener el día actual 
dia_actual = datetime.datetime.now().strftime('%A')
dia_traducido = {
    'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
    'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
}[dia_actual]
pico_hoy_carro = pico_placa_carro.get(dia_traducido, [])

# Leer archivo Excel y preparar DataFrame para carros
df_carro = pd.read_excel("carro.xlsx")
df_carro.columns = df_carro.columns.str.strip().str.upper()  
# Función para extraer el último número de la placa
def ultimo_numero_carro(placa):
    numeros = re.findall(r'\d', str(placa))
    return numeros[-1] if numeros else ''

df_carro['RESTRINGIDAS'] = df_carro['PLACA'].apply(
    lambda placa: 'Restringida' if ultimo_numero_carro(placa) in pico_hoy_carro else 'Disponible'
)
# Función para aplicar estilos a las celdas según disponibilidad de carros
def color_disponibilidad_carro(valor):
    if valor == 'Disponible':
        return 'background-color: #d4edda; color: #155724;'
    elif valor == 'Restringida':
        return 'background-color: #f8d7da; color: #721c24;'
    return ''

df_carro_restringidas = df_carro[df_carro['RESTRINGIDAS'] == 'Restringida']
styled_carros = df_carro_restringidas.style.applymap(color_disponibilidad_carro, subset=['RESTRINGIDAS'])
# Función para obtener el clima actual
def obtener_clima(ciudad):
    API_KEY = "280c7d237a0b8a5d8572124200f1f167" 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
    try:
        response = requests.get(url).json()
        if response.get('main'):
            temp = response['main']['temp']
            temp_min = response['main']['temp_min']
            temp_max = response['main']['temp_max']
            desc = response['weather'][0]['description']
            return f"{temp}°C, {desc.capitalize()}, Mín: {temp_min}°C / Máx: {temp_max}°C"
        elif response.get('message'):
            return f"Error: {response['message']}"
    except Exception as e:
        return f"Error al obtener el clima: {e}"
    return "Datos no disponibles"

# Slider automático entre secciones
with st.container():
    if seccion == 0:
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h2 style='color: #fab70e; text-align: center;'>Pico y Placa en Medellin 🚫</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color:#19277f; color:white; padding:15px; border-radius:8px; font-size:20px; text-align:center;">
                    Hoy {dia_traducido}, hay restricción para placas: <strong>{', '.join(pico_hoy) if pico_hoy else 'Sin restricción'}</strong>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<h2 style='color: #fab70e; text-align: center;'>Clima Actual 🌦️</h2>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background-color:#19277f; color:#fff; padding:15px; border-radius:8px; font-size:20px; text-align:center;">
                    {obtener_clima("Medellín")}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
            <div style="background-color:#fdf6e3; padding:20px; border-radius:12px; margin-bottom:20px;">
                <h2 style='color: #fab70e; text-align: center;'>Motos Restringidas 🏍️</h2>
        """, unsafe_allow_html=True)
        st.dataframe(styled_motos, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    elif seccion == 1:
        
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h2 style='color: #fab70e; text-align: center;'>Pico y Placa en Medellin 🚫 </h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color:#19277f; color:white; padding:15px; border-radius:8px; font-size:20px; text-align:center;">
                    Hoy {dia_traducido}, hay restricción para placas: <strong>{', '.join(pico_hoy) if pico_hoy else 'Sin restricción'}</strong>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<h2 style='color: #fab70e; text-align: center;'>Clima Actual 🌦️</h2>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="background-color:#19277f; color:#fff; padding:15px; border-radius:8px; font-size:20px; text-align:center;">
                    {obtener_clima("Medellín")}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
            <div style="background-color:#fdf6e3; padding:20px; border-radius:12px; margin-bottom:20px;">
                <h2 style='color: #fab70e; text-align: center;'>Carros/ Motocarros Restringidos 🚚</h2>
        """, unsafe_allow_html=True)
        st.dataframe(styled_carros, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

#logo 
        st.markdown("</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 3])  
with col2:
    st.image("logo.png", width=200)

st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #19277f;">
        <p>© 2025 Muelles y Frenos Simón Bolívar. Todos los derechos reservados.</p>
    </div>
""", unsafe_allow_html=True)


