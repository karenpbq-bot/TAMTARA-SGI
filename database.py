import streamlit as st
import time
from database import obtener_usuario  # Importamos la función que creamos antes

def mostrar_login():
    # Centrar el contenido
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 1. Tu Logo de TAMTARA (Como proveedor de confianza)
        st.image("Logo Tamtara sin nombre.png", width=120)
        
        # 2. Título Institucional (Sin mencionar TAMTARA en el saludo)
        st.subheader("🌐 Bienvenido a la App del SGI")
        st.caption("Gestión Integrada de Calidad, SST y Medio Ambiente")
        
        with st.form("form_login", clear_on_submit=False):
            email = st.text_input("Correo Electrónico", placeholder="ejemplo@empresa.com")
            password = st.text_input("Contraseña", type="password")
            btn_entrar = st.form_submit_button("Ingresar al Sistema", use_container_width=True)
            
            if btn_entrar:
                if email and password:
                    # Buscamos al usuario en Supabase
                    user_data = obtener_usuario(email)
                    
                    if user_data and user_data['password_hash'] == password: # Nota: Luego usaremos hashing real
                        # --- VALIDACIÓN DE SEGURIDAD Y PAGOS ---
                        empresa = user_data.get('empresas')
                        
                        if empresa:
                            from datetime import datetime
                            fecha_ven = datetime.strptime(empresa['fecha_vencimiento'], '%Y-%m-%d').date()
                            hoy = datetime.now().date()
                            
                            if hoy > fecha_ven or empresa['estado'] == 'Mora':
                                st.error("🚨 El acceso ha sido suspendido por vencimiento de suscripción. Contacte a su consultor TAMTARA.")
                            else:
                                # Guardamos los datos en la sesión
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
                        st.error("Credenciales incorrectas. Verifique su correo o contraseña.")
                else:
                    st.warning("Por favor, complete todos los campos.")

        st.markdown("---")
        st.caption("© 2026 TAMTARA - Soluciones en Sistemas de Gestión")
