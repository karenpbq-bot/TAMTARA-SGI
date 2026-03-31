import streamlit as st
import time
from datetime import datetime
from database import obtener_usuario  # Aquí sí es correcto importar desde database

def mostrar_login():
    # Centrar el contenido visualmente
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 1. Logo de TAMTARA (Proveedor)
        st.image("Logo Tamtara sin nombre.png", width=150)
        
        # 2. Título Institucional
        st.subheader("🌐 Bienvenido a la App del SGI")
        st.caption("Plataforma de Gestión Integrada: Calidad, SST y Medio Ambiente")
        
        # 3. Formulario de Acceso
        with st.form("form_login", clear_on_submit=False):
            email = st.text_input("Correo Electrónico", placeholder="usuario@empresa.com")
            password = st.text_input("Contraseña", type="password")
            btn_entrar = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if btn_entrar:
                if email and password:
                    user_data = obtener_usuario(email)
                    
                    # Verificación de credenciales
                    if user_data and user_data['password_hash'] == password:
                        empresa = user_data.get('empresas')
                        
                        if empresa:
                            # Validación de Suscripción (Seguridad Financiera)
                            fecha_ven = datetime.strptime(empresa['fecha_vencimiento'], '%Y-%m-%d').date()
                            hoy = datetime.now().date()
                            
                            if hoy > fecha_ven or empresa['estado'] == 'Mora':
                                st.error("🚨 Acceso suspendido por vencimiento de suscripción. Contacte a su consultor TAMTARA.")
                            else:
                                # Guardar variables de sesión globales
                                st.session_state.autenticado = True
                                st.session_state.usuario = user_data['nombre_completo']
                                st.session_state.rol = user_data['rol']
                                st.session_state.empresa_id = user_data['empresa_id']
                                st.session_state.nombre_empresa = empresa['nombre']
                                st.session_state.logo_empresa = empresa['logo_url']
                                
                                st.success(f"Acceso concedido. Bienvenido(a) {user_data['nombre_completo']}")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("Error crítico: El usuario no tiene una empresa vinculada.")
                    else:
                        st.error("Correo o contraseña incorrectos.")
                else:
                    st.warning("Por favor, ingrese sus credenciales completas.")

        st.markdown("---")
        st.caption("© 2026 TAMTARA - Soluciones en Sistemas de Gestión")
