import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Recetario inteligente",
    page_icon="🍲",
    layout="wide"
)

# --- CARGA DE DATOS (CON CACHÉ PARA MEJOR RENDIMIENTO) ---
@st.cache_data
def load_data():
    """Carga los archivos Excel desde la carpeta 'data' y los devuelve como DataFrames de Pandas."""
    try:
        path_comidas = os.path.join('data', 'comidas.xlsx')
        path_equivalencias = os.path.join('data', 'equivalencias.xlsx')
        comidas_df = pd.read_excel(path_comidas)
        equivalencias_df = pd.read_excel(path_equivalencias)
        return comidas_df, equivalencias_df
    except FileNotFoundError:
        st.error("Error: Asegúrate de que los archivos 'comidas.xlsx' y 'equivalencias.xlsx' se encuentran dentro de una carpeta llamada 'data'.")
        return None, None

comidas, equivalencias = load_data()

# --- NAVEGACIÓN DE PÁGINAS EN LA BARRA LATERAL---
st.sidebar.title("Navegación")
pagina_seleccionada = st.sidebar.radio("Elige una página", ["Planificador de Menús", "Calculadora de Equivalencias", "Histórico de Comidas"])
st.sidebar.markdown("---")


# --- DEFINICIÓN DE LA PÁGINA 1: PLANIFICADOR ---
def pagina_planificador():
    st.title("🍲 Planificador de Comidas Inteligente")
    st.markdown("Esta aplicación te ayuda a planificar tus comidas diarias.")
    st.markdown("---")

    # Si no se pudieron cargar los datos, detenemos la ejecución de esta página
    if comidas is None or equivalencias is None:
        st.stop()

    # --- SELECCIÓN PRINCIPAL DEL MENÚ ---
    col_menu1, col_menu2 = st.columns(2)
    with col_menu1:
        tipo_comida_elegida = st.selectbox(
            "**1. Selecciona el tipo de comida:**",
            options=comidas['Comida'].unique()
        )
    with col_menu2:
        platos_disponibles = comidas[comidas['Comida'] == tipo_comida_elegida]['Plato'].unique()
        plato_elegido = st.selectbox(
            "**2. Selecciona el plato:**",
            options=platos_disponibles
        )
    st.markdown("---")

    # --- LÓGICA PRINCIPAL Y VISUALIZACIÓN ---
    if plato_elegido:
        st.header(f"{plato_elegido}")
        receta_original_df = comidas[comidas['Plato'] == plato_elegido].copy()
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.subheader("📝 Receta Original")
            st.dataframe(receta_original_df[['Ingrediente', 'Cantidad en seco', 'Grupo Ingrediente']], use_container_width=True, hide_index=True)

        menu_final = []
        with col2:
            st.subheader("🔄 Sustituir Ingredientes")
            for i, ingrediente_row in receta_original_df.iterrows():
                clave_eq, ingrediente_original, cantidad_original = ingrediente_row['Clave equivalencia'], ingrediente_row['Ingrediente'], ingrediente_row['Cantidad en seco']
                opciones_sustitucion = equivalencias[equivalencias['Clave equivalencia'] == clave_eq]['Ingrediente'].tolist()
                
                if opciones_sustitucion:
                    # Eliminar el ingrediente original de la lista de opciones
                    if ingrediente_original in opciones_sustitucion:
                        opciones_sustitucion.remove(ingrediente_original)

                    # Añadir la opción de no sustituir ("----")
                    opciones_con_placeholder = ["----"] + opciones_sustitucion
                    
                    ingrediente_seleccionado = st.selectbox(
                        f"Sustituto para **{ingrediente_original}**:", 
                        options=opciones_con_placeholder, 
                        index=0, # Por defecto se selecciona "----"
                        key=f"ingrediente_{i}"
                    )
                    
                    # Comprobar si se ha seleccionado una sustitución
                    if ingrediente_seleccionado == "----":
                        # No hay sustitución, usar los valores originales
                        ingrediente_final = ingrediente_original
                        cantidad_final = cantidad_original
                    else:
                        # Se ha seleccionado un sustituto, calcular la nueva cantidad
                        ingrediente_final = ingrediente_seleccionado
                        
                        equivalencia_original_row = equivalencias[equivalencias['Ingrediente'] == ingrediente_original]
                        equivalencia_nueva_row = equivalencias[equivalencias['Ingrediente'] == ingrediente_seleccionado]
                        
                        if not equivalencia_original_row.empty and not equivalencia_nueva_row.empty:
                            equivalencia_original_val = equivalencia_original_row['Equivalencia'].iloc[0]
                            equivalencia_nueva_val = equivalencia_nueva_row['Equivalencia'].iloc[0]
                            if equivalencia_original_val > 0:
                                cantidad_final = (cantidad_original * equivalencia_nueva_val) / equivalencia_original_val
                            else:
                                cantidad_final = 0
                        else:
                            cantidad_final = cantidad_original
                    
                    menu_final.append({"Ingrediente": ingrediente_final, "Cantidad Calculada (gr)": round(cantidad_final, 2), "Grupo Ingrediente": ingrediente_row['Grupo Ingrediente']})
                else:
                    # No hay opciones de sustitución, añadir el ingrediente original
                    menu_final.append({"Ingrediente": ingrediente_original, "Cantidad Calculada (gr)": cantidad_original, "Grupo Ingrediente": ingrediente_row['Grupo Ingrediente']})
        
        st.markdown("---")
        if menu_final:
            st.header("✅ Tu Menú Final Personalizado")
            menu_final_df = pd.DataFrame(menu_final)
            st.dataframe(menu_final_df, use_container_width=True, hide_index=True)

            # --- FORMULARIO PARA GUARDAR EN HISTÓRICO ---
            with st.form("cooking_form"):
                st.write("#### ¿Listo para cocinar? Guarda esta comida en tu histórico.")
                
                form_cols = st.columns(2)
                with form_cols[0]:
                    fecha_cocina = st.date_input("Fecha de la comida", value=datetime.now())
                with form_cols[1]:
                    hora_cocina = st.time_input("Hora de la comida", value=datetime.now())
                
                submitted = st.form_submit_button("Cocinar y Guardar")

                if submitted:
                    # Preparar los datos para guardar
                    historico_nuevo_df = menu_final_df.copy()
                    historico_nuevo_df['fecha'] = fecha_cocina.strftime('%Y-%m-%d')
                    historico_nuevo_df['hora'] = hora_cocina.strftime('%H:%M:%S')
                    historico_nuevo_df['comida'] = tipo_comida_elegida
                    historico_nuevo_df['plato'] = plato_elegido
                    
                    # Renombrar y seleccionar columnas finales
                    historico_nuevo_df = historico_nuevo_df.rename(columns={
                        "Ingrediente": "ingrediente",
                        "Cantidad Calculada (gr)": "cantidad",
                        "Grupo Ingrediente": "grupo_ingrediente"
                    })
                    columnas_finales = ['fecha', 'hora', 'comida', 'plato', 'ingrediente', 'cantidad', 'grupo_ingrediente']
                    historico_nuevo_df = historico_nuevo_df[columnas_finales]
                    
                    # Guardar en el archivo XLSX en la carpeta 'save'
                    save_dir = 'save'
                    os.makedirs(save_dir, exist_ok=True) # Asegura que el directorio exista
                    path_historico = os.path.join(save_dir, 'historico_comidas.xlsx')

                    try:
                        if os.path.exists(path_historico):
                            # Si el archivo existe, leerlo, añadir las nuevas filas y guardar
                            df_existente = pd.read_excel(path_historico)
                            df_final = pd.concat([df_existente, historico_nuevo_df], ignore_index=True)
                            df_final.to_excel(path_historico, index=False)
                        else:
                            # Si el archivo no existe, crearlo
                            historico_nuevo_df.to_excel(path_historico, index=False)
                            
                        st.success(f"¡Comida guardada con éxito en tu histórico para el {fecha_cocina.strftime('%d/%m/%Y')} a las {hora_cocina.strftime('%H:%M')}!")
                    except Exception as e:
                        st.error(f"Ocurrió un error al guardar el archivo: {e}")


