
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard de Ingresos por Vertical", layout="wide")
st.title("💼 Dashboard de Ingresos por Verticales Financieras")
st.caption("Inputs:% de carga para verticales por volumen. % de clientes ingreso fijo.")

# =========================
# Parámetros Globales
# =========================
with st.sidebar:
    st.header("⚙️ Parámetros Globales")
    clientes_totales = st.number_input("Clientes actuales", min_value=0, value=111, step=1)
    volumen_total = st.number_input("Volumen anual total (USD)", min_value=0.0, value=8_000_000_000.0, step=100_000.0, format="%.2f")
    st.markdown("---")
    st.subheader("Formato")
    vista_anual = st.toggle("Ver como **ingresos anuales**", value=True, help="Si lo desactivas, se mostrará equivalente mensual (anual / 12).")

# Helper
def fmt_money(x):
    try:
        return f"$ {x:,.0f}"
    except Exception:
        return "$ 0"

pf = lambda x: x / 100.0  # porcentaje -> fracción

# =========================
# Entradas por Vertical (simplificadas)
# =========================
st.sidebar.subheader("🎚️ Adopción y Tarifas por Vertical")

# --- Financiamiento ---
with st.sidebar.expander("💳 Financiamiento", expanded=True):
    pct_carga_fin = st.slider("% de la carga que se financia", 0, 50, 30, 1)
    tarifa_fin = st.number_input("Tarifa Financiamiento (% sobre monto financiado)", 0.0, 10.0, 0.3, 0.05, format="%.2f")

# --- FX ---
with st.sidebar.expander("💱 FX", expanded=True):
    pct_carga_fx = st.slider("% de la carga que pasa por FX", 0, 50, 30, 1, help="Proporción del volumen total que realiza conversión.")
    tarifa_fx = st.number_input("Tarifa FX (% sobre monto transado)", 0.0, 10.0, 0.2, 0.05, format="%.2f")

# --- Seguro de Crédito ---
with st.sidebar.expander("🛡️ Seguro de Crédito", expanded=False):
    pct_carga_sc = st.slider("% de la carga asegurada con Seguro de Crédito", 0, 50, 5, 1)
    tarifa_sc = st.number_input("Tarifa Seguro de Crédito (% sobre carga asegurada)", 0.0, 1.0, 0.01, 0.01, format="%.2f")

# --- Seguro de Carga ---
with st.sidebar.expander("📦 Seguro de Carga", expanded=False):
    pct_carga_sca = st.slider("% de la carga asegurada con Seguro de Carga", 0, 50, 5, 1)
    tarifa_sca = st.number_input("Tarifa Seguro de Carga (% sobre carga asegurada)", 0.0, 1.0, 0.005, 0.01, format="%.2f")

# --- Pago de Fletes ---
with st.sidebar.expander("🚢 Pago de Fletes", expanded=True):
    pct_cli_pf = st.slider("% de clientes que usan Pago de Fletes (para fijo por cliente)", 0, 100, 30, 1)    
    fijo_pf = st.number_input("Fijo por cliente (USD)", 0.0, 10_000.0, 150.0, 10.0, format="%.2f")
    tarifa_pf = st.number_input("Tarifa variable (% sobre monto de carga)", 0.0, 10.0, 0.5, 0.05, format="%.2f")

# --- Gateway de Pago ---
with st.sidebar.expander("🏦 Gateway de Pago", expanded=True):
    pct_cli_gp = st.slider("% de clientes que usan Gateway de Pago", 25, 100, 50, 1)
    fee_gp = st.number_input("Fee por transacción (USD)", 0.0, 1_000.0, 35.0, 1.0, format="%.2f")
    tx_prom_cli = st.number_input("Transacciones promedio por cliente (al año)", 0, 100_000, 500, 10, help="Usado para proyectar ingresos por gateway.")

# =========================
# Cálculos
# =========================
# Volúmenes por vertical (solo % de carga)
vol_fin = volumen_total * pf(pct_carga_fin)
vol_fx  = volumen_total * pf(pct_carga_fx)
vol_sc  = volumen_total * pf(pct_carga_sc)
vol_sca = volumen_total * pf(pct_carga_sca)
vol_pf  = volumen_total * 0.1 * pct_cli_pf/clientes_totales

# Tarifas como fracciones
t_fin = pf(tarifa_fin)
t_fx  = pf(tarifa_fx)
t_sc  = pf(tarifa_sc)
t_sca = pf(tarifa_sca)
t_pf  = pf(tarifa_pf)

# Nº clientes para verticales que lo requieren
n_pf  = round(clientes_totales * pf(pct_cli_pf) )  # fijo por cliente en Pago de Fletes
n_gp  = round(clientes_totales * pf(pct_cli_gp))  # gateway: tx por cliente

