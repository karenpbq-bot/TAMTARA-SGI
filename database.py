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

# --- Añadir al final de tu archivo database.py ---

def obtener_usuario(email):
    """
    Busca un usuario por su correo para el proceso de Login.
    """
    try:
        res = supabase.table("usuarios").select("*, empresas(*)").eq("email", email).single().execute()
        return res.data
    except Exception:
        return None

def subir_archivo_storage(file, empresa_id, nombre_archivo):
    """
    Sube archivos al bucket de Supabase organizados por empresa.
    """
    # Ruta modular: empresa_id/documentos/nombre_archivo
    path = f"{empresa_id}/documentos/{nombre_archivo}"
    
    try:
        # 'documentos_sgi' debe ser el nombre de tu bucket en Supabase
        res = supabase.storage.from_("documentos_sgi").upload(path, file, {"upsert": "true"})
        # Retorna la URL pública del archivo
        return supabase.storage.from_("documentos_sgi").get_public_url(path)
    except Exception as e:
        st.error(f"Error al subir: {e}")
        return None