# --- DEFINICIÓN DE LA PÁGINA 2: CALCULADORA DE EQUIVALENCIAS ---
def pagina_equivalencias():
    st.title("⚖️ Calculadora de Equivalencias")
    st.markdown("Usa esta herramienta para calcular rápidamente las equivalencias entre ingredientes.")
    st.markdown("---")

    if equivalencias is None:
        st.stop()

    col1, col2 = st.columns(2, gap="large")

    # --- COLUMNA 1: INGREDIENTE DE ORIGEN ---
    with col1:
        st.subheader("➡️ Ingrediente de Origen")
        grupo_origen = st.selectbox("Grupo Ingrediente", options=sorted(equivalencias['Grupo Ingrediente'].unique()), key="grupo_origen")
        
        df_grupo_origen = equivalencias[equivalencias['Grupo Ingrediente'] == grupo_origen]
        ingrediente_origen = st.selectbox("Ingrediente", options=sorted(df_grupo_origen['Ingrediente'].unique()), key="ingrediente_origen")
        
        default_weight = 100.0
        if ingrediente_origen:
            default_weight_row = equivalencias[equivalencias['Ingrediente'] == ingrediente_origen]
            if not default_weight_row.empty:
                default_weight = float(default_weight_row['Equivalencia'].iloc[0])

        peso_origen = st.number_input("Peso (gr)", value=default_weight, min_value=0.1, step=1.0, key="peso_origen")

    # --- COLUMNA 2: INGREDIENTE DE DESTINO ---
    with col2:
        st.subheader("⬅️ Ingrediente de Destino")
        filtro_subcategoria = st.radio("Filtrar por subcategoría", ["Misma subcategoría", "Todas"], horizontal=True, key="filtro_sub")
        
        df_destino_base = equivalencias[equivalencias['Grupo Ingrediente'] == grupo_origen]
        opciones_destino = pd.DataFrame()

        if filtro_subcategoria == "Misma subcategoría":
            if ingrediente_origen:
                clave_origen_row = equivalencias[equivalencias['Ingrediente'] == ingrediente_origen]
                if not clave_origen_row.empty:
                    clave_origen = clave_origen_row['Clave equivalencia'].iloc[0]
                    opciones_destino = df_destino_base[df_destino_base['Clave equivalencia'] == clave_origen]
        else:
            opciones_destino = df_destino_base
        
        ingrediente_destino = st.selectbox("Ingrediente", options=sorted(opciones_destino['Ingrediente'].unique()), key="ingrediente_destino")

    # --- CÁLCULO Y RESULTADO ---
    if ingrediente_origen and ingrediente_destino and peso_origen:
        st.markdown("---")
        st.header("Resultado del Cálculo")
        
        equivalencia_origen_row = equivalencias[equivalencias['Ingrediente'] == ingrediente_origen]
        equivalencia_destino_row = equivalencias[equivalencias['Ingrediente'] == ingrediente_destino]

        if not equivalencia_origen_row.empty and not equivalencia_destino_row.empty:
            val_origen = equivalencia_origen_row['Equivalencia'].iloc[0]
            val_destino = equivalencia_destino_row['Equivalencia'].iloc[0]

            if val_origen > 0:
                cantidad_calculada = (peso_origen * val_destino) / val_origen
                st.success(f"**{peso_origen} gr** de **{ingrediente_origen}** equivalen a **{cantidad_calculada:.2f} gr** de **{ingrediente_destino}**.")
            else:
                st.warning("El ingrediente de origen tiene una equivalencia de 0 y no se puede calcular.")
        else:
            st.error("No se pudo encontrar uno de los ingredientes en la tabla de equivalencias.")