# Ingresos (anuales)
ingreso_fin = vol_fin * t_fin
ingreso_fx  = vol_fx  * t_fx
ingreso_sc  = vol_sc  * t_sc
ingreso_sca = vol_sca * t_sca
ingreso_pf  = n_pf * fijo_pf * 12 + vol_pf * t_pf
ingreso_gp  = n_gp * tx_prom_cli * fee_gp

# Consolidado
data = [
    {"Vertical": "Financiamiento", "Clientes": None, "Volumen USD": vol_fin, "Ingreso Anual USD": ingreso_fin},
    {"Vertical": "FX",             "Clientes": None, "Volumen USD": vol_fx,  "Ingreso Anual USD": ingreso_fx},
    {"Vertical": "Seguro Crédito", "Clientes": None, "Volumen USD": vol_sc,  "Ingreso Anual USD": ingreso_sc},
    {"Vertical": "Seguro Carga",   "Clientes": None, "Volumen USD": vol_sca, "Ingreso Anual USD": ingreso_sca},
    {"Vertical": "Pago de Fletes", "Clientes": n_pf, "Volumen USD": vol_pf,  "Ingreso Anual USD": ingreso_pf},
    {"Vertical": "Gateway de Pago","Clientes": n_gp, "Volumen USD": np.nan,  "Ingreso Anual USD": ingreso_gp},
]

df = pd.DataFrame(data)

# Mensualización si corresponde
if not vista_anual:
    df["Ingreso Mensual USD"] = df["Ingreso Anual USD"] / 12.0

total_anual = df["Ingreso Anual USD"].sum()
total_mensual = total_anual / 12.0

# =========================
# Layout principal
# =========================
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("📊 Ingresos proyectados por vertical")
    campo_ing = "Ingreso Anual USD" if vista_anual else "Ingreso Mensual USD"
    y_vals = df[campo_ing].fillna(0.0).values
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Vertical"], y=y_vals, text=[fmt_money(v) for v in y_vals], textposition="outside"))
    fig.update_layout(
        height=500,
        xaxis_title="Vertical",
        yaxis_title="USD" + (" (anual)" if vista_anual else " (mensual)"),
        margin=dict(l=10, r=10, t=40, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 📋 Detalle")
    mostrar_cols = ["Vertical", "Clientes", "Volumen USD", "Ingreso Anual USD"]
    if not vista_anual:
        mostrar_cols += ["Ingreso Mensual USD"]

    df_mostrar = df.copy()
    df_mostrar["Clientes"] = df_mostrar["Clientes"].apply(lambda x: int(x) if pd.notna(x) else "—")
    df_mostrar["Volumen USD"] = df_mostrar["Volumen USD"].apply(lambda x: fmt_money(x) if pd.notna(x) else "—")
    df_mostrar["Ingreso Anual USD"] = df_mostrar["Ingreso Anual USD"].apply(fmt_money)
    if not vista_anual:
        df_mostrar["Ingreso Mensual USD"] = df_mostrar["Ingreso Mensual USD"].apply(fmt_money)

    st.dataframe(df_mostrar[mostrar_cols], use_container_width=True, hide_index=True)

with col2:
    st.subheader("🧮 Totales")
    if vista_anual:
        st.metric("Ingreso total anual (USD)", fmt_money(total_anual))
        st.metric("Ingreso total mensual estimado (USD)", fmt_money(total_mensual))
    else:
        st.metric("Ingreso total mensual (USD)", fmt_money(total_mensual))
        st.metric("Ingreso total anual estimado (USD)", fmt_money(total_anual))

    st.markdown("---")
    st.subheader("Supuestos actuales")
    st.markdown(f"- Clientes totales: **{clientes_totales}**")
    st.markdown(f"- Volumen anual total: **{fmt_money(volumen_total)}**")
    st.markdown("**Tarifas vigentes:**")
    st.markdown(f"- Financiamiento: **{tarifa_fin:.2f}%** sobre {pct_carga_fin}% de la carga")
    st.markdown(f"- FX: **{tarifa_fx:.2f}%** sobre {pct_carga_fx}% de la carga")
    st.markdown(f"- Seguro Crédito: **{tarifa_sc:.2f}%** sobre {pct_carga_sc}% de la carga")
    st.markdown(f"- Seguro Carga: **{tarifa_sca:.2f}%** sobre {pct_carga_sca}% de la carga")
    st.markdown(f"- Pago de Fletes: **{fmt_money(fijo_pf)} fijo/cliente** (aplica a {pct_cli_pf}% de clientes) + **{tarifa_pf:.2f}%** sobre valor pagado por fletes")
    st.markdown(f"- Gateway de Pago: **{fmt_money(fee_gp)} por transacción** · {pct_cli_gp}% de clientes · **{tx_prom_cli}** tx/cliente/año")

st.markdown("---")
st.caption("Simplificación aplicada: para verticales por volumen se usa solo % de carga. % de clientes solo se usa en Pago de Fletes (fijo por cliente) y Gateway de Pago.")
