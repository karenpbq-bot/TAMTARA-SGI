import streamlit as st
from supabase import create_client

# Configuración de conexión (usando st.secrets para GitHub/Streamlit Cloud)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

def filtrar_por_empresa(tabla):
    """
    Función maestra para asegurar el aislamiento de datos.
    """
    if "empresa_id" in st.session_state:
        return supabase.table(tabla).select("*").eq("empresa_id", st.session_state.empresa_id).execute()
    return None

def validar_suscripcion(empresa_id):
    """
    Verifica si la empresa tiene el pago al día.
    """
    res = supabase.table("empresas").select("fecha_vencimiento, estado").eq("id", empresa_id).single().execute()
    return res.data
