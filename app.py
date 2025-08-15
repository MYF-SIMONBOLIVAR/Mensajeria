import streamlit as st
import pandas as pd
import datetime
import requests
from streamlit_autorefresh import st_autorefresh
import re
import time
import pyodbc
import os
import pyodbc
from dotenv import load_dotenv

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

# Obtener las credenciales desde las variables de entorno
server = os.getenv('DB_SERVER')
database = os.getenv('DB_NAME')
username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
# Auto-refresh para cambiar entre secciones
count = st_autorefresh(interval=60000, key="auto_refresh")
seccion = count % 4

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

hora_actual = datetime.datetime.now().strftime("%I:%M %p")  

#Título 
st.markdown("<h1 style='text-align: center; color: #19277f;'>Muelles y Frenos Simón Bolívar</h1>", unsafe_allow_html=True)

# Pico y placa por día
pico_placa = {
    'Lunes': ['6', '9'],
    'Martes': ['5', '7'],
    'Miércoles': ['1', '8'],
    'Jueves': ['0', '2'],
    'Viernes': ['3', '4'],
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
    'Lunes': ['6', '9'],
    'Martes': ['5', '7'],
    'Miércoles': ['1', '8'],
    'Jueves': ['0', '2'],
    'Viernes': ['3', '4'],
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
# Función para aplicar estilos a las celdas 
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
# Mostrar la sección de motos
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
# mostrar la sección de carros y motocarros
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

# Sección de despachos
if seccion == 2:
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

    st.markdown("""
        <div style="background-color:#fdf6e3; padding:20px; border-radius:12px; margin-bottom:20px;">
            <h2 style='color: #fab70e; text-align: center;'>Despachos Programados 🚚</h2>
            <p style='text-align: center; color: #19277f; font-size: 18px;'>Aquí podrás ver los despachos programados para el día de hoy.</p>
        </div>
    """, unsafe_allow_html=True)

    # Leer los despachos desde un archivo Excel
    try:
        df_despachos = pd.read_excel("Despachos.xlsx")  # Leer desde el archivo Excel
        df_despachos.columns = df_despachos.columns.str.strip().str.upper()  # Limpiar nombres de columnas

        # Asegúrate de que las columnas estén en el formato correcto
        df_despachos['FECHAABRE'] = pd.to_datetime(df_despachos['FECHAABRE'])
        df_despachos['FECHAENTREGA'] = pd.to_datetime(df_despachos['FECHAENTREGA'], errors='coerce')

        # Filtrar los despachos programados para hoy
        fecha_actual = datetime.datetime.now().date()
        df_despachos_hoy = df_despachos[df_despachos['FECHAABRE'].dt.date == fecha_actual]

        # Crear una columna con el tiempo transcurrido
        df_despachos_hoy['TIEMPO_TRANSCURRIDO'] = df_despachos_hoy.apply(
            lambda row: f"{(row['FECHAENTREGA'] - row['FECHAABRE']).seconds // 3600}h " 
                        f"{((row['FECHAENTREGA'] - row['FECHAABRE']).seconds // 60) % 60}m" 
            if pd.notnull(row['FECHAENTREGA']) else 'PENDIENTE', axis=1
        )

        if df_despachos_hoy.empty:
            st.markdown(
                "<p style='text-align: center; color: #19277f;'>No hay despachos programados para hoy.</p>",
                unsafe_allow_html=True
            )
        else:
            st.dataframe(df_despachos_hoy[['NROCARGUE', 'USUARIOABRE', 'FECHAABRE', 'FECHAENTREGA', 'TIEMPO_TRANSCURRIDO']], use_container_width=True)

    except Exception as e:
        st.markdown(f"<p style='text-align: center; color: red;'>Error al cargar los datos de despachos: {e}</p>", unsafe_allow_html=True)

# Sección de ranking de despachos
elif seccion == 3:
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

    st.markdown("""
        <div style="background-color:#fdf6e3; padding:20px; border-radius:12px; margin-bottom:20px;">
            <h2 style='color: #fab70e; text-align: center;'>Ranking de Despachos 🚚</h2>
            <p style='text-align: center; color: #19277f; font-size: 18px;'>En esta sección podrás ver el ranking de despachos programados en el transcurso del día.</p>
        </div>
    """, unsafe_allow_html=True)

    # Leer el ranking desde un archivo Excel
    try:
        df_ranking = pd.read_excel("Ranking.xlsx")  # Leer desde el archivo Excel
        df_ranking.columns = df_ranking.columns.str.strip().str.upper()  # Limpiar nombres de columnas

        # Asegúrate de que las columnas estén en el formato correcto
        df_ranking['FECHAABRE'] = pd.to_datetime(df_ranking['FECHAABRE'])
        df_ranking['FECHAENTREGA'] = pd.to_datetime(df_ranking['FECHAENTREGA'], errors='coerce')

        # Filtrar el ranking de despachos para hoy
        fecha_actual = datetime.datetime.now().date()
        df_ranking_hoy = df_ranking[df_ranking['FECHAABRE'].dt.date == fecha_actual]

        # Agrupar por usuario y contar los despachos entregados
        df_ranking_hoy = df_ranking_hoy.groupby('USUARIOABRE').agg(
            PEDIDOS_ENTREGADOS=('NROCARGUE', 'count'),
            TIEMPO_TRANSCURRIDO_PROMEDIO=('FECHAENTREGA', lambda x: (x.max() - x.min()).seconds // 3600)
        ).reset_index()

        if df_ranking_hoy.empty:
            st.markdown(
                "<p style='text-align: center; color: #19277f;'>No hay datos de ranking disponibles para hoy.</p>",
                unsafe_allow_html=True
            )
        else:
            st.dataframe(df_ranking_hoy.sort_values(by='PEDIDOS_ENTREGADOS', ascending=False), use_container_width=True)

    except Exception as e:
        st.markdown(f"<p style='text-align: center; color: red;'>Error al cargar los datos de ranking: {e}</p>", unsafe_allow_html=True)

#logo empresa
        st.markdown("</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 3])  
with col2:
    st.image("logo.png", width=200)

# derechos reservados
st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #19277f;">
        <p>© 2025 Muelles y Frenos Simón Bolívar. Todos los derechos reservados.</p>
    </div>
""", unsafe_allow_html=True)















