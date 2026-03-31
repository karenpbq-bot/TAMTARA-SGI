import streamlit as st

# 1. CONFIGURACIÓN DE PÁGINA (Colores suaves de TAMTARA)
# Esto debe ser lo primero que ejecute el script
st.set_page_config(
    page_title="App del SGI | TAMTARA",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. IMPORTACIONES MODULARES
# Importamos el login después de configurar la página
from login import mostrar_login

# 3. CONTROL DE SESIÓN (Estado de Autenticación)
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# 4. LÓGICA DE NAVEGACIÓN
if not st.session_state.autenticado:
    # Si no está logueado, muestra la pantalla de acceso
    mostrar_login()
else:
    # --- INTERFAZ PRINCIPAL (POST-LOGIN) ---
    
    # Barra Lateral Personalizada con el Logo de la Empresa del Cliente
    with st.sidebar:
        if st.session_state.logo_empresa:
            st.image(st.session_state.logo_empresa, width=120)
        else:
            st.image("Logo Tamtara sin nombre.png", width=100)
            
        st.title(f"SGI {st.session_state.nombre_empresa}")
        st.divider()
        
        st.write(f"👤 **Usuario:** {st.session_state.usuario}")
        st.write(f"🔑 **Rol:** {st.session_state.rol}")
        
        st.divider()
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # Cuerpo de la aplicación
    st.title(f"Bienvenido a la App del SGI")
    st.info(f"Has ingresado correctamente al sistema de {st.session_state.nombre_empresa}.")
    
    # Aquí es donde llamaremos a documentos.py, proyectos.py, etc.
    st.write("Seleccione un módulo en el menú lateral para comenzar.")
