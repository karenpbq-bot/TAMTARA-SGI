import streamlit as st
import time
import os  # Para manejar rutas de archivos de forma segura
from datetime import datetime
from database import obtener_usuario  # Importamos la función de conexión

def mostrar_login():
    # --- Lógica para localizar el logo correctamente ---
    directorio_actual = os.path.dirname(__file__)
    # Usamos la imagen geométrica como el fondo de login
    nombre_logo_fondo = "image_4.png" # Nombre exacto del archivo geométrico
    ruta_logo_fondo = os.path.join(directorio_actual, nombre_logo_fondo)
    
    # También traemos el logo con nombre para mostrarlo dentro del formulario
    nombre_logo_nombre = "Logo Tamtara sin nombre.png"
    ruta_logo_nombre = os.path.join(directorio_actual, nombre_logo_nombre)

    # --- CSS AVANZADO: Fondo Geométrico ---
    # Este bloque de CSS posiciona la imagen geométrica detrás del formulario
    css_fondo = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{st.image_to_base64(ruta_logo_fondo)}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
    }}
    /* Aseguramos que el formulario sea visible sobre el fondo */
    .stForm {{
        background-color: rgba(249, 251, 252, 0.9); # Fondo nube con opacidad
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(74, 78, 90, 0.1); # Gris pizarra suave
    }}
    </style>
    """
    st.markdown(css_fondo, unsafe_allow_html=True)

    # Centrar el contenido visualmente en la pantalla
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # El formulario ahora tiene el fondo geométrico detrás
        with st.form("form_login", clear_on_submit=False):
            # Mostramos el logo con nombre dentro del formulario
            try:
                st.image(ruta_logo_nombre, width=120)
            except Exception:
                pass
                
            st.subheader("Bienvenido a la App del SGI")
            st.caption("Plataforma Integrada de Gestión: Calidad, SST y Medio Ambiente")
            
            st.write("Ingrese sus credenciales para acceder:")
            email = st.text_input("Correo Electrónico", placeholder="usuario@empresa.com")
            password = st.text_input("Contraseña", type="password")
            btn_entrar = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if btn_entrar:
                if email and password:
                    # Llamada a la base de datos de Supabase
                    user_data = obtener_usuario(email)
                    
                    # Verificación de credenciales (Comparación directa temporal)
                    if user_data and user_data['password_hash'] == password:
                        # Obtenemos los datos de la empresa vinculada
                        empresa = user_data.get('empresas')
                        
                        if empresa:
                            # --- VALIDACIÓN DE SEGURIDAD Y PAGOS (Suscripción) ---
                            fecha_ven = datetime.strptime(empresa['fecha_vencimiento'], '%Y-%m-%d').date()
                            hoy = datetime.now().date()
                            
                            if hoy > fecha_ven or empresa['estado'] == 'Mora':
                                st.error("🚨 Acceso suspendido por vencimiento. Contacte a su consultor TAMTARA.")
                            else:
                                # --- LOGIN EXITOSO ---
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
                            st.error("Error crítico: El usuario no tiene una empresa vinculada.")
                    else:
                        st.error("Credenciales incorrectas.")
                else:
                    st.warning("Por favor, complete ambos campos.")

        st.markdown("---")
        st.caption("© 2026 TAMTARA - Soluciones Digitales")
