import streamlit as st
import time
import os
import base64  # Librería necesaria para convertir la imagen
from datetime import datetime
from database import obtener_usuario 

def get_base64(bin_file):
    """Función para convertir la imagen a base64 para el CSS"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def mostrar_login():
    # --- Localización del logo ---
    directorio_actual = os.path.dirname(__file__)
    nombre_logo = "Logo Tamtara sin nombre.png"
    ruta_logo = os.path.join(directorio_actual, nombre_logo)

    # --- Aplicación de Estilo CSS para el Logo de Fondo ---
    if os.path.exists(ruta_logo):
        bin_str = get_base64(ruta_logo)
        css_fondo = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-repeat: no-repeat;
            background-position: center;
            background-size: 400px; /* Ajusta este tamaño según prefieras */
            background-attachment: fixed;
        }}
        
        /* Ajuste del formulario para que sea legible sobre el fondo */
        .stForm {{
            background-color: rgba(249, 251, 252, 0.95) !important;
            border: 1px solid #8CC0D8 !important;
            border-radius: 15px;
            padding: 30px;
        }}
        </style>
        """
        st.markdown(css_fondo, unsafe_allow_html=True)

    # --- Interfaz Visual ---
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.write("") # Espaciado superior
        st.write("")
        
        with st.form("form_login", clear_on_submit=False):
            # Título principal
            st.markdown("<h2 style='text-align: center; color: #4A4E5A;'>Bienvenido a la App del SGI</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #8CC0D8;'>Gestión de Calidad, SST y Medio Ambiente</p>", unsafe_allow_html=True)
            
            email = st.text_input("Correo Electrónico", placeholder="usuario@empresa.com")
            password = st.text_input("Contraseña", type="password")
            btn_entrar = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if btn_entrar:
                if email and password:
                    user_data = obtener_usuario(email)
                    
                    if user_data and user_data['password_hash'] == password:
                        empresa = user_data.get('empresas')
                        
                        if empresa:
                            fecha_ven = datetime.strptime(empresa['fecha_vencimiento'], '%Y-%m-%d').date()
                            hoy = datetime.now().date()
                            
                            if hoy > fecha_ven or empresa['estado'] == 'Mora':
                                st.error("🚨 Acceso suspendido por vencimiento. Contacte a TAMTARA.")
                            else:
                                st.session_state.autenticado = True
                                st.session_state.usuario = user_data['nombre_completo']
                                st.session_state.rol = user_data['rol']
                                st.session_state.empresa_id = user_data['empresa_id']
                                st.session_state.nombre_empresa = empresa['nombre']
                                st.session_state.logo_empresa = empresa['logo_url']
                                
                                st.success(f"Bienvenido(a), {user_data['nombre_completo']}")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("Error: Empresa no vinculada.")
                    else:
                        st.error("Credenciales incorrectas.")
                else:
                    st.warning("Por favor, complete los campos.")

        st.markdown("<p style='text-align: center; color: #4A4E5A; font-size: 0.8rem; margin-top: 20px;'>© 2026 TAMTARA - Soluciones en Sistemas de Gestión</p>", unsafe_allow_html=True)