# --- DEFINICIÓN DE LA PÁGINA 3: HISTÓRICO ---
def pagina_historico():
    st.title("📖 Histórico de Comidas")
    st.markdown("Aquí puedes ver, filtrar y editar todas las comidas que has guardado.")
    
    save_dir = 'save'
    path_historico = os.path.join(save_dir, 'historico_comidas.xlsx')

    if not os.path.exists(path_historico):
        st.warning("El histórico está vacío. Guarda una comida desde el 'Planificador de Menús' para empezar.")
        return

    try:
        df_historico = pd.read_excel(path_historico)
        df_historico['fecha'] = pd.to_datetime(df_historico['fecha'])
        # Ordenar el DataFrame por fecha y hora de forma descendente
        df_historico.sort_values(by=['fecha', 'hora'], ascending=False, inplace=True)
    except Exception as e:
        st.error(f"No se pudo leer el archivo del histórico: {e}")
        return

    st.markdown("---")
    st.subheader("🔎 Filtrar Histórico")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not df_historico.empty:
            min_date, max_date = df_historico['fecha'].min().date(), df_historico['fecha'].max().date()
            fechas_seleccionadas = st.date_input(
                "Rango de fechas",
                value=(min_date, max_date),
                min_value=min_date, max_value=max_date
            )
        else:
            fechas_seleccionadas = st.date_input("Rango de fechas", value=(), disabled=True)

    with col2:
        comidas_seleccionadas = st.multiselect("Tipo de Comida", options=sorted(df_historico['comida'].unique()), placeholder="Elige uno o varios")

    with col3:
        platos_seleccionados = st.multiselect("Plato", options=sorted(df_historico['plato'].unique()), placeholder="Elige uno o varios")
    
    with col4:
        # Añadir filtro para grupo_ingrediente si la columna existe
        if 'grupo_ingrediente' in df_historico.columns:
            grupos_seleccionados = st.multiselect("Grupo Ingrediente", options=sorted(df_historico['grupo_ingrediente'].dropna().unique()), placeholder="Elige uno o varios")
        else:
            grupos_seleccionados = []

    # Aplicar filtros
    df_filtrado = df_historico.copy()
    if len(fechas_seleccionadas) == 2:
        start_date, end_date = pd.to_datetime(fechas_seleccionadas[0]), pd.to_datetime(fechas_seleccionadas[1])
        df_filtrado = df_filtrado[(df_filtrado['fecha'] >= start_date) & (df_filtrado['fecha'] <= end_date)]
    
    if comidas_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado['comida'].isin(comidas_seleccionadas)]
    
    if platos_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['plato'].isin(platos_seleccionados)]
    
    if grupos_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['grupo_ingrediente'].isin(grupos_seleccionados)]
        
    st.markdown("---")
    st.subheader("🗓️ Vista de Comidas Guardadas")

    # Formatear la fecha para la visualización sin la hora
    df_display = df_filtrado.copy()
    df_display['fecha'] = df_display['fecha'].dt.strftime('%Y-%m-%d')
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("✏️ Editar Histórico Completo")
    st.info("Para editar, haz doble clic en una celda de la tabla de abajo. Usa los iconos a la derecha para añadir o eliminar filas.")
    
    df_historico_editor = df_historico.copy()
    df_historico_editor['fecha'] = df_historico_editor['fecha'].dt.strftime('%Y-%m-%d')
    
    df_editado = st.data_editor(
        df_historico_editor,
        num_rows="dynamic",
        key="historico_editor",
        use_container_width=True,
        hide_index=True
    )

    if st.button("Guardar Cambios en el Histórico"):
        try:
            df_editado['fecha'] = pd.to_datetime(df_editado['fecha'])
            df_editado.to_excel(path_historico, index=False)
            st.success("¡Histórico actualizado correctamente!")
            st.rerun()
        except Exception as e:
            st.error(f"Ocurrió un error al guardar los cambios: {e}")


# --- LÓGICA PARA MOSTRAR LA PÁGINA SELECCIONADA ---
if pagina_seleccionada == "Planificador de Menús":
    pagina_planificador()
elif pagina_seleccionada == "Calculadora de Equivalencias":
    pagina_equivalencias()
elif pagina_seleccionada == "Histórico de Comidas":
    pagina_historico()
