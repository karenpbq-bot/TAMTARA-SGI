import streamlit as st
import os

# --- Lógica para localizar el logo en el servidor ---
directorio_actual = os.path.dirname(__file__)
nombre_archivo_logo = "Logo Tamtara sin nombre.png"
ruta_logo = os.path.join(directorio_actual, nombre_archivo_logo)

# 1. CONFIGURACIÓN DE PÁGINA (Favicon y Título)
# Usamos tu logo en 'page_icon' para que aparezca en la pestaña del navegador
st.set_page_config(
    page_title="App del SGI | TAMTARA",
    page_icon=ruta_logo if os.path.exists(ruta_logo) else "🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. IMPORTACIONES MODULARES
from login import mostrar_login

# 3. CONTROL DE SESIÓN
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# 4. LÓGICA DE NAVEGACIÓN
if not st.session_state.autenticado:
    # Pantalla de acceso
    mostrar_login()
else:
    # --- INTERFAZ PRINCIPAL (POST-LOGIN) ---
    
    # Barra Lateral con los colores de TAMTARA
    with st.sidebar:
        # Prioridad: Logo del Cliente -> Si no hay, Logo de TAMTARA
        if st.session_state.logo_empresa:
            st.image(st.session_state.logo_empresa, width=120)
        else:
            if os.path.exists(ruta_logo):
                st.image(ruta_logo, width=120)
            else:
                st.write("📌 **TAMTARA SGI**")
            
        st.title(f"SGI {st.session_state.nombre_empresa}")
        st.divider()
        
        st.write(f"👤 **Usuario:** {st.session_state.usuario}")
        st.write(f"🔑 **Rol:** {st.session_state.rol}")
        
        st.divider()
        
        # Botón de cierre de sesión con estilo
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # Cuerpo de la aplicación (Bienvenidos)
    st.title(f"Bienvenido a la App del SGI")
    st.info(f"Has ingresado correctamente al sistema de **{st.session_state.nombre_empresa}**.")
    
    # Espacio para los futuros módulos (documentos.py, etc.)
    st.write("---")
    st.subheader("Panel de Control")
    st.write("Seleccione un módulo en el menú lateral para comenzar a gestionar sus procesos.")
