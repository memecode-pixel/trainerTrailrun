import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# Título SIEMPRE visible
# -------------------------

st.title("Trail Training Recommendation System")
st.write("Sube tu archivo de actividades exportado desde Strava para comenzar.")

# -------------------------
# File uploader
# -------------------------

uploaded_file = st.file_uploader("Sube tu archivo CSV de Strava", type=["csv"])

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        # -------------------------
        # Renombrar columnas
        # -------------------------

        df = df.rename(columns={
            "Fecha de la actividad": "date",
            "Tipo de actividad": "type",
            "Tiempo transcurrido": "duration_sec",
            "Distancia": "distance_km",
            "Desnivel positivo": "elev_gain"
        })

        # -------------------------
        # Conversión de tipos
        # -------------------------

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")
        df["duration_sec"] = pd.to_numeric(df["duration_sec"], errors="coerce")
        df["elev_gain"] = pd.to_numeric(df["elev_gain"], errors="coerce").fillna(0)

        # -------------------------
        # Filtrar solo carreras
        # -------------------------

        df_run = df[df["type"] == "Carrera"].copy()
        df_run = df_run[df_run["distance_km"] > 0]

        if df_run.empty:
            st.warning("No se encontraron actividades tipo 'Carrera' en el archivo.")
        else:

            # -------------------------
            # Crear Trail Load
            # -------------------------

            df_run["trail_load"] = df_run["distance_km"] + (df_run["elev_gain"] / 100)

            # -------------------------
            # Carga semanal
            # -------------------------

            df_run["year"] = df_run["date"].dt.year
            df_run["week"] = df_run["date"].dt.isocalendar().week

            weekly = (
                df_run
                .groupby(["year","week"])["trail_load"]
                .sum()
                .reset_index()
            )

            # -------------------------
            # Calcular AC Ratio
            # -------------------------

            if len(weekly) >= 4:
                acute = weekly["trail_load"].iloc[-1]
                chronic = weekly["trail_load"].tail(4).mean()
                ratio = acute / chronic
            else:
                acute = weekly["trail_load"].iloc[-1]
                chronic = weekly["trail_load"].mean()
                ratio = acute / chronic if chronic != 0 else 1

            st.subheader("Estado actual")

            st.write("Carga aguda:", round(acute,2))
            st.write("Carga crónica:", round(chronic,2))
            st.write("AC Ratio:", round(ratio,2))

            # -------------------------
            # Input distancia objetivo
            # -------------------------

            target_distance = st.number_
