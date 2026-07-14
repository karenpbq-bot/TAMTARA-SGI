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
    
    # Verificamos si es la empresa administradora (TAMTARA)
    es_admin = st.session_state.get("es_administradora", False)
    
    # Definimos los menús correspondientes
    if es_admin:
        opciones_menu = [
            "🏠 Inicio TAMTARA", 
            "👥 Gestión de Clientes", 
            "⚙️ Configuración Global"
        ]
    else:
        # Los módulos transaccionales que generarán la data para el cliente
        opciones_menu = [
            "📂 Documentos del SGI",
            "📊 Gestión de Indicadores",
            "📈 Gestión de Mejora",
            "📝 Auditoría y Autoevaluación",
            "🔄 Gestión de Procesos"
        ]

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
        
        # MENÚ DE NAVEGACIÓN
        st.subheader("Menú del SGI")
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
    
    # --- VISTAS DEL ADMINISTRADOR (TAMTARA) ---
    if modulo_seleccionado == "🏠 Inicio TAMTARA":
        st.title("Panel Administrativo de TAMTARA SGI")
        st.info("Has ingresado como Administrador Global del Sistema de Gestión Integrado.")
        st.write("---")
        st.subheader("Indicadores del Negocio")
        st.write("Aquí se visualizarán las métricas de tus clientes activos, estado de sus suscripciones y alertas de soporte.")

    elif modulo_seleccionado == "👥 Gestión de Clientes":
        st.title("👥 Gestión de Clientes (TAMTARA)")
        st.write("---")
        try:
            import clientes
            if hasattr(clientes, "mostrar_modulo_clientes"):
                clientes.mostrar_modulo_clientes()
            else:
                st.info("Módulo 'clientes.py' cargado correctamente. Listo para recibir la función 'mostrar_modulo_clientes'.")
        except ModuleNotFoundError:
            st.error("No se encontró el archivo modular 'clientes.py' en el directorio.")

    elif modulo_seleccionado == "⚙️ Configuración Global":
        st.title("⚙️ Configuración Global de la Plataforma")
        st.write("---")
        st.info("Configuraciones del sistema, administración de base de datos y logs de auditoría.")

    # --- VISTAS DEL CLIENTE (MÓDULOS DE DATA) ---
    elif modulo_seleccionado == "📂 Documentos del SGI":
        st.title("📂 Gestión Documental del SGI")
        st.write("---")
        try:
            import documentos
            if hasattr(documentos, "mostrar_modulo_documentos"):
                documentos.mostrar_modulo_documentos()
            else:
                st.info("Módulo de Gestión Documental. Listo para recibir la función 'mostrar_modulo_documentos'.")
        except ModuleNotFoundError:
            st.warning("El archivo modular 'documentos.py' aún no ha sido creado en el directorio.")

    elif modulo_seleccionado == "📊 Gestión de Indicadores":
        st.title("📊 Gestión de Indicadores")
        st.write("---")
        try:
            import indicadores
            if hasattr(indicadores, "mostrar_modulo_indicadores"):
                indicadores.mostrar_modulo_indicadores()
            else:
                st.info("Módulo de Gestión de Indicadores (KPIs). Listo para recibir la función 'mostrar_modulo_indicadores'.")
        except ModuleNotFoundError:
            st.warning("El archivo modular 'indicadores.py' aún no ha sido creado en el directorio.")

    elif modulo_seleccionado == "📈 Gestión de Mejora":
        st.title("📈 Gestión de Mejora")
        st.write("---")
        try:
            import mejora
            if hasattr(mejora, "mostrar_modulo_mejora"):
                mejora.mostrar_modulo_mejora()
            else:
                st.info("Módulo de Acciones Correctivas y Preventivas (CAPA). Listo para recibir la función 'mostrar_modulo_mejora'.")
        except ModuleNotFoundError:
            st.warning("El archivo modular 'mejora.py' aún no ha sido creado en el directorio.")

    elif modulo_seleccionado == "📝 Auditoría y Autoevaluación":
        st.title("📝 Auditoría y Autoevaluación")
        st.write("---")
        try:
            import auditorias
            if hasattr(auditorias, "mostrar_modulo_auditorias"):
                auditorias.mostrar_modulo_auditorias()
            else:
                st.info("Módulo de Planificación y Ejecución de Auditorías. Listo para recibir la función 'mostrar_modulo_auditorias'.")
        except ModuleNotFoundError:
            st.warning("El archivo modular 'auditorias.py' aún no ha sido creado en el directorio.")

    elif modulo_seleccionado == "🔄 Gestión de Procesos":
        st.title("🔄 Gestión de Procesos")
        st.write("---")
        try:
            import procesos
            if hasattr(procesos, "mostrar_modulo_procesos"):
                procesos.mostrar_modulo_procesos()
            else:
                st.info("Módulo de Caracterización de Procesos y Flujogramas. Listo para recibir la función 'mostrar_modulo_procesos'.")
        except ModuleNotFoundError:
            st.warning("El archivo modular 'procesos.py' aún no ha sido creado en el directorio.")
