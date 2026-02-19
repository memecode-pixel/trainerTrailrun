import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Trail Training Recommendation System")
st.write("Sube tu archivo de actividades exportado desde Strava para comenzar.")

uploaded_file = st.file_uploader("Sube tu archivo CSV de Strava", type=["csv"])

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        df = df.rename(columns={
            "Fecha de la actividad": "date",
            "Tipo de actividad": "type",
            "Tiempo transcurrido": "duration_sec",
            "Distancia": "distance_km",
            "Desnivel positivo": "elev_gain"
        })

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")
        df["duration_sec"] = pd.to_numeric(df["duration_sec"], errors="coerce")
        df["elev_gain"] = pd.to_numeric(df["elev_gain"], errors="coerce").fillna(0)

        df_run = df[df["type"] == "Carrera"].copy()
        df_run = df_run[df_run["distance_km"] > 0]

        if df_run.empty:
            st.warning("No se encontraron actividades tipo 'Carrera'.")
        else:

            df_run["trail_load"] = df_run["distance_km"] + (df_run["elev_gain"] / 100)

            df_run["year"] = df_run["date"].dt.year
            df_run["week"] = df_run["date"].dt.isocalendar().week

            weekly = (
                df_run
                .groupby(["year", "week"])["trail_load"]
                .sum()
                .reset_index()
            )

            if len(weekly) >= 4:
                acute = weekly["trail_load"].iloc[-1]
                chronic = weekly["trail_load"].tail(4).mean()
                ratio = acute / chronic
            else:
                acute = weekly["trail_load"].iloc[-1]
                chronic = weekly["trail_load"].mean()
                ratio = acute / chronic if chronic != 0 else 1

            st.subheader("Estado actual")
            st.write("Carga aguda:", round(acute, 2))
            st.write("Carga crónica:", round(chronic, 2))
            st.write("AC Ratio:", round(ratio, 2))

            target_distance = st.number_input(
                "Distancia objetivo (km)",
                min_value=5,
                max_value=100,
                value=15
            )

            current_max = df_run["distance_km"].max()

            st.subheader("Recomendación")

            if target_distance > current_max:

                gap = target_distance - current_max

                if ratio < 0.8:
                    progression_rate = 0.10
                elif ratio <= 1.3:
                    progression_rate = 0.07
                else:
                    progression_rate = 0.03

                weekly_increase = current_max * progression_rate
                weeks_needed = gap / weekly_increase if weekly_increase != 0 else 0

                st.write("Distancia máxima actual:", round(current_max, 2), "km")
                st.write("Aumento recomendado por semana:", round(weekly_increase, 2), "km")
                st.write("Semanas estimadas:", round(weeks_needed, 1))

            else:
                st.success("Ya tienes base suficiente para esa distancia objetivo.")

            st.subheader("Carga semanal histórica")

            fig, ax = plt.subplots()
            ax.plot(weekly["trail_load"])
            ax.set_xlabel("Semanas")
            ax.set_ylabel("Trail Load")
            st.pyplot(fig)

    except Exception as e:
        st.error("Error procesando el archivo:")
        st.error(e)
