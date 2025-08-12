import streamlit as st
import pandas as pd
import datetime
import requests
from streamlit_autorefresh import st_autorefresh
import re
import pyodbc

# =====================
# Configuración inicial
# =====================
st.set_page_config(layout="wide")

# Auto-refresh cada 10 segundos
count = st_autorefresh(interval=60000, key="auto_refresh")
seccion = count % 4

# Obtener credenciales desde secrets
server = st.secrets["DB_SERVER"]
database = st.secrets["DB_NAME"]
username = st.secrets["DB_USER"]
password = st.secrets["DB_PASSWORD"]
driver = st.secrets["driver"]
OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"]

# =====================
# Estilos CSS
# =====================
st.markdown("""
    <style>
    body, .stApp { background-color: #e3f0fc !important; }
    .fade-in { animation: fadeIn 1s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .block-container { padding-top: 1rem !important; }
    h1 { margin-top: 0 !important; }
    </style>
""", unsafe_allow_html=True)

# =====================
# Hora actual
# =====================
hora_actual = datetime.datetime.now().strftime("%I:%M %p")

# Título
st.markdown("<h1 style='text-align: center; color: #19277f;'>Muelles y Frenos Simón Bolívar</h1>", unsafe_allow_html=True)

# =====================
# Pico y placa Motos
# =====================
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

df = pd.read_excel("motos.xlsx")
df.columns = df.columns.str.strip().str.upper()

def primer_numero(placa):
    match = re.search(r'\d', str(placa))
    return match.group(0) if match else ''

df['RESTRINGIDAS'] = df['PLACA'].apply(
    lambda placa: 'Restringida' if primer_numero(placa) in pico_hoy else 'Disponible'
)

def color_disponibilidad(valor):
    if valor == 'Disponible':
        return 'background-color: #d4edda; color: #155724;'
    elif valor == 'Restringida':
        return 'background-color: #f8d7da; color: #721c24;'
    return ''

df_restringidas = df[df['RESTRINGIDAS'] == 'Restringida']
styled_motos = df_restringidas.style.applymap(color_disponibilidad, subset=['RESTRINGIDAS'])

# =====================
# Pico y placa Carros
# =====================
pico_placa_carro = {
    'Lunes': ['6', '9'],
    'Martes': ['5', '7'],
    'Miércoles': ['1', '8'],
    'Jueves': ['0', '2'],
    'Viernes': ['3', '4'],
}
pico_hoy_carro = pico_placa_carro.get(dia_traducido, [])

df_carro = pd.read_excel("carro.xlsx")
df_carro.columns = df_carro.columns.str.strip().str.upper()

def ultimo_numero_carro(placa):
    numeros = re.findall(r'\d', str(placa))
    return numeros[-1] if numeros else ''

df_carro['RESTRINGIDAS'] = df_carro['PLACA'].apply(
    lambda placa: 'Restringida' if ultimo_numero_carro(placa) in pico_hoy_carro else 'Disponible'
)

def color_disponibilidad_carro(valor):
    if valor == 'Disponible':
        return 'background-color: #d4edda; color: #155724;'
    elif valor == 'Restringida':
        return 'background-color: #f8d7da; color: #721c24;'
    return ''

df_carro_restringidas = df_carro[df_carro['RESTRINGIDAS'] == 'Restringida']
styled_carros = df_carro_restringidas.style.applymap(color_disponibilidad_carro, subset=['RESTRINGIDAS'])

# =====================
# Función clima
# =====================
def obtener_clima(ciudad):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={OPENWEATHER_API_KEY}&units=metric&lang=es"
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

# =====================
# Secciones
# =====================
with st.container():
    if seccion == 0:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h2 style='color: #fab70e; text-align: center;'>Pico y Placa en Medellín 🚫</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color:#19277f; color:white; padding:15px; border-radius:8px; font-size:20px; text-align:center;">
                    Hoy {dia_traducido}, hay restricción para placas: <strong>{', '.join(pico_hoy) if pico_hoy else 'Sin restricción'}</strong>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<h2 style='color: #fab70e; text-align: center;'>Clima Actual 🌦️</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color:#19277f; color:#fff; padding:15px; border-radius:8px; font-size:20px; text-align:center;">
                    {obtener_clima("Medellín")}
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #fab70e; text-align: center;'>Motos Restringidas 🏍️</h2>", unsafe_allow_html=True)
        st.dataframe(styled_motos, use_container_width=True)

    elif seccion == 1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h2 style='color: #fab70e; text-align: center;'>Pico y Placa en Medellín 🚫</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color:#19277f; color:white; padding:15px; border-radius:8px; font-size:20px; text-align:center;">
                    Hoy {dia_traducido}, hay restricción para placas: <strong>{', '.join(pico_hoy_carro) if pico_hoy_carro else 'Sin restricción'}</strong>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<h2 style='color: #fab70e; text-align: center;'>Clima Actual 🌦️</h2>", unsafe_allow_html=True)
            st.markdown(f"""
                <div style="background-color:#19277f; color:#fff; padding:15px; border-radius:8px; font-size:20px; text-align:center;">
                    {obtener_clima("Medellín")}
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #fab70e; text-align: center;'>Carros/Motocarros Restringidos 🚚</h2>", unsafe_allow_html=True)
        st.dataframe(styled_carros, use_container_width=True)

    elif seccion == 2:
        st.markdown("<h2 style='color: #fab70e; text-align: center;'>Despachos 🚚</h2>", unsafe_allow_html=True)
        try:
           conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
           conn = pyodbc.connect(conn_str)
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
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
                st.info("No hay despachos programados para hoy.")
            else:
                st.dataframe(df_despachos, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo conectar a la base de datos: {e}")

    elif seccion == 3:
        st.markdown("<h2 style='color: #fab70e; text-align: center;'>Ranking de Despachos 🚚</h2>", unsafe_allow_html=True)
        try:
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
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
                st.info("No hay datos de ranking disponibles para hoy.")
            else:
                st.dataframe(df_ranking, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo conectar a la base de datos: {e}")

# Logo y derechos
col1, col2, col3 = st.columns([3, 1, 3])
with col2:
    st.image("logo.png", width=200)

st.markdown("""
    <div style="text-align: center; margin-top: 20px; color: #19277f;">
        <p>© 2025 Muelles y Frenos Simón Bolívar. Todos los derechos reservados.</p>
    </div>
""", unsafe_allow_html=True)




