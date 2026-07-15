import streamlit as st
import time
from database import supabase

# =========================================================================
# 1. FUNCIONES DE BASE DE DATOS (PROCESOS CRUD DE SUPABASE)
# =========================================================================

def obtener_todos_los_clientes():
    """Trae la lista de empresas que no son administradoras (clientes)."""
    try:
        res = supabase.table("empresas").select("*").eq("es_administradora", False).order("nombre").execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener clientes: {e}")
        return []

def crear_cliente_db(nombre, fecha_ven, estado):
    """Inserta una nueva empresa en la base de datos y retorna su registro."""
    try:
        data = {
            "nombre": nombre,
            "fecha_vencimiento": str(fecha_ven),
            "estado": estado,
            "es_administradora": False
        }
        res = supabase.table("empresas").insert(data).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Error al registrar la empresa: {e}")
        return None

def actualizar_cliente_db(empresa_id, nombre, fecha_ven, estado):
    """Actualiza los datos básicos de una empresa cliente."""
    try:
        data = {
            "nombre": nombre,
            "fecha_vencimiento": str(fecha_ven),
            "estado": estado
        }
        supabase.table("empresas").update(data).eq("id", empresa_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la empresa: {e}")
        return False

def eliminar_cliente_db(empresa_id):
    """Elimina permanentemente una empresa de la base de datos (y cascada de usuarios/licencias)."""
    try:
        supabase.table("empresas").delete().eq("id", empresa_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al eliminar la empresa: {e}")
        return False

# --- GESTIÓN DE USUARIOS DE CLIENTES ---

def obtener_usuarios_por_empresa(empresa_id):
    """Obtiene todos los usuarios pertenecientes a una empresa específica."""
    try:
        res = supabase.table("usuarios").select("*").eq("empresa_id", empresa_id).order("nombre_completo").execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener usuarios: {e}")
        return []

def crear_usuario_db(email, password, nombre, rol, empresa_id):
    """Crea un nuevo colaborador para una empresa cliente."""
    try:
        # Verificar si el correo ya existe de forma insensible a mayúsculas/minúsculas
        check_usr = supabase.table("usuarios").select("id").ilike("email", email.strip()).execute()
        if check_usr.data:
            st.error("❌ Error: Ya existe un usuario registrado con este correo electrónico.")
            return False
            
        data = {
            "email": email.strip().lower(),
            "password_hash": password,  # Contraseña almacenada de forma directa
            "nombre_completo": nombre,
            "rol": rol,
            "empresa_id": empresa_id
        }
        supabase.table("usuarios").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error al crear el usuario: {e}")
        return False

def actualizar_usuario_db(usuario_id, email, nombre, rol, password=None):
    """Actualiza la información de un usuario y opcionalmente su contraseña."""
    try:
        data = {
            "email": email.strip().lower(),
            "nombre_completo": nombre,
            "rol": rol
        }
        # Solo actualizamos la contraseña si se digitó un valor nuevo en el campo
        if password and password.strip() != "":
            data["password_hash"] = password
            
        supabase.table("usuarios").update(data).eq("id", usuario_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar el usuario: {e}")
        return False

def eliminar_usuario_db(usuario_id):
    """Elimina permanentemente un usuario de la base de datos."""
    try:
        supabase.table("usuarios").delete().eq("id", usuario_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al eliminar usuario: {e}")
        return False

# --- MÓDULOS Y LICENCIAS ---

def obtener_modulos_sistema():
    """Obtiene el catálogo completo de submódulos de la plataforma."""
    try:
        res = supabase.table("modulos_sistema").select("*").order("nombre_modulo").execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener catálogo de módulos: {e}")
        return []

def obtener_licencias_cliente(empresa_id):
    """Trae las llaves de los submódulos que el cliente tiene activos."""
    try:
        res = supabase.table("licencias_empresa").select("modulo_llave").eq("empresa_id", empresa_id).execute()
        return [item['modulo_llave'] for item in res.data]
    except Exception as e:
        st.error(f"Error al obtener licencias: {e}")
        return []

def guardar_licencias_cliente(empresa_id, llaves_seleccionadas):
    """Actualiza en Supabase las licencias activas para una empresa."""
    try:
        supabase.table("licencias_empresa").delete().eq("empresa_id", empresa_id).execute()
        if llaves_seleccionadas:
            data_to_insert = [{"empresa_id": empresa_id, "modulo_llave": llave} for llave in llaves_seleccionadas]
            supabase.table("licencias_empresa").insert(data_to_insert).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar licencias: {e}")
        return False


# =========================================================================
# 2. INTERFAZ GRÁFICA (VISTAS DE STREAMLIT)
# =========================================================================

@st.dialog("⚠️ Confirmar Eliminación de Cliente")
def confirmar_eliminacion_cliente(cliente):
    """Muestra una ventana modal flotante para confirmar la eliminación segura de un cliente."""
    st.warning(
        f"Está a punto de eliminar de forma permanente a la empresa **{cliente['nombre']}**."
    )
    st.error(
        "🚨 **¡ATENCIÓN!** Esta acción es irreversible. Se borrarán automáticamente "
        "todos los usuarios registrados bajo esta empresa y se cancelarán todas sus licencias activas."
    )
    st.write("¿Realmente desea proceder con la eliminación?")
    
    col_si, col_no = st.columns(2)
    with col_si:
        if st.button("Sí, Eliminar", use_container_width=True, type="primary", key=f"confirm_yes_{cliente['id']}"):
            with st.spinner("Eliminando cliente y dependencias..."):
                if eliminar_cliente_db(cliente['id']):
                    st.success(f"La empresa '{cliente['nombre']}' ha sido eliminada.")
                    time.sleep(1.5)
                    st.rerun()
    with col_no:
        if st.button("No, Cancelar", use_container_width=True, key=f"confirm_no_{cliente['id']}"):
            st.rerun()


def mostrar_modulo_clientes():
    # Inicialización de estados de navegación persistentes
    if "cliente_seleccionado" not in st.session_state:
        st.session_state.cliente_seleccionado = None
    if "editando_empresa" not in st.session_state:
        st.session_state.editando_empresa = None
    if "editando_usuario" not in st.session_state:
        st.session_state.editando_usuario = None

    # =========================================================================
    # DETALLE DE GESTIÓN (RUTAS SECUNDARIAS)
    # =========================================================================
    
    # RUTA B.1: Gestión de Accesos y Usuarios de un Cliente
    if st.session_state.cliente_seleccionado is not None:
        cliente = st.session_state.cliente_seleccionado
        
        if st.button("⬅️ Volver al Directorio de Clientes"):
            st.session_state.cliente_seleccionado = None
            st.rerun()
            
        st.subheader(f"⚙️ Panel de Control de Accesos: {cliente['nombre']}")
        st.write(f"ID del Cliente: `{cliente['id']}` | Estado: **{cliente['estado']}**")
        st.write("---")
        
        col_licencias, col_usuarios = st.columns([1, 1])
        
        # --- COLUMNA LICENCIAS (ACTIVAR / DESACTIVAR SUBMÓDULOS) ---
        with col_licencias:
            st.markdown("### 🔌 Módulos y Submódulos Activos")
            st.write("Configura los accesos directos para la empresa:")
            
            cat_modulos = obtener_modulos_sistema()
            licencias_actuales = obtener_licencias_cliente(cliente['id'])
            
            modulos_agrupados = {}
            for m in cat_modulos:
                padre = m['nombre_modulo']
                if padre not in modulos_agrupados:
                    modulos_agrupados[padre] = []
                modulos_agrupados[padre].append(m)
            
            with st.form("form_licencias"):
                nuevas_licencias = []
                for modulo_padre, subm_list in modulos_agrupados.items():
                    with st.expander(f"📦 {modulo_padre}", expanded=True):
                        for subm in subm_list:
                            esta_activo = subm['llave_tecnica'] in licencias_actuales
                            seleccionado = st.checkbox(
                                label=subm['nombre_submodulo'],
                                value=esta_activo,
                                key=f"chk_{cliente['id']}_{subm['llave_tecnica']}"
                            )
                            if seleccionado:
                                nuevas_licencias.append(subm['llave_tecnica'])
                
                btn_guardar_lic = st.form_submit_button("💾 Guardar Cambios de Licencia", use_container_width=True)
                if btn_guardar_lic:
                    if guardar_licencias_cliente(cliente['id'], nuevas_licencias):
                        st.success("¡Licencias actualizadas exitosamente!")
                        time.sleep(1)
                        st.rerun()

        # --- COLUMNA GESTIÓN DE USUARIOS DEL CLIENTE ---
        with col_usuarios:
            st.markdown("### 👥 Colaboradores y Usuarios")
            
            # Formulario Colapsable para crear un nuevo usuario directamente aquí
            with st.expander("➕ Registrar Nuevo Usuario para este Cliente", expanded=False):
                with st.form("form_nuevo_usr"):
                    u_nombre = st.text_input("Nombre Completo")
                    u_email = st.text_input("Correo Electrónico (Será su Login)")
                    u_rol = st.selectbox("Rol en el SGI", ["Administrador", "Operador", "Visualizador"])
                    u_pass = st.text_input("Contraseña Inicial", type="password")
                    btn_crear_usr = st.form_submit_button("Crear Colaborador", use_container_width=True)
                    
                    if btn_crear_usr:
                        if u_nombre and u_email and u_pass:
                            if crear_usuario_db(u_email, u_pass, u_nombre, u_rol, cliente['id']):
                                st.success(f"¡Usuario '{u_nombre}' registrado de forma exitosa!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("Complete todos los campos del usuario.")
            
            st.write("---")
            usuarios = obtener_usuarios_por_empresa(cliente['id'])
            
            if not usuarios:
                st.warning("Este cliente no tiene usuarios asociados.")
            else:
                for usr in usuarios:
                    with st.container(border=True):
                        # Si estamos editando este usuario específico
                        if st.session_state.editando_usuario == usr['id']:
                            st.markdown(f"**✏️ Editando Usuario: {usr['nombre_completo']}**")
                            edit_u_nombre = st.text_input("Nombre Completo", value=usr['nombre_completo'], key=f"ed_unom_{usr['id']}")
                            edit_u_email = st.text_input("Correo Electrónico", value=usr['email'], key=f"ed_umail_{usr['id']}")
                            edit_u_rol = st.selectbox("Rol", ["Administrador", "Operador", "Visualizador"], index=["Administrador", "Operador", "Visualizador"].index(usr['rol']), key=f"ed_urol_{usr['id']}")
                            edit_u_pass = st.text_input("Actualizar Contraseña (Opcional)", type="password", placeholder="Dejar vacío para mantener la actual", key=f"ed_upass_{usr['id']}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("Guardar Cambios", key=f"btn_save_u_{usr['id']}", use_container_width=True):
                                    if actualizar_usuario_db(usr['id'], edit_u_email, edit_u_nombre, edit_u_rol, edit_u_pass):
                                        st.success("Cambios guardados.")
                                        st.session_state.editando_usuario = None
                                        time.sleep(1)
                                        st.rerun()
                            with c2:
                                if st.button("Cancelar", key=f"btn_cancel_u_{usr['id']}", use_container_width=True):
                                    st.session_state.editando_usuario = None
                                    st.rerun()
                        else:
                            # Vista normal del usuario en el listado
                            st.markdown(f"**👤 {usr['nombre_completo']}**")
                            st.text(f"Correo: {usr['email']}")
                            st.text(f"Rol Actual: {usr['rol']}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("✏️ Editar Usuario", key=f"btn_edit_u_view_{usr['id']}", use_container_width=True):
                                    st.session_state.editando_usuario = usr['id']
                                    st.rerun()
                            with c2:
                                # Eliminación con doble confirmación implícita
                                if st.button("❌ Eliminar", key=f"btn_del_u_view_{usr['id']}", use_container_width=True, type="primary"):
                                    if eliminar_usuario_db(usr['id']):
                                        st.success("Usuario eliminado.")
                                        time.sleep(1)
                                        st.rerun()
        return

    # RUTA B.2: Edición de Datos de Empresa Cliente
    if st.session_state.editando_empresa is not None:
        cli_edit = st.session_state.editando_empresa
        st.subheader(f"✏️ Modificar Información: {cli_edit['nombre']}")
        
        with st.form("form_edit_emp"):
            nuevo_nombre_emp = st.text_input("Nombre de la Empresa", value=cli_edit['nombre'])
            import datetime
            fecha_v_act = datetime.datetime.strptime(cli_edit['fecha_vencimiento'], "%Y-%m-%d").date() if isinstance(cli_edit['fecha_vencimiento'], str) else cli_edit['fecha_vencimiento']
            nueva_fecha_v = st.date_input("Fecha de Vencimiento", value=fecha_v_act)
            nuevo_estado_emp = st.selectbox("Estado de Cuenta", ["Activo", "Mora"], index=0 if cli_edit['estado'] == 'Activo' else 1)
            
            c1, c2 = st.columns(2)
            with c1:
                btn_save = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
                if btn_save:
                    if actualizar_cliente_db(cli_edit['id'], nuevo_nombre_emp, nueva_fecha_v, nuevo_estado_emp):
                        st.success("¡Datos actualizados!")
                        st.session_state.editando_empresa = None
                        time.sleep(1)
                        st.rerun()
            with c2:
                btn_cancel = st.form_submit_button("Cancelar", use_container_width=True)
                if btn_cancel:
                    st.session_state.editando_empresa = None
                    st.rerun()
        return


    # =========================================================================
    # MENÚ PRINCIPAL (ESTRUCTURA DE PESTAÑAS GENERALES)
    # =========================================================================
    tab_directorio, tab_crear = st.tabs(["👥 Directorio de Clientes", "➕ Crear Cuenta de Cliente"])

    # --- TAB 1: DIRECTORIO DE CLIENTES ---
    with tab_directorio:
        st.subheader("Lista de Clientes Registrados")
        st.write("Visualiza, edita o suspende cuentas empresariales y sus accesos:")
        st.write("---")
        
        clientes = obtener_todos_los_clientes()
        
        if not clientes:
            st.info("No hay cuentas de clientes registradas en la plataforma.")
        else:
            cols_cabecera = st.columns([1, 3, 2, 2, 4])
            with cols_cabecera[0]: st.markdown("**ID**")
            with cols_cabecera[1]: st.markdown("**Empresa**")
            with cols_cabecera[2]: st.markdown("**Vencimiento**")
            with cols_cabecera[3]: st.markdown("**Estado**")
            with cols_cabecera[4]: st.markdown("**Acciones de Control**")
            st.write("---")
            
            for cli in clientes:
                cols_fila = st.columns([1, 3, 2, 2, 4])
                with cols_fila[0]:
                    st.write(cli['id'])
                with cols_fila[1]:
                    st.markdown(f"**{cli['nombre']}**")
                with cols_fila[2]:
                    st.write(cli['fecha_vencimiento'])
                with cols_fila[3]:
                    if cli['estado'] == 'Activo':
                        st.success("Activo")
                    else:
                        st.error("Mora")
                        
                with cols_fila[4]:
                    ca1, ca2, ca3 = st.columns([1.5, 1, 1])
                    with ca1:
                        if st.button("🔑 Accesos", key=f"btn_acc_{cli['id']}", use_container_width=True):
                            st.session_state.cliente_seleccionado = cli
                            st.rerun()
                    with ca2:
                        if st.button("✏️", key=f"btn_edit_cli_{cli['id']}", use_container_width=True, help="Editar Empresa"):
                            st.session_state.editando_empresa = cli
                            st.rerun()
                    with ca3:
                        if st.button("❌", key=f"btn_del_cli_{cli['id']}", use_container_width=True, type="primary", help="Eliminar Empresa"):
                            confirmar_eliminacion_cliente(cli)

    # --- TAB 2: CREAR CUENTA DE CLIENTE (SEPARADO Y FLEXIBLE) ---
    with tab_crear:
        st.subheader("Asistente de Registro")
        st.write("Registra nuevas empresas clientes y gestiona la creación de sus usuarios de forma independiente:")
        st.write("---")
        
        # ==========================================
        # PARTE 1: CREACIÓN EXCLUSIVA DE LA EMPRESA
        # ==========================================
        st.markdown("### 🏢 1. Registrar Nueva Empresa Cliente")
        
        col_e1, col_e2, col_e3 = st.columns([2, 1, 1])
        with col_e1:
            new_emp_nombre = st.text_input("Nombre de la Empresa o Razón Social", placeholder="Ej. La Exacta", key="txt_new_emp_nom")
        with col_e2:
            import datetime
            new_emp_vencimiento = st.date_input("Vencimiento del Servicio", value=datetime.date.today() + datetime.timedelta(days=365), key="date_new_emp_ven")
        with col_e3:
            new_emp_estado = st.selectbox("Estado Inicial", ["Activo", "Mora"], key="sel_new_emp_est")
            
        btn_crear_solo_empresa = st.button("💾 Registrar Empresa", use_container_width=True, type="primary", key="btn_crear_solo_empresa")
        
        if btn_crear_solo_empresa:
            nombre_emp_limpio = new_emp_nombre.strip() if new_emp_nombre else ""
            if nombre_emp_limpio:
                with st.spinner("Registrando empresa..."):
                    empresa_creada = crear_cliente_db(nombre_emp_limpio, new_emp_vencimiento, new_emp_estado)
                    if empresa_creada:
                        st.success(f"🎉 Empresa '{nombre_emp_limpio}' registrada con éxito. Ya aparece en el Directorio.")
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("⚠️ Debe ingresar el nombre de la empresa para poder registrarla.")

        st.write("---")
        
        # ==========================================
        # PARTE 2: CREACIÓN DE USUARIOS INDEPENDIENTES
        # ==========================================
        st.markdown("### 👤 2. Registrar Usuarios y Colaboradores")
        st.write("Selecciona una empresa registrada para añadirle un nuevo usuario (puedes crear múltiples usuarios uno por uno):")
        
        # Obtenemos la lista actualizada de clientes de la base de datos para el selector
        lista_clientes = obtener_todos_los_clientes()
        
        if not lista_clientes:
            st.info("Para registrar usuarios, primero debe tener al menos una empresa registrada en la sección de arriba.")
        else:
            # Creamos un diccionario para mapear el nombre de la empresa con su ID
            dict_empresas = {cli['nombre']: cli['id'] for cli in lista_clientes}
            
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                empresa_seleccionada_nom = st.selectbox("Asociar al Cliente:", options=list(dict_empresas.keys()), key="sel_usr_emp_asoc")
                new_usr_nombre = st.text_input("Nombre Completo del Colaborador", placeholder="Ej. Arturo Díaz", key="txt_new_usr_nom")
                new_usr_rol = st.selectbox("Rol asignado en el SGI", ["Administrador", "Operador", "Visualizador"], key="sel_new_usr_rol")
            with col_u2:
                new_usr_email = st.text_input("Correo de Acceso (Email)", placeholder="ejemplo@gmail.com", key="txt_new_usr_mail")
                new_usr_pass = st.text_input("Contraseña de Acceso", type="password", placeholder="Contraseña inicial", key="txt_new_usr_pass")
                
            st.write("")
            btn_crear_usuario_suelto = st.button("➕ Registrar y Vincular Usuario", use_container_width=True, key="btn_crear_usuario_suelto")
            
            if btn_crear_usuario_suelto:
                nombre_usr_limpio = new_usr_nombre.strip() if new_usr_nombre else ""
                email_usr_limpio = new_usr_email.strip() if new_usr_email else ""
                pass_usr_limpio = new_usr_pass.strip() if new_usr_pass else ""
                emp_id_asociado = dict_empresas[empresa_seleccionada_nom]
                
                if nombre_usr_limpio and email_usr_limpio and pass_usr_limpio:
                    with st.spinner("Registrando usuario colaborador..."):
                        exito_usuario = crear_usuario_db(
                            email=email_usr_limpio,
                            password=pass_usr_limpio,
                            nombre=nombre_usr_limpio,
                            rol=new_usr_rol,
                            empresa_id=emp_id_asociado
                        )
                        if exito_usuario:
                            st.success(f"🎉 Usuario '{nombre_usr_limpio}' registrado exitosamente para la empresa '{empresa_seleccionada_nom}'.")
                            time.sleep(1.5)
                            st.rerun()
                else:
                    st.warning("⚠️ Todos los campos de la sección de usuario son obligatorios.")
