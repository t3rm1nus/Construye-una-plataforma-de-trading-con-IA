import os
import sqlite3
from datetime import datetime, timezone
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Panel de la plataforma", layout="wide")
st.title("Panel de control")
st.caption("Vista de solo lectura. No envía ni modifica órdenes.")
if st.button("Actualizar datos"):
    st.rerun()


def leer(consulta: str) -> pd.DataFrame:
    ruta = os.environ.get("RUTA_BD", "plataforma.db")
    con = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    try:
        return pd.read_sql_query(consulta, con)
    finally:
        con.close()
try:
    ordenes = leer("SELECT id, simbolo, lado, cantidad, estado, ts_ms "
                   "FROM ordenes ORDER BY ts_ms DESC LIMIT 50")
except (sqlite3.Error, OSError, ValueError) as exc:
    st.error(f"No se pudo leer el estado de la plataforma: {exc}")
    st.stop()
if not ordenes.empty:
    ultimo_ms = int(ordenes["ts_ms"].max())
    edad_s = max(0, (datetime.now(timezone.utc).timestamp() * 1000 - ultimo_ms) / 1000)
    st.caption(f"Última orden registrada hace {edad_s:.1f} segundos (UTC)")
else:
    st.info("Todavía no se ha registrado ninguna orden.")
abiertas = ordenes[~ordenes["estado"].isin(["ejecutada", "cancelada", "rechazada"])]
col1, col2 = st.columns(2)
col1.metric("Órdenes recientes", len(ordenes))
col2.metric("Órdenes activas", len(abiertas))
st.subheader("Últimas órdenes")
st.dataframe(ordenes.drop(columns=["ts_ms"], errors="ignore"), width="stretch")
