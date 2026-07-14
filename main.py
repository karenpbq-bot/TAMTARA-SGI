import streamlit as st
import os

# --- Lógica para localizar el logo en el servidor ---
directorio_actual = os.path.dirname(__file__)
nombre_archivo_logo = "Logo Tamtara sin nombre.png"
ruta_logo = os.path.join(directorio_actual, nombre_archivo_logo)

# 1. CONFIGURACIÓN DE PÁGINA (Favicon y Título)
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

# 4. LÓGICA DE NAVEGACIÓN PRINCIPAL
if not st.session_state.autenticado:
    mostrar_login()
else:
    # --- INTERFAZ PRINCIPAL (POST-LOGIN) ---
    
    # Determinar opciones del menú según el nivel de administración
    # Al ser la creadora (TAMTARA), tendrás acceso a todas las opciones globales.
    es_admin = st.session_state.get("es_administradora", False)
    
    if es_admin:
        opciones_menu = ["🏠 Inicio", "👥 Gestión de Clientes", "📂 Documentos del SGI", "⚙️ Configuración Global"]
    else:
        opciones_menu = ["🏠 Inicio", "📂 Documentos del SGI"]

    # --- BARRA LATERAL ---
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
        
        # MENÚ DE NAVEGACIÓN DINÁMICO
        st.subheader("Navegación")
        modulo_seleccionado = st.radio(
            "Seleccione un módulo:",
            options=opciones_menu,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Botón de cierre de sesión
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # --- CUERPO PRINCIPAL (RENDERIZADO DINÁMICO) ---
    
    if modulo_seleccionado == "🏠 Inicio":
        st.title(f"Bienvenido a la App del SGI")
        st.info(f"Has ingresado correctamente al sistema de **{st.session_state.nombre_empresa}**.")
        st.write("---")
        st.subheader("Panel de Control")
        st.write("Utiliza el menú lateral de navegación para gestionar tus procesos de SGI de forma centralizada.")
        
    elif modulo_seleccionado == "👥 Gestión de Clientes":
        st.title("👥 Gestión de Clientes (TAMTARA)")
        st.write("---")
        try:
            # Importación bajo demanda del archivo clientes.py
            import clientes
            # Aquí llamaremos a la función principal que contendrá clientes.py
            if hasattr(clientes, "mostrar_modulo_clientes"):
                clientes.mostrar_modulo_clientes()
            else:
                st.warning("El módulo de clientes está listo para recibir el código. Por ahora no contiene la función 'mostrar_modulo_clientes'.")
        except ModuleNotFoundError:
            st.error("No se encontró el archivo modular 'clientes.py'. Asegúrate de que exista en tu directorio.")
            
    elif modulo_seleccionado == "📂 Documentos del SGI":
        st.title("📂 Gestión Documental del SGI")
        st.write("---")
        st.info("Aquí podrás subir, filtrar y organizar los documentos del Sistema de Gestión Integrado.")
        # Posteriormente importaremos un módulo de documentos aquí
        
    elif modulo_seleccionado == "⚙️ Configuración Global":
        st.title("⚙️ Configuración de la Plataforma")
        st.write("---")
        st.info("Panel exclusivo para TAMTARA. Modificación de parámetros de la base de datos, licencias y auditorías.")
