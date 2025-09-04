import pandas as pd
import numpy as np
import datetime
import streamlit as st
st.set_page_config(layout="wide")


def get_first_datetime_of_month(month_name):
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
        print(f"Error: Invalid month name '{month_name}'. Please provide a full month name (e.g., 'September').")
        return None


def load_VF(path):
    return pd.read_excel(path,sheet_name="Pivot",skiprows=3)



def generate(table, month):
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
    df_VF = load_VF(table)
    df_VF_maq = df_VF.loc[df_VF["Line"].isin(['LMAQ-ENV', 'LMAQ-ETI', 'LMAQ-FAR', 'LMAQ-IUS', 'LMAQ-REN'])]
    df_products = df_VF_maq[["Product Number", "Product Short Description", "Config"]]
    df_products.columns = ["codigo_del_producto", "descripcion", "familia"]
    df_products = df_products.drop_duplicates(subset=["codigo_del_producto"])
    df_products = df_products.reset_index()
    df_products = df_products[["codigo_del_producto", "descripcion", "familia"]]
    st.session_state.df_products = df_products

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

    df_prod_CM = df_VF_maq[["Line", "Product Number"]]

    df_prod_envatec = df_prod_CM.loc[df_prod_CM["Line"] == "Envatec"]
    df_prod_envatec = df_prod_envatec.reset_index(level=None, drop=True, inplace=False, col_level=0, col_fill='')
    df_prod_envatec = df_prod_envatec.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
    df_prod_envatec = df_prod_envatec[["index", "Product Number"]]
    df_prod_envatec.columns = ["ID", "Producto"]
    st.session_state.df_prod_envatec = df_prod_envatec

    df_prod_etipack = df_prod_CM.loc[df_prod_CM["Line"] == "Etipack"]
    df_prod_etipack = df_prod_etipack.reset_index(level=None, drop=True, inplace=False, col_level=0, col_fill='')
    df_prod_etipack = df_prod_etipack.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
    df_prod_etipack = df_prod_etipack[["index", "Product Number"]]
    df_prod_etipack.columns = ["ID", "Producto"]
    st.session_state.df_prod_etipack = df_prod_etipack

    df_prod_fareva = df_prod_CM.loc[df_prod_CM["Line"] == "Fareva"]
    df_prod_fareva = df_prod_fareva.reset_index(level=None, drop=True, inplace=False, col_level=0, col_fill='')
    df_prod_fareva = df_prod_fareva.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
    df_prod_fareva = df_prod_fareva[["index", "Product Number"]]
    df_prod_fareva.columns = ["ID", "Producto"]
    st.session_state.df_prod_fareva = df_prod_fareva

    df_prod_iuisa = df_prod_CM.loc[df_prod_CM["Line"] == "IUISA"]
    df_prod_iuisa = df_prod_iuisa.reset_index(level=None, drop=True, inplace=False, col_level=0, col_fill='')
    df_prod_iuisa = df_prod_iuisa.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
    df_prod_iuisa = df_prod_iuisa[["index", "Product Number"]]
    df_prod_iuisa.columns = ["ID", "Producto"]
    st.session_state.df_prod_iuisa = df_prod_iuisa

    df_prod_renopac = df_prod_CM.loc[df_prod_CM["Line"] == "Renopac"]
    df_prod_renopac = df_prod_renopac.reset_index(level=None, drop=True, inplace=False, col_level=0, col_fill='')
    df_prod_renopac = df_prod_renopac.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')
    df_prod_renopac = df_prod_renopac[["index", "Product Number"]]
    df_prod_renopac.columns = ["ID", "Producto"]
    st.session_state.df_prod_renopac = df_prod_renopac


st.title("Coyuntural")
table_VF = st.file_uploader("Select Planeación VF", type="xlsx")
month = st.selectbox(
    "Select Month",
    ["Select an option", "January", "February", "March", "April", "May", "June", "July", "August", "September",
     "October", "November", "December"]
)

if st.button("Generar Tablas") and month != "Select an option":
    generate(table_VF, month)

    if 'df_prod_renopac' in st.session_state:
        st.header("Tabla de Productos")
        st.dataframe(st.session_state.df_products)
        st.header("Tabla de Plan de Producción")
        st.dataframe(st.session_state.df_Plan)
        st.header("Tabla de Envatec")
        st.dataframe(st.session_state.df_prod_envatec)
        st.header("Tabla de Etipack")
        st.dataframe(st.session_state.df_prod_etipack)
        st.header("Tabla de Fareva")
        st.dataframe(st.session_state.df_prod_fareva)
        st.header("Tabla de IUISA")
        st.dataframe(st.session_state.df_prod_iuisa)
        st.header("Tabla de Renopac")
        st.dataframe(st.session_state.df_prod_renopac)




