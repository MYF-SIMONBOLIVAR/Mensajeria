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
server = 192.168.1.8,
database = KONTROLAR_MUELLESSB,
username = KontrolarEsc,
password = K0ntr0l4rS0luc10n3s2023

# Auto-refresh para cambiar entre secciones
count = st_autorefresh(interval=10000, key="auto_refresh")
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

#seccion despachos
    elif seccion == 2:
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

        st.markdown("""
            <div style="background-color:#fdf6e3; padding:20px; border-radius:12px; margin-bottom:20px;">
                <h2 style='color: #fab70e; text-align: center;'>Despachos 🚚</h2>
                <p style='text-align: center; color: #19277f; font-size: 18px;'>En esta sección podrás ver los despachos programados en el transcurso del dia.</p>
            </div>
        """, unsafe_allow_html=True)

        # Conectar a la base de datos
        conn = pyodbc.connect(
            f'Driver={{SQL Server}};'
            f'Server={server};'
            f'Database={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        query = """
        SELECT 
            [NroCargue],
            [UsuarioAbre],
            [FechaAbre],
            CASE 
                WHEN FechaEntrega = '1900-01-01 00:00:00.000' THEN 'PENDIENTE'
                ELSE FORMAT(FechaEntrega, 'yyyy-MM-dd HH:mm:ss.fff') 
            END AS FechaEntrega,
            CONCAT(
                DATEDIFF(MINUTE, FechaAbre, FechaEntrega) / 60, 'h ',
                DATEDIFF(MINUTE, FechaAbre, FechaEntrega) % 60, 'm'
            ) AS Tiempo_Transcurrido
        FROM [KONTROLAR_MUELLESSB].[dbo].[VTA_Transporte]
        WHERE CAST(FechaLectura AS DATE) = CAST(GETDATE() AS DATE)
        ORDER BY FechaLectura DESC;

        """

        df_despachos = pd.read_sql(query, conn)

        if df_despachos.empty:
            st.markdown(
                "<p style='text-align: center; color: #19277f;'>No hay despachos programados para hoy.</p>",
                unsafe_allow_html=True
            )
        else:
            st.dataframe(df_despachos, use_container_width=True)
#seccion de ranking 

    elif seccion == 3:
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)

        st.markdown("""
            <div style="background-color:#fdf6e3; padding:20px; border-radius:12px; margin-bottom:20px;">
                <h2 style='color: #fab70e; text-align: center;'>Ranking de Despachos 🚚</h2>
                <p style='text-align: center; color: #19277f; font-size: 18px;'>En esta sección podrás ver el ranking de despachos programados en el transurso del día.</p>
            </div>
        """, unsafe_allow_html=True)
        # Conectar a la base de datos
        conn = pyodbc.connect(
            f'Driver={{SQL Server}};'
            f'Server={server};'
            f'Database={database};'
            f'UID={username};'
            f'PWD={password};'
        )
        query_ranking = """
           SELECT 
            [UsuarioAbre],
            COUNT([NroCargue]) AS Pedidos_Entregados,
            CONCAT(
                DATEDIFF(MINUTE, MIN(FechaAbre), MAX(FechaEntrega)) / 60, 'h ',
                DATEDIFF(MINUTE, MIN(FechaAbre), MAX(FechaEntrega)) % 60, 'm'
            ) AS Tiempo_Transcurrido_Promedio
        FROM [KONTROLAR_MUELLESSB].[dbo].[VTA_Transporte]
        WHERE CAST(FechaLectura AS DATE) = CAST(GETDATE() AS DATE)
        GROUP BY [UsuarioAbre]
        ORDER BY Pedidos_Entregados DESC;
        """
        df_ranking = pd.read_sql(query_ranking, conn)

        if df_ranking.empty:
            st.markdown(
                "<p style='text-align: center; color: #19277f;'>No hay datos de ranking disponibles para hoy.</p>",
                unsafe_allow_html=True
            )
        else:
            st.dataframe(df_ranking)  

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











