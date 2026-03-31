import streamlit as st
from supabase import create_client

# 1. Configuración de conexión (Lee de Secrets en Streamlit Cloud)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 2. Funciones de Usuario y Login
def obtener_usuario(email):
    """Busca un usuario y trae los datos de su empresa asociada."""
    try:
        res = supabase.table("usuarios").select("*, empresas(*)").eq("email", email).single().execute()
        return res.data
    except Exception:
        return None

# 3. Funciones de Filtrado y Seguridad
def filtrar_por_empresa(tabla):
    """Asegura que cada cliente solo vea sus propios datos."""
    if "empresa_id" in st.session_state:
        return supabase.table(tabla).select("*").eq("empresa_id", st.session_state.empresa_id).execute()
    return None

def validar_suscripcion(empresa_id):
    """Verifica el estado de pago de la empresa."""
    try:
        res = supabase.table("empresas").select("fecha_vencimiento, estado").eq("id", empresa_id).single().execute()
        return res.data
    except Exception:
        return None

# 4. Gestión de Archivos (Storage)
def subir_archivo_storage(file, empresa_id, nombre_archivo):
    """Sube archivos al bucket 'documentos_sgi' organizado por carpetas de empresa."""
    path = f"{empresa_id}/documentos/{nombre_archivo}"
    try:
        supabase.storage.from_("documentos_sgi").upload(path, file, {"upsert": "true"})
        return supabase.storage.from_("documentos_sgi").get_public_url(path)
    except Exception as e:
        st.error(f"Error al subir: {e}")
        return None
