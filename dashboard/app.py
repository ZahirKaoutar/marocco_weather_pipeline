
import streamlit as st
import plotly.express as px

from db.data import (
    get_top_temperatures,
    get_top_precipitations,
    get_top_risque_moyen,
    get_periodes_risque_max,
    get_risque_par_ville,
    get_number_ville,
    get_maximal_precipitation,
    get_maximal_temp,
    get_categories_risque_aujourdhui,
    get_categories_temperature_aujourdhui,
    get_categories_precipitation_aujourdhui,
    get_categories_vent_aujourdhui
)



st.set_page_config(
    page_title="MétéoRisk Maroc",
    layout="wide"
)

st.title("Dashboard MétéoRisk — Prévisions & Risques Météo Maroc")
st.markdown("---")


# ==========================
# Chargement des données
# ==========================

df_temperatures = get_top_temperatures()
df_precipitations = get_top_precipitations()
df_risquem = get_top_risque_moyen()
df_periodes = get_periodes_risque_max()
df_risque_ville = get_risque_par_ville()

max_temp = get_maximal_temp()
max_precip = get_maximal_precipitation()
nmbr_ville = get_number_ville()

df_risque_categories = get_categories_risque_aujourdhui()
df_temperature_categories = get_categories_temperature_aujourdhui()
df_precipitation_categories = get_categories_precipitation_aujourdhui()
df_vent_categories = get_categories_vent_aujourdhui()


# ==========================
# KPI — Indicateurs clés
# ==========================

st.subheader("Indicateurs Clés")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Nombre de villes",
        int(nmbr_ville["number_city"].iloc[0])
    )

with col2:
    st.metric(
        "Température maximale",
        f"{max_temp['max_temp'].iloc[0]} °C"
    )

with col3:
    st.metric(
        "Précipitations maximales",
        f"{max_precip['max_precipitation'].iloc[0]} mm"
    )

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
    labels={
        "city": "Ville",
        "temp_max": "Température max (°C)"
    }
)

fig1.update_traces(textposition="outside")
fig1.update_layout(
    showlegend=False,
    coloraxis_showscale=False
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==========================
# Graphique 2 — Précipitations
# ==========================

st.subheader(
    "Top 10 des villes avec les plus fortes précipitations"
)

fig2 = px.bar(
    df_precipitations,
    x="city",
    y="precipitation_max",
    color="precipitation_max",
    color_continuous_scale="Blues",
    text_auto=".1f",
    labels={
        "city": "Ville",
        "precipitation_max": "Précipitations max (mm)"
    }
)

fig2.update_traces(textposition="outside")
fig2.update_layout(
    showlegend=False,
    coloraxis_showscale=False
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ==========================
# Graphique 3 — Risque moyen
# ==========================

st.subheader(
    "Top 10 des villes avec le risque météorologique moyen le plus élevé"
)

fig3 = px.bar(
    df_risquem,
    x="city",
    y="risque_moyen",
    color="risque_moyen",
    color_continuous_scale="Oranges",
    text_auto=".2f",
    labels={
        "city": "Ville",
        "risque_moyen": "Score de risque moyen"
    }
)

fig3.update_traces(textposition="outside")
fig3.update_layout(
    showlegend=False,
    coloraxis_showscale=False
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ==========================
# Graphique 4 — Risque max par période
# ==========================

st.subheader(
    "Risque maximal par période"
)

fig4 = px.bar(
    df_periodes,
    x="time",
    y="risque_max",
    color="risque_max",
    color_continuous_scale="YlOrRd",
    text_auto=".1f",
    labels={
        "time": "Date",
        "risque_max": "Score de risque maximal"
    }
)

fig4.update_xaxes(type="category")

fig4.update_traces(
    textposition="outside"
)

fig4.update_layout(
    showlegend=False,
    coloraxis_showscale=False
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# ==========================
# Graphique 5 — Risque par ville
# ==========================

st.subheader(
    "Évolution du risque maximal par ville et par date"
)

# Prendre les 5 villes avec le risque moyen le plus élevé
top5_villes = df_risquem["city"].head(5).tolist()

df_risque_filtre = df_risque_ville[
    df_risque_ville["city"].isin(top5_villes)
]

fig5 = px.bar(
    df_risque_filtre,
    x="time",
    y="risque_max",
    color="city",
    barmode="group",
    text_auto=".1f",
    labels={
        "time": "Date",
        "risque_max": "Score de risque maximal",
        "city": "Ville"
    },
    title="Risque maximal — Top 5 villes"
)

fig5.update_xaxes(type="category")

st.plotly_chart(
    fig5,
    use_container_width=True
)



st.markdown("---")
st.subheader("Répartition des villes aujourd'hui")


# ==========================
# Ligne 1
# ==========================

col1, col2 = st.columns(2)


with col1:

    fig_risque = px.pie(
        df_risque_categories,
        names="risk_category",
        values="nombre_villes",
        title="Niveau de risque"
    )

    fig_risque.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig_risque.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_risque,
        use_container_width=True
    )


with col2:

    fig_temperature = px.pie(
        df_temperature_categories,
        names="temperature_category",
        values="nombre_villes",
        title="Catégories de température"
    )

    fig_temperature.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig_temperature.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_temperature,
        use_container_width=True
    )


# ==========================
# Ligne 2
# ==========================

col3, col4 = st.columns(2)


with col3:

    fig_precipitation = px.pie(
        df_precipitation_categories,
        names="precipitation_category",
        values="nombre_villes",
        title="Catégories de précipitation"
    )

    fig_precipitation.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig_precipitation.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_precipitation,
        use_container_width=True
    )


with col4:

    fig_vent = px.pie(
        df_vent_categories,
        names="wind_category",
        values="nombre_villes",
        title="Catégories de vent"
    )

    fig_vent.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )

    fig_vent.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_vent,
        use_container_width=True
    )

