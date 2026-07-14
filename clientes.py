import streamlit as st
from database import supabase

def obtener_todos_los_clientes():
    """Trae la lista de empresas que no son administradoras (clientes)."""
    try:
        res = supabase.table("empresas").select("*").eq("es_administradora", False).execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener clientes: {e}")
        return []

def obtener_usuarios_por_empresa(empresa_id):
    """Obtiene todos los usuarios pertenecientes a una empresa específica."""
    try:
        res = supabase.table("usuarios").select("*").eq("empresa_id", empresa_id).execute()
        return res.data
    except Exception as e:
        st.error(f"Error al obtener usuarios: {e}")
        return []

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
        # 1. Eliminar licencias existentes de este cliente
        supabase.table("licencias_empresa").delete().eq("empresa_id", empresa_id).execute()
        
        # 2. Insertar las nuevas licencias seleccionadas
        if llaves_seleccionadas:
            data_to_insert = [{"empresa_id": empresa_id, "modulo_llave": llave} for llave in llaves_seleccionadas]
            supabase.table("licencias_empresa").insert(data_to_insert).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar licencias: {e}")
        return False

def actualizar_rol_usuario(usuario_id, nuevo_rol):
    """Actualiza el rol de un usuario en la base de datos."""
    try:
        supabase.table("usuarios").update({"rol": nuevo_rol}).eq("id", usuario_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar rol: {e}")
        return False


def mostrar_modulo_clientes():
    # Inicializar el estado de navegación dentro del módulo de clientes si no existe
    if "cliente_seleccionado" not in st.session_state:
        st.session_state.cliente_seleccionado = None

    # =========================================================================
    # PANEL B: DETALLE Y GESTIÓN DE ACCESOS DE UN CLIENTE SELECCIONADO
    # =========================================================================
    if st.session_state.cliente_seleccionado is not None:
        cliente = st.session_state.cliente_seleccionado
        
        # Botón de retorno para regresar al Panel A
        if st.button("⬅️ Volver a la lista de Clientes"):
            st.session_state.cliente_seleccionado = None
            st.rerun()
            
        st.subheader(f"⚙️ Panel de Control de Accesos: {cliente['nombre']}")
        st.write(f"ID del Cliente: `{cliente['id']}` | Estado de Cuenta: **{cliente['estado']}**")
        st.write("---")
        
        col_licencias, col_usuarios = st.columns([1, 1])
        
        # --- Columna Izquierda: Activar / Desactivar Submódulos ---
        with col_licencias:
            st.markdown("### 🔌 Módulos y Submódulos Activos")
            st.write("Selecciona los componentes a los que esta empresa tendrá acceso en su plataforma:")
            
            # Obtener catálogo de base de datos
            cat_modulos = obtener_modulos_sistema()
            licencias_actuales = obtener_licencias_cliente(cliente['id'])
            
            # Agrupar los submódulos por su módulo padre para una visualización ordenada
            modulos_agrupados = {}
            for m in cat_modulos:
                padre = m['nombre_modulo']
                if padre not in modulos_agrupados:
                    modulos_agrupados[padre] = []
                modulos_agrupados[padre].append(m)
            
            # Formulario para registrar las selecciones
            with st.form("form_licencias"):
                nuevas_licencias = []
                
                # Renderizar un expansor por módulo principal
                for modulo_padre, subm_list in modulos_agrupados.items():
                    with st.expander(f"📦 {modulo_padre}", expanded=True):
                        for subm in subm_list:
                            # Verificar si ya está activo para el cliente
                            esta_activo = subm['llave_tecnica'] in licencias_actuales
                            
                            # Checkbox individual por submódulo
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
                        st.success("¡Licencias actualizadas con éxito en la base de datos!")
                        time.sleep(1)
                        st.rerun()

        # --- Columna Derecha: Gestión de Usuarios y Roles del Cliente ---
        with col_usuarios:
            st.markdown("### 👥 Usuarios de la Empresa")
            st.write("Administra los niveles de acceso de cada colaborador del cliente:")
            
            usuarios = obtener_usuarios_por_empresa(cliente['id'])
            
            if not usuarios:
                st.warning("Este cliente aún no tiene usuarios registrados.")
            else:
                roles_disponibles = ["Administrador", "Operador", "Visualizador"]
                
                for usr in usuarios:
                    with st.container(border=True):
                        st.markdown(f"**👤 {usr['nombre_completo']}**")
                        st.text(f"Correo: {usr['email']}")
                        
                        # Determinar índice del rol actual
                        rol_actual = usr['rol']
                        default_idx = roles_disponibles.index(rol_actual) if rol_actual in roles_disponibles else 1
                        
                        # Selectbox para cambiar el rol del usuario
                        nuevo_rol = st.selectbox(
                            "Rol asignado:",
                            options=roles_disponibles,
                            index=default_idx,
                            key=f"sel_rol_{usr['id']}"
                        )
                        
                        # Si el rol seleccionado es diferente al actual, mostrar botón de actualizar
                        if nuevo_rol != rol_actual:
                            if st.button("💾 Actualizar Rol", key=f"btn_rol_{usr['id']}", use_container_width=True):
                                if actualizar_rol_usuario(usr['id'], nuevo_rol):
                                    st.success(f"Rol de {usr['nombre_completo']} actualizado a '{nuevo_rol}'")
                                    time.sleep(1)
                                    st.rerun()

    # =========================================================================
    # PANEL A: LISTADO GENERAL DE CLIENTES
    # =========================================================================
    else:
        st.subheader("Lista de Clientes de TAMTARA")
        st.write("A continuación, se listan todas las empresas registradas bajo tu plataforma. Haz clic en **Gestionar Accesos** para activar componentes o cambiar roles de usuarios.")
        st.write("---")
        
        clientes = obtener_todos_los_clientes()
        
        if not clientes:
            st.info("Aún no tienes clientes registrados en la plataforma.")
        else:
            # Cabeceras de tabla personalizadas para Streamlit
            cols_cabecera = st.columns([1, 3, 2, 2, 2])
            with cols_cabecera[0]: st.markdown("**ID**")
            with cols_cabecera[1]: st.markdown("**Empresa**")
            with cols_cabecera[2]: st.markdown("**Vencimiento**")
            with cols_cabecera[3]: st.markdown("**Estado**")
            with cols_cabecera[4]: st.markdown("**Acción**")
            st.write("---")
            
            # Listar cada cliente con su correspondiente botón de acción
            for cli in clientes:
                cols_fila = st.columns([1, 3, 2, 2, 2])
                with cols_fila[0]:
                    st.write(cli['id'])
                with cols_fila[1]:
                    st.markdown(f"**{cli['nombre']}**")
                with cols_fila[2]:
                    st.write(cli['fecha_vencimiento'])
                with cols_fila[3]:
                    # Mostrar badge de color según estado
                    if cli['estado'] == 'Activo':
                        st.success("Activo")
                    else:
                        st.error("Mora")
                        
                with cols_fila[4]:
                    # Al hacer clic, guardamos la empresa en sesión y redibujamos la pantalla
                    if st.button("🔍 Gestionar Accesos", key=f"btn_manage_{cli['id']}", use_container_width=True):
                        st.session_state.cliente_seleccionado = cli
                        st.rerun()
