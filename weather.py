import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Oldal beállítás
st.set_page_config(page_title="Időjárás Dashboard", layout="wide")

# API kulcs 
API_KEY = st.secrets["api_key"]

# cache

@st.cache_data(ttl=600)
def get_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=hu"
    return requests.get(url).json()

@st.cache_data(ttl=600)
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=hu"
    return requests.get(url).json()

# UI
st.title("Időjárás Dashboard")

# Város bemeneti mező
city = st.text_input("Város megadása:", value="Budapest")

if city:
    weather = get_current_weather(city)

    if weather.get("cod") != 200:
        st.error(f"Hiba történt: {weather.get('message', 'Ismeretlen hiba')}")
    else:
        #adatok
        st.subheader("Aktuális időjárás")

        col1, col2, col3 = st.columns(3)
        col1.metric("Hőmérséklet", f"{weather['main']['temp']} °C")
        col2.metric("Páratartalom", f"{weather['main']['humidity']} %")
        col3.metric("Szélsebesség", f"{weather['wind']['speed']} m/s")

        # Map
        st.subheader("Város elhelyezkedése a térképen")
        lat = weather["coord"]["lat"]
        lon = weather["coord"]["lon"]
        st.map(pd.DataFrame([[lat, lon]], columns=["lat", "lon"]))

        #5 napos előrejelzés
        st.subheader("5 napos előrejelzés")

        forecast = get_forecast(city)

        df = pd.DataFrame(forecast["list"])
        df["Dátum"] = pd.to_datetime(df["dt_txt"])
        df["Hőmérséklet"] = df["main"].apply(lambda x: x["temp"])

        fig = px.line(df, x="Dátum", y="Hőmérséklet",
                      title="Hőmérséklet előrejelzés",
                      labels={"Dátum": "Időpont", "Hőmérséklet": "Hőmérséklet (°C)"},
                      markers=True)
        fig.update_layout(xaxis_tickformat="%m-%d %H:%M", xaxis_title="Dátum", yaxis_title="Hőmérséklet (°C)")
        st.plotly_chart(fig, use_container_width=True)
