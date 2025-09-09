import pandas as pd
import numpy as np
import datetime
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.app_logo import add_logo
import time
import base64

st.set_page_config(layout="wide", page_title="Sistema de Planificación",
                   page_icon="📊", initial_sidebar_state="expanded")

# Estilo CSS personalizado
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #0068c9;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #004e96;
    }
    .stProgress .st-bo {
        background-color: #0068c9;
    }
    h1, h2, h3 {
        color: #0068c9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f3f4;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-left: 10px;
        padding-right: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0068c9;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# Funciones existentes sin cambios
def get_first_datetime_of_month(month_name):
    # Código sin cambios
    try:
        current_date = datetime.datetime.now()

        if month_name == "January" and current_date.month > 1:
            year = current_date.year + 1
        else:
            year = current_date.year

        date_object = datetime.datetime.strptime(month_name, "%B")
        month_number = date_object.month

        first_day_of_month = datetime.datetime(year, month_number, 1, 0, 0, 0)
        return first_day_of_month
    except ValueError:
        st.error(f"Error: Nombre de mes inválido '{month_name}'.")
        return None


def load_VF(path):
    try:
        return pd.read_excel(path, sheet_name="Pivot", skiprows=3)
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return None


def download_csv_button(df, filename, text="Descargar CSV"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">⬇️ {text}</a>'
    return href


def generate(table, month):
    # Mostrar progreso
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(100):
        if i < 20:
            status_text.text("Cargando datos...")
        elif i < 40:
            status_text.text("Procesando tablas...")
        elif i < 70:
            status_text.text("Generando reportes...")
        elif i < 90:
            status_text.text("Finalizando...")
        else:
            status_text.text("¡Listo!")
        progress_bar.progress(i + 1)
        time.sleep(0.01)

    # Resto del código de generación sin cambios
    month_dict = {
        "January": "Suma de ene",
        "February": "Suma de feb",
        "March": "Suma de mar",
        "April": "Suma de abr",
        "May": "Suma de may",
        "June": "Suma de jun",
        "July": "Suma de jul",
        "August": "Suma de ago",
        "September": "Suma de sep",
        "October": "Suma de oct",
        "November": "Suma de nov",
        "December": "Suma de dic"
    }

    try:
        df_VF = load_VF(table)
        if df_VF is None:
            return

        df_VF_maq = df_VF.loc[df_VF["Line"].isin(['LMAQ-ENV', 'LMAQ-ETI', 'LMAQ-FAR', 'LMAQ-IUS', 'LMAQ-REN'])]
        df_products = df_VF_maq[["Product Number", "Product Short Description", "Config"]]
        df_products.columns = ["codigo_del_producto", "descripcion", "familia"]
        df_products = df_products.drop_duplicates(subset=["codigo_del_producto"])
        df_products = df_products.reset_index()
        df_products = df_products[["codigo_del_producto", "descripcion", "familia"]]
        st.session_state.df_products = df_products

        # Resto del código de procesamiento sin cambios
        line_mapping = {
            'LMAQ-ENV': 'Envatec',
            'LMAQ-ETI': 'Etipack',
            'LMAQ-FAR': 'Fareva',
            'LMAQ-IUS': 'IUISA',
            'LMAQ-REN': 'Renopac'
        }

        df_VF_maq['Line'] = df_VF_maq['Line'].map(line_mapping)
        df_Plan = df_VF_maq[["Line", "Config", "Product Number", month_dict[month]]]
        df_Plan = df_Plan.dropna(subset=[month_dict[month]])
        df_Plan = df_Plan.reset_index(level=None, drop=True, inplace=False, col_level=0, col_fill='')
        df_Plan = df_Plan.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
        df_Plan["fecha"] = get_first_datetime_of_month(month).strftime('%d-%m-%Y %H:%M')
        df_Plan = df_Plan[["index", "Line", "fecha", "Product Number", month_dict[month]]]
        df_Plan.columns = ["Titulo", "nombre", "fecha", "codigo_del_producto", "cantidad"]
        st.session_state.df_Plan = df_Plan

        # Código para procesar cada línea
        df_prod_CM = df_VF_maq[["Line", "Product Number"]]

        for line, line_name in line_mapping.items():
            df_filtered = df_prod_CM.loc[df_prod_CM["Line"] == line_name]
            df_filtered = df_filtered.reset_index(drop=True).reset_index()
            df_filtered = df_filtered[["index", "Product Number"]]
            df_filtered.columns = ["ID", "Producto"]
            st.session_state[f"df_prod_{line_name.lower()}"] = df_filtered

        status_text.text("¡Datos generados correctamente!")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()

        st.session_state.generated = True

    except Exception as e:
        st.error(f"Error al generar tablas: {str(e)}")
        status_text.empty()
        progress_bar.empty()
        return


# Sidebar
with st.sidebar:
    st.title("Panel de Control")
    st.info("Esta aplicación permite generar tablas de planificación a partir de un archivo Excel.")

    with st.expander("❓ Ayuda"):
        st.markdown("""
        ### Instrucciones:
        1. Carga el archivo Excel de planeación
        2. Selecciona el mes para los datos
        3. Presiona el botón "Generar Tablas"
        4. Explora los resultados en las pestañas
        """)

    st.divider()
    st.caption("© 2023 Sistema de Planificación v1.0")

# Contenido principal
colored_header(label="Sistema de Planificación de Producción",
               description="Genera tablas de planificación basadas en datos de producción",
               color_name="blue-green-70")

# Sección de carga de datos
st.subheader("📤 Carga de datos")

col1, col2 = st.columns([2, 1])
with col1:
    table_VF = st.file_uploader("Selecciona el archivo de Planeación VF", type="xlsx",
                                help="El archivo debe tener una hoja llamada 'Pivot'")
with col2:
    month = st.selectbox(
        "Selecciona el mes",
        ["Selecciona una opción", "January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"],
        help="Mes para el cual se generarán las tablas"
    )

generate_button = st.button("✨ Generar Tablas", use_container_width=True,
                            help="Haz clic para procesar los datos y generar las tablas")

# Validación y generación
if generate_button:
    if month == "Selecciona una opción":
        st.warning("⚠️ Por favor selecciona un mes válido")
    elif table_VF is None:
        st.warning("⚠️ Por favor carga un archivo Excel")
    else:
        generate(table_VF, month)

st.divider()

# Mostrar resultados
if 'generated' in st.session_state and st.session_state.generated:
    tabs = st.tabs(["📊 Resumen", "🏭 Productos", "📅 Plan", "🏢 Maquiladores"])

    with tabs[0]:
        st.subheader("Resumen de datos")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Productos", len(st.session_state.df_products))
        with col2:
            st.metric("Total Plan", len(st.session_state.df_Plan))
        with col3:
            st.metric("Mes Seleccionado", month)

        st.success(f"Se generaron correctamente todas las tablas para el mes de {month}")

    with tabs[1]:
        st.subheader("Tabla de Productos")

        # Agregar búsqueda/filtro
        search = st.text_input("🔍 Buscar producto", "")
        if search:
            filtered_df = st.session_state.df_products[
                st.session_state.df_products["codigo_del_producto"].str.contains(search, case=False) |
                st.session_state.df_products["descripcion"].str.contains(search, case=False)
                ]
        else:
            filtered_df = st.session_state.df_products

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        st.markdown(download_csv_button(filtered_df, "productos"), unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("Tabla de Plan de Producción")
        st.dataframe(st.session_state.df_Plan, use_container_width=True, hide_index=True)
        st.markdown(download_csv_button(st.session_state.df_Plan, "plan_produccion"), unsafe_allow_html=True)

    with tabs[3]:
        maquilas_tabs = st.tabs(["Envatec", "Etipack", "Fareva", "IUISA", "Renopac"])

        for i, maq in enumerate(["envatec", "etipack", "fareva", "iuisa", "renopac"]):
            with maquilas_tabs[i]:
                st.subheader(f"Productos para {maq.capitalize()}")
                df_name = f"df_prod_{maq}"
                if df_name in st.session_state:
                    st.dataframe(st.session_state[df_name], use_container_width=True, hide_index=True)
                    st.markdown(download_csv_button(st.session_state[df_name], f"productos_{maq}"),
                                unsafe_allow_html=True)

