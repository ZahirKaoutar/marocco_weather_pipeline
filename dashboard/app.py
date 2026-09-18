import streamlit as st
import plotly.express as px
from db.data import (
    get_top_temperatures, get_top_precipitations, get_top_risque_moyen,
    get_periodes_risque_max, get_risque_par_ville,
    get_number_ville, get_maximal_precipitation, get_maximal_temp,
    get_all_villes, get_all_dates, get_meteo_detail
)


st.set_page_config(
    page_title="MétéoRisk Maroc",
    
    layout="wide"
)

st.title("Dashboard MétéoRisk — Prévisions & Risques Météo Maroc")
st.markdown("---")


df_temperatures    = get_top_temperatures()
df_precipitations  = get_top_precipitations()
df_risquem         = get_top_risque_moyen()
df_periodes        = get_periodes_risque_max()
df_risque_ville    = get_risque_par_ville()
max_temp           = get_maximal_temp()
max_precip         = get_maximal_precipitation()
nmbr_ville         = get_number_ville()
all_villes         = get_all_villes()
all_dates          = get_all_dates()

# ==========================
# Barre latérale — Filtres
# ==========================
st.sidebar.title("Filtres")

ville_selc = st.sidebar.selectbox(
    "Ville",
    ["Toutes les villes"] + all_villes
)

date_selc = st.sidebar.selectbox(
    "Date",
    ["Toutes les dates"] + all_dates
)

risque_selc = st.sidebar.selectbox(
    "⚠️ Niveau de risque",
    ["Tous", "Faible", "Modéré", "Élevé"]
)

# Préparer les paramètres de filtre
ville_param  = None if ville_selc == "Toutes les villes" else ville_selc
date_param   = None if date_selc == "Toutes les dates" else date_selc
risque_param = None if risque_selc == "Tous" else risque_selc

# Charger les données filtrées (utilisées pour le tableau détaillé)
df_detail = get_meteo_detail(ville=ville_param, date=date_param, niveau_risque=risque_param)

# ==========================
# KPI — Indicateurs clés
# ==========================
st.subheader("Indicateurs Clés")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Nombre de villes", int(nmbr_ville["number_city"].iloc[0]))
with col2:
    st.metric("Température maximale", f"{max_temp['max_temp'].iloc[0]} °C")
with col3:
    st.metric("Précipitations maximales", f"{max_precip['max_precipitation'].iloc[0]} mm")
with col4:
    nb_risque_eleve = len(df_detail[df_detail["risk_category"] == "Élevé"]) if not df_detail.empty else 0
    st.metric("Alertes risque élevé", nb_risque_eleve)

st.markdown("---")

# ==========================
# Graphique 1 — Températures
# ==========================
st.subheader("Top 10 des villes les plus chaudes")

fig1 = px.bar(
    df_temperatures,
    x="city",
    y="temp_max",
    color="temp_max",
    color_continuous_scale="Reds",
    text_auto=".1f",
    labels={"city": "Ville", "temp_max": "Température max (°C)"}
)
fig1.update_traces(textposition="outside")
fig1.update_layout(showlegend=False, coloraxis_showscale=False)
st.plotly_chart(fig1, use_container_width=True)

# ==========================
# Graphique 2 — Précipitations
# ==========================
st.subheader("Top 10 des villes avec les plus fortes précipitations")

# Appliquer le filtre ville si sélectionné
if ville_param:
    df_precip_filtre = df_precipitations[df_precipitations["city"] == ville_param]
    if df_precip_filtre.empty:
        st.info(f"Aucune donnée de précipitation pour **{ville_param}** dans le top 10. Affichage général.")
        df_precip_filtre = df_precipitations
else:
    df_precip_filtre = df_precipitations

