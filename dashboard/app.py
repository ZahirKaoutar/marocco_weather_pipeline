import streamlit as st
import plotly.express as px
from db.data import (
    get_top_temperatures, get_top_precipitations, get_top_risque_moyen,
    get_periodes_risque_max, get_risque_par_ville,
    get_number_ville, get_maximal_precipitation, get_maximal_temp
)

def_villes_temperatures=get_top_temperatures()
def_villes_precipitations=get_top_precipitations()
def_villes_risquem=get_top_risque_moyen()
def_get_periodes_risque_max= get_periodes_risque_max()
def_risque_ville=get_risque_par_ville()
nmbr_ville=get_number_ville()





ville_selc=st.sidebar.selectbox("Ville",["Tout"]+sorted(def_villes_temperatures["city"].unique().tolist()))
risques_selc=st.sidebar.selectbox("Risque",["Tous"]+sorted(def_risque_ville["risque_max"].unique().tolist()))



fig1=px.bar(def_villes_temperatures,x="city",y="temp_max",color_discrete_sequence=["red"])

st.title("graphe des villes en fonctionne temperature")
fig1.update_yaxes(range=[40, 43])

st.plotly_chart(fig1, use_container_width=True)

fig2=px.bar(def_villes_precipitations,x="city",y="precipitation_max")
st.title("graphe des villes en fonctionne precipitation")

st.plotly_chart(fig2, use_container_width=True)


fig3=px.bar(def_villes_risquem,x="city",y="risque_moyen")
st.title("graphe des ville en fonction  de  risque weather_moyen")
st.plotly_chart(fig3,use_container_width=True)

fig4=px.bar(def_get_periodes_risque_max,x="time",y="risque_max")
st.title("graphe de rique maximale en fonction de periode")
st.plotly_chart(fig4,use_container_width=True)

fig5 = px.bar(def_risque_ville, x="time", y="risque_max", color="city", barmode="group")
st.title("graphe de rique maximale en fonction de temp")
st.plotly_chart(fig5,use_container_width=True)