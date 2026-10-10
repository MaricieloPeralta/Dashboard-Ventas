import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de ventas", page_icon="📊", layout="wide")

st.title("📊 Dashboard de ventas")
st.write(
    "Sube un archivo CSV con tus ventas y la app calcula totales y gráficos. "
    "Columnas requeridas: **fecha, producto, categoria, cantidad, precio_unitario**."
)

COLUMNAS = ["fecha", "producto", "categoria", "cantidad", "precio_unitario"]

# --- 1. Cargar datos ---
archivo = st.file_uploader("Sube tu archivo CSV", type="csv")

if archivo is not None:
    df = pd.read_csv(archivo)
else:
    st.info("No subiste archivo: se muestran datos de ejemplo.")
    try:
        df = pd.read_csv("ventas_ejemplo.csv")
    except FileNotFoundError:
        st.stop()

# --- 2. Validar y limpiar ---
faltan = [c for c in COLUMNAS if c not in df.columns]
if faltan:
    st.error(f"Faltan estas columnas en tu CSV: {', '.join(faltan)}")
    st.stop()

df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
df = df.dropna(subset=["fecha", "cantidad", "precio_unitario"])
df["ingreso"] = df["cantidad"] * df["precio_unitario"]  # ingreso de cada venta
df["mes"] = df["fecha"].dt.to_period("M").astype(str)

# --- 3. Filtros (barra lateral) ---
st.sidebar.header("Filtros")
productos = st.sidebar.multiselect(
    "Producto", sorted(df["producto"].unique()), default=sorted(df["producto"].unique())
)
f_min, f_max = df["fecha"].min().date(), df["fecha"].max().date()
rango = st.sidebar.date_input("Rango de fechas", (f_min, f_max), min_value=f_min, max_value=f_max)

filtrado = df[df["producto"].isin(productos)]
if len(rango) == 2:
    filtrado = filtrado[
        (filtrado["fecha"].dt.date >= rango[0]) & (filtrado["fecha"].dt.date <= rango[1])
    ]

if filtrado.empty:
    st.warning("No hay ventas con esos filtros.")
    st.stop()

# --- 4. Indicadores ---
total = filtrado["ingreso"].sum()
unidades = int(filtrado["cantidad"].sum())
ticket = filtrado["ingreso"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ingresos totales", f"S/ {total:,.2f}")
c2.metric("Unidades vendidas", f"{unidades:,}")
c3.metric("Número de ventas", f"{len(filtrado):,}")
c4.metric("Ticket promedio", f"S/ {ticket:,.2f}")

# --- 5. Gráficos ---
g1, g2 = st.columns(2)
with g1:
    st.subheader("Ingresos por mes")
    st.bar_chart(filtrado.groupby("mes")["ingreso"].sum())
with g2:
    st.subheader("Ingresos por producto")
    st.bar_chart(filtrado.groupby("producto")["ingreso"].sum().sort_values(ascending=False))

# --- 6. Tabla y descarga ---
st.subheader("Detalle de ventas")
st.dataframe(filtrado.drop(columns="mes"), width="stretch")
