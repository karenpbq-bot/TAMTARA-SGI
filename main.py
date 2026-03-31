import streamlit as st
from login import mostrar_login

# Configuración visual (Paleta Suave)
st.set_page_config(page_title="App del SGI", page_icon="🌐", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    mostrar_login()
else:
    # Aquí irá el menú lateral con los colores celestes y verdes
    st.sidebar.image(st.session_state.logo_empresa if st.session_state.logo_empresa else "Logo Tamtara sin nombre.png", width=100)
    st.sidebar.title(f"SGI {st.session_state.nombre_empresa}")
    
    # Lógica de módulos según suscripción...
    st.write(f"Hola {st.session_state.usuario}, has ingresado correctamente.")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