fig2 = px.bar(
    df_precip_filtre,
    x="city",
    y="precipitation_max",
    color="precipitation_max",
    color_continuous_scale="Blues",
    text_auto=".1f",
    labels={"city": "Ville", "precipitation_max": "Précipitations max (mm)"}
)
fig2.update_traces(textposition="outside")
fig2.update_layout(showlegend=False, coloraxis_showscale=False)
st.plotly_chart(fig2, use_container_width=True)

# ==========================
# Graphique 3 — Risque moyen
# ==========================
st.subheader("Top 10 des villes avec le risque météorologique moyen le plus élevé")

fig3 = px.bar(
    df_risquem,
    x="city",
    y="risque_moyen",
    color="risque_moyen",
    color_continuous_scale="Oranges",
    text_auto=".2f",
    labels={"city": "Ville", "risque_moyen": "Score de risque moyen"}
)
fig3.update_traces(textposition="outside")
fig3.update_layout(showlegend=False, coloraxis_showscale=False)
st.plotly_chart(fig3, use_container_width=True)

# ==========================
# Graphique 4 — Risque max par période
# ==========================
st.subheader("Risque maximal par période (tous les jours de prévision)")

fig4 = px.bar(
    df_periodes,
    x="time",
    y="risque_max",
    color="risque_max",
    color_continuous_scale="YlOrRd",
    text_auto=".1f",
    labels={"time": "Date", "risque_max": "Score de risque maximal"}
)
fig4.update_xaxes(type="category")
fig4.update_traces(textposition="outside")
fig4.update_layout(showlegend=False, coloraxis_showscale=False)
st.plotly_chart(fig4, use_container_width=True)

# ==========================
# Graphique 5 — Risque par ville (filtré par ville)
# ==========================
st.subheader("Évolution du risque maximal par ville et par date")

if ville_param:
    df_risque_filtre = df_risque_ville[df_risque_ville["city"] == ville_param]
    titre_fig5 = f"Risque maximal — {ville_param}"
else:
    # Prendre les 5 villes avec le plus grand risque global pour éviter la surcharge
    top5_villes = df_risquem["city"].head(5).tolist()
    df_risque_filtre = df_risque_ville[df_risque_ville["city"].isin(top5_villes)]
    titre_fig5 = "Risque maximal — Top 5 villes les plus à risque (sélectionnez une ville pour filtrer)"

fig5 = px.bar(
    df_risque_filtre,
    x="time",
    y="risque_max",
    color="city",
    barmode="group",
    text_auto=".1f",
    labels={"time": "Date", "risque_max": "Score de risque maximal", "city": "Ville"},
    title=titre_fig5
)
fig5.update_xaxes(type="category")
st.plotly_chart(fig5, use_container_width=True)

# ==========================
# Tableau détaillé filtré
# ==========================
st.markdown("---")
st.subheader("Données détaillées filtrées")

filtre_actif = []
if ville_param:
    filtre_actif.append(f"Ville : **{ville_param}**")
if date_param:
    filtre_actif.append(f"Date : **{date_param}**")
if risque_param:
    filtre_actif.append(f"Niveau de risque : **{risque_param}**")

if filtre_actif:
    st.markdown("Filtres actifs : " + " | ".join(filtre_actif))
else:
    st.markdown("Aucun filtre actif — affichage de toutes les données.")

if df_detail.empty:
    st.warning("Aucune donnée trouvée pour les filtres sélectionnés.")
else:
    st.dataframe(
        df_detail.rename(columns={
            "city": "Ville",
            "date": "Date",
            "temperature_2m_max": "Temp. max (°C)",
            "temperature_2m_min": "Temp. min (°C)",
            "temperature_moyenne_jour": "Temp. moyenne (°C)",
            "temperature_category": "Catégorie Temp.",
            "precipitation_sum": "Précip. (mm)",
            "precipitation_category": "Catégorie Précip.",
            "windspeed_10m_max": "Vent max (km/h)",
            "wind_category": "Catégorie Vent",
            "weather_risk_score": "Score de risque",
            "risk_category": "Niveau de risque"
        }),
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"{len(df_detail)} ligne(s) affichée(s)")
