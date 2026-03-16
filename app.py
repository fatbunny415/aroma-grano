import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="BizIntelligence Aroma & Grano", layout="wide")
st.title("📊 BI Dashboard: Aroma & Grano")

# --- CARGA PROFESIONAL ---
@st.cache_data
def cargar_inventario():
    # Usamos low_memory=False para archivos grandes (en este caso es pequeño pero es buena práctica)
    return pd.read_csv("ventas_pro.csv")

df = cargar_inventario()

# --- SONDEO INICIAL (Teoría en acción) ---
st.header("🔍 1. Sondeo de Categorías")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Productos Únicos", df['producto'].nunique())
    
with col2:
    st.write("Tipos de productos encontrados:")
    st.write(df['tipo'].unique())

with col3:
    st.write("Frecuencia de ventas por producto:")
    st.write(df['producto'].value_counts())
st.text_area(
    "✍️ Tu explicación (Propias palabras, sin IA):", 
    value="Aquí básicamente damos un primer vistazo a los datos. Usamos Streamlit para mostrar métricas rápidas: cuántos productos diferentes tenemos, qué categorías hay y cuáles son los que más se repiten o venden (frecuencia). Es necesario para entender la estructura de la base de datos antes de limpiarla.", 
    key="reflexion_paso_2"
)



st.divider()
st.header("🛠️ 2. Motor de Limpieza")

# PASO A: Eliminar Duplicados (Vimos el ID 2 y 10 repetidos en el CSV)
df = df.drop_duplicates(subset=['id'])

# PASO B: Corregir Tipos de Datos
# El CSV tiene el ID 12 con cantidad "1" entre comillas (texto). Lo forzamos a número.
df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce')

# PASO C: Rellenar Nulos (NaN)
# Si no sabemos la cantidad, asumiremos que se vendió 1 unidad.
df['cantidad'] = df['cantidad'].fillna(1)

st.success("✅ Limpieza automátizada: Duplicados removidos, números corregidos y nulos rellenados.")
st.dataframe(df)
st.text_area(
    "✍️ Tu explicación (Propias palabras, sin IA):", 
    value="Esta parte es nuestra limpieza de datos. Básicamente lo que se hizo fue quitar las filas repetidas usando el ID, asegurarnos de que la cantidad de productos fuera un número (a veces hay errores en el archivo original) y si faltaba la cantidad, se asumió que era 1 para que las cuentas de más adelante no den error.", 
    key="reflexion_paso_3"
)



st.divider()
st.header("✨ 3. Transformación de Reporte")

# Calculamos el subtotal primero
df['Ingreso_Bruto'] = df['precio'] * df['cantidad']

# CREAMOS UNA VISTA LIMPIA PARA EL REPORTE
# Renombramos y ordenamos de mayor ingreso a menor
reporte_ejecutivo = df.rename(columns={
    'id': 'ID Pedido',
    'producto': 'Producto',
    'Ingreso_Bruto': 'Venta Total ($)'
}).sort_values(by='Venta Total ($)', ascending=False)

st.write("Top de ventas del mes (Ordenado):")
st.dataframe(reporte_ejecutivo[['ID Pedido', 'Producto', 'Venta Total ($)']].head(10))
st.text_area(
    "✍️ Tu explicación (Propias palabras, sin IA):", 
    value="Acá ya empezamos a ver plata. Multiplicamos el precio del producto por la cantidad para saber cuánto se vendió. También le cambié el nombre a las columnas para que se vean más bonitas en el reporte final y organicé la tabla de mayor a menor para ver enseguida cuáles fueron los productos que más plata dejaron.", 
    key="reflexion_paso_4"
)



st.sidebar.header("⚙️ Panel de Auditoría")

# Filtro multi-selección
ciudades_filtro = st.sidebar.multiselect(
    "Filtrar por Tipo:",
    options=df['tipo'].unique(),
    default=df['tipo'].unique()
)

# Filtro Slider
monto_min = st.sidebar.slider("Ver ventas superiores a ($):", 0, 100, 0)

# APLICACIÓN DE LÓGICA FILTRADO (AND)
# Que pertenezca al tipo seleccionado Y supere el monto mínimo
df_final = df[(df['tipo'].isin(ciudades_filtro)) & (df['Ingreso_Bruto'] >= monto_min)]

st.subheader("📋 Pedidos Filtrados")
st.table(df_final)
st.text_area(
    "✍️ Tu explicación (Propias palabras, sin IA):", 
    value="Aquí se agrego un menú a la izquierda para poder filtrar la información. Contiene dos opciones: una para elegir la categoría del producto y otra para ver solo las ventas que pasen de cierta cantidad de plata. Lo bueno es que ambos filtros funcionan a la vez, así es mucho más fácil buscar algo puntual.", 
    key="reflexion_paso_5"
)



st.divider()
st.header("📈 4. Análisis Agregado")

# Agrupamos por tipo y sumamos ingresos
resumen = df.groupby('tipo')['Ingreso_Bruto'].agg(['sum', 'count', 'mean']).round(2)
st.write(resumen)

st.bar_chart(resumen['sum'])
st.text_area(
    "✍️ Tu explicación (Propias palabras, sin IA):", 
    value="Para esta parte se agruparon los datos por la categoría del producto (si es café, postre, etc.) y sumé cuánto entró por cada una. Con esa información armé un gráfico de barras, que me parece la forma más rápida y visual de darse cuenta qué tipo de producto es el que más nos está haciendo ganar.", 
    key="reflexion_paso_6"
)



# Tabla de ejemplo de proveedores
proveedores = pd.DataFrame({
    'producto': ['Espresso', 'Latte', 'Capuccino', 'Muffin', 'Cold Brew', 'Pastel de Chocolate'],
    'Proveedor': ['Granos del Cauca', 'Lácteos Central', 'Lácteos Central', 'Trigo & Sal', 'Refrescantes S.A.', 'Delicias Doña Ana']
})

# Fusión (Merge)
df_maestro = pd.merge(df, proveedores, on='producto', how='left')

st.header("🏢 Contacto de Proveedores por Pedido")
st.dataframe(df_maestro[['id', 'producto', 'Proveedor']])
st.text_area(
    "✍️ Tu explicación (Propias palabras, sin IA):", 
    value="Por último, se creó una tabla pequeñita con los nombres de los proveedores. Lo que se hizo fue cruzar esa tabla nueva con la tabla principal de ventas que ya teníamos, usando el nombre del producto para emparejarlos. Así ahora podemos ver el registro de ventas y al lado a quién le compramos ese producto.", 
    key="reflexion_paso_7"
)
