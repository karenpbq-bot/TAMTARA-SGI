import streamlit as st
import time
import datetime
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

def crear_cliente_db(nombre, fecha_ven, estado, ruc=None, nom_con=None, nro_con=None, mail_con=None):
    """Inserta una nueva empresa en la base de datos."""
    try:
        data = {
            "nombre": nombre,
            "fecha_vencimiento": str(fecha_ven),
            "estado": estado,
            "es_administradora": False,
            "ruc": ruc.strip() if ruc and ruc.strip() != "" else None,
            "nombre_contacto": nom_con.strip() if nom_con and nom_con.strip() != "" else None,
            "nro_contacto": nro_con.strip() if nro_con and nro_con.strip() != "" else None,
            "correo_contacto": mail_con.strip().lower() if mail_con and mail_con.strip() != "" else None
        }
        res = supabase.table("empresas").insert(data).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Error al registrar la empresa: {e}")
        return None

def actualizar_cliente_db(empresa_id, nombre, fecha_ven, estado, ruc=None, nom_con=None, nro_con=None, mail_con=None):
    """Actualiza los datos de una empresa cliente."""
    try:
        data = {
            "nombre": nombre,
            "fecha_vencimiento": str(fecha_ven),
            "estado": estado,
            "ruc": ruc.strip() if ruc and ruc.strip() != "" else None,
            "nombre_contacto": nom_con.strip() if nom_con and nom_con.strip() != "" else None,
            "nro_contacto": nro_con.strip() if nro_con and nro_con.strip() != "" else None,
            "correo_contacto": mail_con.strip().lower() if mail_con and mail_con.strip() != "" else None
        }
        supabase.table("empresas").update(data).eq("id", empresa_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar la empresa: {e}")
        return False

def eliminar_cliente_db(empresa_id):
    """Elimina permanentemente una empresa de la base de datos (con cascada)."""
    try:
        supabase.table("empresas").delete().eq("id", empresa_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al eliminar la empresa: {e}")
        return False


# --- GESTIÓN DE PERFILES Y PERMISOS POR EMPRESA ---

def obtener_perfiles_por_empresa(empresa_id):
    """Obtiene el catálogo de perfiles personalizados de una empresa."""
    try:
        res = supabase.table("perfiles_empresa").select("*").eq("empresa_id", empresa_id).order("nombre_perfil").execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener perfiles: {e}")
        return []

def crear_perfil_db(empresa_id, nombre_perfil, descripcion=""):
    """Crea un nuevo perfil de acceso para la empresa."""
    try:
        data = {
            "empresa_id": empresa_id,
            "nombre_perfil": nombre_perfil.strip(),
            "descripcion": descripcion.strip() if descripcion else None
        }
        res = supabase.table("perfiles_empresa").insert(data).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Error al crear el perfil: {e}")
        return None

def eliminar_perfil_db(perfil_id):
    """Elimina un perfil de acceso."""
    try:
        supabase.table("perfiles_empresa").delete().eq("id", perfil_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al eliminar perfil: {e}")
        return False

def obtener_permisos_por_perfil(perfil_id):
    """Obtiene las llaves técnicas de submódulos asociadas a un perfil."""
    try:
        res = supabase.table("permisos_perfil").select("submodulo_llave").eq("perfil_id", perfil_id).execute()
        return [item['submodulo_llave'] for item in res.data]
    except Exception as e:
        st.error(f"Error al obtener permisos: {e}")
        return []

def guardar_permisos_perfil(perfil_id, llaves_seleccionadas):
    """Guarda y sincroniza los submódulos autorizados para un perfil."""
    try:
        supabase.table("permisos_perfil").delete().eq("perfil_id", perfil_id).execute()
        if llaves_seleccionadas:
            data_to_insert = [{"perfil_id": perfil_id, "submodulo_llave": llave} for llave in llaves_seleccionadas]
            supabase.table("permisos_perfil").insert(data_to_insert).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar permisos del perfil: {e}")
        return False


# --- GESTIÓN DE USUARIOS VINCULADOS A PERFILES ---

def obtener_usuarios_por_empresa(empresa_id):
    """Obtiene los usuarios de una empresa con el detalle de su perfil."""
    try:
        res = supabase.table("usuarios").select("*, perfiles_empresa(nombre_perfil)").eq("empresa_id", empresa_id).order("nombre_completo").execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener usuarios: {e}")
        return []

def crear_usuario_db(email, password, nombre, perfil_id, empresa_id):
    """Crea un usuario vinculándolo a un perfil específico de la empresa."""
    try:
        check_usr = supabase.table("usuarios").select("id").ilike("email", email.strip()).execute()
        if check_usr.data:
            st.error("❌ Error: Ya existe un usuario registrado con este correo.")
            return False
            
        data = {
            "email": email.strip().lower(),
            "password_hash": password,
            "nombre_completo": nombre,
            "empresa_id": empresa_id,
            "perfil_id": perfil_id,
            "rol": "Operador"
        }
        supabase.table("usuarios").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error al crear el usuario: {e}")
        return False

def actualizar_usuario_db(usuario_id, email, nombre, perfil_id, password=None):
    """Actualiza los datos del usuario y su perfil asociado."""
    try:
        data = {
            "email": email.strip().lower(),
            "nombre_completo": nombre,
            "perfil_id": perfil_id
        }
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


# --- LICENCIAS GLOBALES (MÓDULOS DEL SGI DISPONIBLES PARA LA EMPRESA) ---

def obtener_modulos_sistema():
    """Obtiene el catálogo completo de submódulos del sistema."""
    try:
        res = supabase.table("modulos_sistema").select("*").order("nombre_modulo").execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener catálogo de módulos: {e}")
        return []

def obtener_licencias_cliente(empresa_id):
    """Trae las llaves de los módulos que el cliente tiene activos globalmente."""
    try:
        res = supabase.table("licencias_empresa").select("modulo_llave").eq("empresa_id", empresa_id).execute()
        return [item['modulo_llave'] for item in res.data]
    except Exception as e:
        st.error(f"Error al obtener licencias: {e}")
        return []

def guardar_licencias_cliente(empresa_id, llaves_seleccionadas):
    """Actualiza las licencias activas globales de la empresa."""
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
    st.warning(f"Está a punto de eliminar permanentemente a **{cliente['nombre']}**.")
    st.error("🚨 Esta acción borrará de forma irreversible usuarios, perfiles, licencias y datos vinculados.")
    col_si, col_no = st.columns(2)
    with col_si:
        if st.button("Sí, Eliminar", use_container_width=True, type="primary", key=f"confirm_yes_{cliente['id']}"):
            if eliminar_cliente_db(cliente['id']):
                st.success(f"Empresa '{cliente['nombre']}' eliminada.")
                time.sleep(1)
                st.rerun()
    with col_no:
        if st.button("No, Cancelar", use_container_width=True, key=f"confirm_no_{cliente['id']}"):
            st.rerun()


def mostrar_modulo_clientes():
    # Inicialización de variables de estado
    if "editando_empresa" not in st.session_state:
        st.session_state.editando_empresa = None
    if "editando_usuario" not in st.session_state:
        st.session_state.editando_usuario = None
    if "perfil_seleccionado_permisos" not in st.session_state:
        st.session_state.perfil_seleccionado_permisos = None
        
    if "id_empresa_recien_creada" not in st.session_state:
        st.session_state.id_empresa_recien_creada = None
    if "nombre_empresa_recien_creada" not in st.session_state:
        st.session_state.nombre_empresa_recien_creada = None

    # =========================================================================
    # RUTA SECUNDARIA: EDICIÓN INTEGRAL DE CLIENTES (VISTA OPTIMIZADA EN 4 TABS)
    # =========================================================================
    if st.session_state.editando_empresa is not None:
        cli_edit = st.session_state.editando_empresa
        
        col_cab_izq, col_cab_der = st.columns([3, 1])
        with col_cab_izq:
            st.subheader(f"✏️ Gestión Integral: {cli_edit['nombre']}")
        with col_cab_der:
            if st.button("⬅️ Volver sin Guardar", use_container_width=True, type="secondary", key="btn_volver_sin_guardar_hdr"):
                st.session_state.editando_empresa = None
                st.session_state.editando_usuario = None
                st.session_state.perfil_seleccionado_permisos = None
                st.rerun()
        st.write("---")
        
        # DEFINICIÓN DE LAS 4 PESTAÑAS (ANCHO COMPLETO)
        tab_datos, tab_licencias, tab_perfiles, tab_usuarios = st.tabs([
            "🏢 1. Datos de Empresa", 
            "🔑 2. Módulos Contratados", 
            "📁 3. Perfiles & Permisos", 
            "👥 4. Usuarios de la Empresa"
        ])
        
        # --- TAB 1: DATOS DE LA EMPRESA ---
        with tab_datos:
            with st.form("form_edit_emp", border=False):
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    nuevo_nombre_emp = st.text_input("Nombre / Razón Social", value=cli_edit['nombre'])
                    nuevo_ruc = st.text_input("RUC", value=cli_edit.get('ruc') or "")
                with col_f2:
                    fecha_v_act = datetime.datetime.strptime(cli_edit['fecha_vencimiento'], "%Y-%m-%d").date() if isinstance(cli_edit['fecha_vencimiento'], str) else cli_edit['fecha_vencimiento']
                    nueva_fecha_v = st.date_input("Fecha de Vencimiento", value=fecha_v_act)
                    nuevo_estado_emp = st.selectbox("Estado de Servicio", ["Activo", "Mora"], index=0 if cli_edit['estado'] == 'Activo' else 1)
                
                st.markdown("**Persona de Contacto Directo**")
                nuevo_nom_con = st.text_input("Nombre Completo de Contacto", value=cli_edit.get('nombre_contacto') or "")
                
                c_tel, c_mail = st.columns(2)
                with c_tel:
                    nuevo_nro_con = st.text_input("Número de Teléfono", value=cli_edit.get('nro_contacto') or "")
                with c_mail:
                    nuevo_mail_con = st.text_input("Correo de Contacto", value=cli_edit.get('correo_contacto') or "")
                
                if st.form_submit_button("💾 Actualizar Información Corporativa", use_container_width=True):
                    if actualizar_cliente_db(cli_edit['id'], nuevo_nombre_emp, nueva_fecha_v, nuevo_estado_emp, nuevo_ruc, nuevo_nom_con, nuevo_nro_con, nuevo_mail_con):
                        cli_edit['nombre'] = nuevo_nombre_emp
                        cli_edit['fecha_vencimiento'] = str(nueva_fecha_v)
                        cli_edit['estado'] = nuevo_estado_emp
                        cli_edit['ruc'] = nuevo_ruc
                        cli_edit['nombre_contacto'] = nuevo_nom_con
                        cli_edit['nro_contacto'] = nuevo_nro_con
                        cli_edit['correo_contacto'] = nuevo_mail_con
                        st.session_state.editando_empresa = cli_edit
                        st.success("Cambios corporativos guardados con éxito.")
                        time.sleep(0.8)
                        st.rerun()
        
        # --- TAB 2: MÓDULOS CONTRATADOS ---
        with tab_licencias:
            cat_modulos = obtener_modulos_sistema()
            licencias_actuales = obtener_licencias_cliente(cli_edit['id'])
            
            modulos_agrupados = {}
            for m in cat_modulos:
                padre = m['nombre_modulo']
                if padre not in modulos_agrupados:
                    modulos_agrupados[padre] = []
                modulos_agrupados[padre].append(m)
            
            with st.form("form_lic_globales", border=False):
                st.write("Configure los módulos de la plataforma a los cuales este cliente tiene derecho de acceso:")
                nuevas_lic_globales = []
                
                # Súper matriz de selección
                for mod_padre, subm_list in modulos_agrupados.items():
                    with st.expander(f"📦 {mod_padre}", expanded=True):
                        cols_sub = st.columns(2)
                        for idx, subm in enumerate(subm_list):
                            with cols_sub[idx % 2]:
                                esta_lic = subm['llave_tecnica'] in licencias_actuales
                                sel = st.checkbox(
                                    label=subm['nombre_submodulo'],
                                    value=esta_lic,
                                    key=f"lic_emp_{cli_edit['id']}_{subm['llave_tecnica']}"
                                )
                                if sel:
                                    nuevas_lic_globales.append(subm['llave_tecnica'])
                                    
                if st.form_submit_button("💾 Actualizar Licencias del SGI", use_container_width=True):
                    if guardar_licencias_cliente(cli_edit['id'], nuevas_lic_globales):
                        st.success("Licencias del SGI actualizadas.")
                        time.sleep(0.8)
                        st.rerun()

        # --- TAB 3: PERFILES & PERMISOS ---
        with tab_perfiles:
            perfiles = obtener_perfiles_por_empresa(cli_edit['id'])
            
            col_cr_p_list, col_cr_p_add = st.columns([1.5, 1])
            
            with col_cr_p_list:
                st.markdown("**Catálogo de Perfiles Disponibles**")
                opciones_perfil = {p['nombre_perfil']: p for p in perfiles}
                
                col_sel, col_del = st.columns([2, 1])
                with col_sel:
                    nombre_perf_seleccionado = st.selectbox(
                        "Perfiles de la empresa:",
                        options=list(opciones_perfil.keys()),
                        index=0 if perfiles else None,
                        label_visibility="collapsed"
                    )
                with col_del:
                    if nombre_perf_seleccionado:
                        perfil_a_borrar = opciones_perfil[nombre_perf_seleccionado]
                        if st.button("❌ Eliminar Perfil", key=f"del_perf_{perfil_a_borrar['id']}", use_container_width=True, type="primary"):
                            if eliminar_perfil_db(perfil_a_borrar['id']):
                                st.success("Perfil eliminado.")
                                time.sleep(0.8)
                                st.rerun()
            
            with col_cr_p_add:
                st.markdown("**Crear Perfil Nuevo**")
                new_perf_nombre = st.text_input("Nombre del Perfil de Acceso", placeholder="Ej. Supervisor de Planta", label_visibility="collapsed", key="add_new_p_name_asist")
                if st.button("➕ Registrar Perfil", use_container_width=True):
                    if new_perf_nombre.strip():
                        if crear_perfil_db(cli_edit['id'], new_perf_nombre):
                            st.success(f"Perfil '{new_perf_nombre}' creado.")
                            time.sleep(0.8)
                            st.rerun()
                    else:
                        st.warning("Escriba un nombre válido.")

            st.write("---")
            
            if nombre_perf_seleccionado:
                perfil_obj = opciones_perfil[nombre_perf_seleccionado]
                st.markdown(f"#### Permisos de Acceso para: `{perfil_obj['nombre_perfil']}`")
                
                # Filtrar solo los módulos activos que tiene permitidos la empresa
                lic_empresa = obtener_licencias_cliente(cli_edit['id'])
                todos_los_submodulos = obtener_modulos_sistema()
                submodulos_permitidos_empresa = [s for s in todos_los_submodulos if s['llave_tecnica'] in lic_empresa]
                
                permisos_actuales_perfil = obtener_permisos_por_perfil(perfil_obj['id'])
                
                if not submodulos_permitidos_empresa:
                    st.info("Debe habilitar módulos contratados para la empresa en la pestaña 'Módulos Contratados' antes de asignar permisos.")
                else:
                    with st.form(f"form_permisos_perf_{perfil_obj['id']}", border=False):
                        nuevos_permisos_perfil = []
                        cols_perm = st.columns(2)
                        for idx, subm in enumerate(submodulos_permitidos_empresa):
                            with cols_perm[idx % 2]:
                                tiene_permiso = subm['llave_tecnica'] in permisos_actuales_perfil
                                check_sub = st.checkbox(
                                    label=f"{subm['nombre_modulo']} ➡️ {subm['nombre_submodulo']}",
                                    value=tiene_permiso,
                                    key=f"perm_{perfil_obj['id']}_{subm['llave_tecnica']}"
                                )
                                if check_sub:
                                    nuevos_permisos_perfil.append(subm['llave_tecnica'])
                                    
                        if st.form_submit_button("💾 Sincronizar Permisos del Perfil", use_container_width=True):
                            if guardar_permisos_perfil(perfil_obj['id'], nuevos_permisos_perfil):
                                st.success("Permisos asignados al perfil con éxito.")
                                time.sleep(0.8)
                                st.rerun()

        # --- TAB 4: USUARIOS DEL CLIENTE (CON BUSCADOR DINÁMICO) ---
        with tab_usuarios:
            perfiles_emp = obtener_perfiles_por_empresa(cli_edit['id'])
            perfiles_dict = {p['nombre_perfil']: p['id'] for p in perfiles_emp}
            
            col_us_b, col_us_a = st.columns([1.5, 1])
            
            # Sub-bloque 4.1: Buscador de usuarios
            with col_us_b:
                st.markdown("**🔍 Filtrar Usuarios por Palabra Clave**")
                busqueda_usuario = st.text_input("Buscar por Nombre, Correo o Perfil:", placeholder="Escriba aquí...", label_visibility="collapsed", key="search_user_edit")
                
            # Sub-bloque 4.2: Agregar un colaborador de forma rápida
            with col_us_a:
                st.markdown("**Nuevo Usuario**")
                with st.expander("➕ Registrar Colaborador", expanded=False):
                    nu_nombre = st.text_input("Nombre Completo", key="add_usr_n")
                    nu_email = st.text_input("Correo de Login", key="add_usr_e")
                    nu_pass = st.text_input("Contraseña Inicial", type="password", key="add_usr_p")
                    nu_perf_nom = st.selectbox("Perfil de Acceso", options=list(perfiles_dict.keys()), key="add_usr_per")
                    
                    if st.button("Guardar Colaborador", use_container_width=True, type="primary"):
                        if nu_nombre and nu_email and nu_pass and nu_perf_nom:
                            p_id = perfiles_dict[nu_perf_nom]
                            if crear_usuario_db(nu_email, nu_pass, nu_nombre, p_id, cli_edit['id']):
                                st.success("Usuario añadido exitosamente.")
                                time.sleep(0.8)
                                st.rerun()
                        else:
                            st.warning("Todos los campos de registro son obligatorios.")
            
            st.write("---")
            
            usuarios = obtener_usuarios_por_empresa(cli_edit['id'])
            
            # Lógica de filtrado en tiempo real
            if busqueda_usuario:
                q = busqueda_usuario.lower().strip()
                usuarios_mostrados = [
                    u for u in usuarios if 
                    q in u['nombre_completo'].lower() or 
                    q in u['email'].lower() or
                    (u.get('perfiles_empresa') and q in u['perfiles_empresa']['nombre_perfil'].lower())
                ]
            else:
                usuarios_mostrados = usuarios
                
            if not usuarios_mostrados:
                st.info("No se encontraron usuarios asignados que coincidan con la búsqueda.")
            else:
                for usr in usuarios_mostrados:
                    with st.container(border=True):
                        if st.session_state.editando_usuario == usr['id']:
                            # Formulario de edición en línea
                            st.markdown(f"**✏️ Editando: {usr['nombre_completo']}**")
                            col_ed_u1, col_ed_u2 = st.columns(2)
                            with col_ed_u1:
                                ed_u_nombre = st.text_input("Nombre Completo", value=usr['nombre_completo'], key=f"e_unom_{usr['id']}")
                                ed_u_email = st.text_input("Correo de Acceso", value=usr['email'], key=f"e_umail_{usr['id']}")
                            with col_ed_u2:
                                ed_u_perf_nom = st.selectbox(
                                    "Perfil de Permisos", 
                                    options=list(perfiles_dict.keys()), 
                                    index=list(perfiles_dict.values()).index(usr['perfil_id']) if usr['perfil_id'] in perfiles_dict.values() else 0,
                                    key=f"e_uperf_{usr['id']}"
                                )
                                ed_u_pass = st.text_input("Modificar Contraseña (Opcional)", type="password", placeholder="Dejar vacío para mantener", key=f"e_upass_{usr['id']}")
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("Guardar Cambios", key=f"b_s_u_{usr['id']}", use_container_width=True, type="primary"):
                                    pid_sel = perfiles_dict[ed_u_perf_nom]
                                    if actualizar_usuario_db(usr['id'], ed_u_email, ed_u_nombre, pid_sel, ed_u_pass):
                                        st.session_state.editando_usuario = None
                                        st.success("Usuario modificado.")
                                        time.sleep(0.8)
                                        st.rerun()
                            with c2:
                                if st.button("Cancelar", key=f"b_c_u_{usr['id']}", use_container_width=True):
                                        st.session_state.editando_usuario = None
                                        st.rerun()
                        else:
                            # Tarjeta compacta del usuario
                            p_nombre = usr.get('perfiles_empresa', {}).get('nombre_perfil') if usr.get('perfiles_empresa') else "Sin Perfil"
                            col_card_info, col_card_acts = st.columns([3, 1])
                            with col_card_info:
                                st.markdown(f"👤 **{usr['nombre_completo']}** — Perfil: `{p_nombre}`")
                                st.text(f"Correo: {usr['email']}")
                            with col_card_acts:
                                ca_u1, ca_u2 = st.columns(2)
                                with ca_u1:
                                    if st.button("✏️", key=f"b_ed_{usr['id']}", use_container_width=True, help="Editar Usuario"):
                                        st.session_state.editando_usuario = usr['id']
                                        st.rerun()
                                with ca_u2:
                                    if st.button("❌", key=f"b_de_{usr['id']}", use_container_width=True, type="primary", help="Eliminar Usuario"):
                                        if eliminar_usuario_db(usr['id']):
                                            st.success("Usuario removido.")
                                            time.sleep(0.8)
                                            st.rerun()
        return


    # =========================================================================
    # MENÚ PRINCIPAL: DIRECTORIO GENERAL & CREACIÓN DE CUENTAS
    # =========================================================================
    tab_directorio, tab_crear = st.tabs(["👥 Directorio de Clientes", "➕ Alta de Nuevo Cliente"])

    # --- TAB 1: DIRECTORIO COMPACTO DE CLIENTES (CON BUSCADOR DINÁMICO) ---
    with tab_directorio:
        clientes = obtener_todos_los_clientes()
        
        if not clientes:
            st.info("No hay cuentas de clientes registradas en la plataforma.")
        else:
            st.markdown("**🔍 Búsqueda Inteligente de Empresas**")
            busqueda_cliente = st.text_input("Filtrar por Nombre, RUC o Contacto:", placeholder="Escriba palabras clave del cliente...", label_visibility="collapsed", key="search_cli_main")
            st.write("")
            
            # Lógica de filtrado en tiempo real
            if busqueda_cliente:
                q_cli = busqueda_cliente.lower().strip()
                clientes_mostrados = [
                    c for c in clientes if 
                    q_cli in c['nombre'].lower() or 
                    (c.get('ruc') and q_cli in c['ruc'].lower()) or
                    (c.get('nombre_contacto') and q_cli in c['nombre_contacto'].lower()) or
                    (c.get('correo_contacto') and q_cli in c['correo_contacto'].lower())
                ]
            else:
                clientes_mostrados = clientes
                
            if not clientes_mostrados:
                st.warning("No se encontraron empresas clientes que coincidan con la búsqueda.")
            else:
                cols_cabecera = st.columns([1, 2.5, 2, 2, 2.5, 2])
                with cols_cabecera[0]: st.markdown("**ID**")
                with cols_cabecera[1]: st.markdown("**Empresa**")
                with cols_cabecera[2]: st.markdown("**RUC**")
                with cols_cabecera[3]: st.markdown("**Vencimiento**")
                with cols_cabecera[4]: st.markdown("**Estado**")
                with cols_cabecera[5]: st.markdown("**Control**")
                st.write("---")
                
                for cli in clientes_mostrados:
                    cols_fila = st.columns([1, 2.5, 2, 2, 2.5, 2])
                    with cols_fila[0]:
                        st.write(cli['id'])
                    with cols_fila[1]:
                        st.markdown(f"**{cli['nombre']}**")
                    with cols_fila[2]:
                        st.write(cli.get('ruc') or "—")
                    with cols_fila[3]:
                        st.write(cli['fecha_vencimiento'])
                    with cols_fila[4]:
                        if cli['estado'] == 'Activo':
                            st.success("Activo")
                        else:
                            st.error("Mora")
                            
                    with cols_fila[5]:
                        ca1, ca2 = st.columns(2)
                        with ca1:
                            if st.button("✏️", key=f"btn_edit_cli_{cli['id']}", use_container_width=True, help="Editar Empresa, Perfiles y Usuarios"):
                                st.session_state.editando_empresa = cli
                                st.rerun()
                        with ca2:
                            if st.button("❌", key=f"btn_del_cli_{cli['id']}", use_container_width=True, type="primary", help="Borrar Cliente"):
                                confirmar_eliminacion_cliente(cli)

    # --- TAB 2: ASISTENTE DE CREACIÓN DE CLIENTES ---
    with tab_crear:
        st.subheader("Asistente de Registro")
        
        # =====================================================================
        # PASO A: CREACIÓN BÁSICA DE LA EMPRESA
        # =====================================================================
        if st.session_state.id_empresa_recien_creada is None:
            st.markdown("#### 🏢 Paso 1: Datos de la Empresa")
            
            col_e1, col_e2 = st.columns([2, 1])
            with col_e1:
                new_emp_nombre = st.text_input("Nombre de la Empresa o Razón Social", placeholder="Ej. Constructora Delta", key="c_emp_nom")
            with col_e2:
                new_emp_ruc = st.text_input("RUC (Opcional)", placeholder="20123456789", key="c_emp_ruc")
                
            col_e3, col_e4 = st.columns(2)
            with col_e3:
                new_emp_vencimiento = st.date_input("Vencimiento del Plan", value=datetime.date.today() + datetime.timedelta(days=365), key="c_emp_ven")
            with col_e4:
                new_emp_estado = st.selectbox("Estado Inicial", ["Activo", "Mora"], key="c_emp_est")
                
            st.markdown("**Persona de Contacto Directo (Opcional)**")
            new_emp_nom_con = st.text_input("Nombre de Contacto", placeholder="Ej. Karen Barrientos", key="c_emp_nom_con")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                new_emp_nro_con = st.text_input("Teléfono/Celular", placeholder="987654321", key="c_emp_nro_con")
            with col_c2:
                new_emp_mail_con = st.text_input("Correo de Contacto", placeholder="karen@delta.com", key="c_emp_mail_con")
                
            st.write("")
            if st.button("💾 Crear Empresa e Ir a Configuración de Roles", use_container_width=True, type="primary"):
                nombre_limpio = new_emp_nombre.strip() if new_emp_nombre else ""
                if nombre_limpio:
                    with st.spinner("Creando empresa..."):
                        empresa_creada = crear_cliente_db(
                            nombre_limpio, 
                            new_emp_vencimiento, 
                            new_emp_estado,
                            new_emp_ruc,
                            new_emp_nom_con,
                            new_emp_nro_con,
                            new_emp_mail_con
                        )
                        if empresa_creada:
                            st.session_state.id_empresa_recien_creada = empresa_creada["id"]
                            st.session_state.nombre_empresa_recien_creada = empresa_creada["nombre"]
                            st.success(f"🎉 Empresa '{nombre_limpio}' registrada con éxito.")
                            time.sleep(1)
                            st.rerun()
                else:
                    st.warning("⚠️ El nombre de la empresa es obligatorio.")
                    
        # =====================================================================
        # PASO B: CREACIÓN ASISTIDA DE PERFILES Y USUARIOS
        # =====================================================================
        else:
            id_emp = st.session_state.id_empresa_recien_creada
            nom_emp = st.session_state.nombre_empresa_recien_creada
            
            st.markdown(f"#### 👤 Paso 2: Configurar Perfiles y Usuarios para **{nom_emp}**")
            
            col_cr_p, col_cr_u = st.columns([1, 1.1])
            
            with col_cr_p:
                st.markdown("**1. Crear Perfiles del Cliente**")
                perfiles_creados = obtener_perfiles_por_empresa(id_emp)
                
                if perfiles_creados:
                    st.write("Perfiles registrados:")
                    for p in perfiles_creados:
                        st.write(f"- 📁 `{p['nombre_perfil']}`")
                else:
                    st.info("Crea al menos un perfil para poder asignar usuarios.")
                
                asist_nombre_perfil = st.text_input("Nombre de Perfil", placeholder="Ej. Administrador Interno", key="asist_p_nom")
                if st.button("➕ Añadir Perfil", use_container_width=True):
                    if asist_nombre_perfil.strip():
                        if crear_perfil_db(id_emp, asist_nombre_perfil):
                            st.success(f"Perfil '{asist_nombre_perfil}' creado.")
                            time.sleep(0.8)
                            st.rerun()
                    else:
                        st.warning("Asigne un nombre al perfil.")
                        
            with col_cr_u:
                st.markdown("**2. Registrar Usuarios**")
                usuarios_creados = obtener_usuarios_por_empresa(id_emp)
                
                if usuarios_creados:
                    st.write("Usuarios creados:")
                    for u in usuarios_creados:
                        p_nom = u.get('perfiles_empresa', {}).get('nombre_perfil') if u.get('perfiles_empresa') else "Sin Perfil"
                        st.write(f"- 👤 {u['nombre_completo']} ({p_nom})")
                
                perfiles_dict_asist = {p['nombre_perfil']: p['id'] for p in perfiles_creados}
                
                u_nom = st.text_input("Nombre del Colaborador", key="asist_u_nom")
                u_mail = st.text_input("Correo", key="asist_u_mail")
                u_pass = st.text_input("Contraseña", type="password", key="asist_u_pass")
                u_perf_nom = st.selectbox("Perfil Asignado", options=list(perfiles_dict_asist.keys()), key="asist_u_perf")
                
                c_b1, c_b2 = st.columns(2)
                with c_b1:
                    if st.button("➕ Guardar y Registrar Otro", use_container_width=True):
                        if u_nom and u_mail and u_pass and u_perf_nom:
                            p_id = perfiles_dict_asist[u_perf_nom]
                            if crear_usuario_db(u_mail, u_pass, u_nom, p_id, id_emp):
                                st.success("Usuario agregado.")
                                time.sleep(0.8)
                                st.rerun()
                        else:
                            st.warning("Complete todos los campos.")
                with c_b2:
                    if st.button("💾 Finalizar Registro", use_container_width=True, type="primary"):
                        if u_nom or u_mail or u_pass:
                            if u_nom and u_mail and u_pass and u_perf_nom:
                                p_id = perfiles_dict_asist[u_perf_nom]
                                crear_usuario_db(u_mail, u_pass, u_nom, p_id, id_emp)
                            else:
                                st.warning("Datos del último usuario incompletos. Se finalizó el asistente sin guardar este registro.")
                                time.sleep(1.5)
                                
                        st.session_state.id_empresa_recien_creada = None
                        st.session_state.nombre_empresa_recien_creada = None
                        st.success("¡Empresa y usuarios creados exitosamente!")
                        time.sleep(1)
                        st.rerun()
            
            st.write("---")
            if st.button("❌ Cerrar Asistente de Creación", use_container_width=True):
                st.session_state.id_empresa_recien_creada = None
                st.session_state.nombre_empresa_recien_creada = None
                st.rerun()
