import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title = "Hotel Demand Forecasting",
layout = "wide")

st.title("Hotel Demand Forecasting (FastAPI)")
st.write("Forecast hotel bookings using FastAPI backend")

#-----------------------
#Sidebar
#-----------------------

st.sidebar.header("Forecast Settings")

MIN_DATE = pd.to_datetime("2025-12-02").date()
MAX_DATE = pd.to_datetime("2025-12-31").date()

start_date = st.sidebar.date_input(
"Forecast Start Date",
value = None,
min_value = MIN_DATE,
max_value = MAX_DATE
)


end_date = st.sidebar.date_input(
"Forecast End Date",
value = MAX_DATE,
min_value = start_date,
max_value = MAX_DATE
)


room = st.sidebar.selectbox(
"Room Type",["All Rooms", "Deluxe", "Standard", "Suite"]
)

predict = st.sidebar.button("Generate Forecast")

#-----------------------------
#Call FastAPI
#-----------------------------
if predict:
    url = "http://127.0.0.1:8000/forecast"
    
    payload = {
    "start_date": str(start_date),
    "end_date": str(end_date)
    }
    
    with st.spinner("Calling FastAPI..."):
        response = requests.post(url, json=payload)
        
    if response.status_code != 200:
    
        st.error("API Error")
        st.write(response.text)
        st.stop()
        
    forecast_df = pd.DataFrame(response.json())
    
    forecast_df["date"] = pd.to_datetime(forecast_df["date"])
    
    st.success("Forecast received from FastAPI!")
    
    # -----------------------------
    # Filter room
    # -----------------------------

    if room == "All Rooms":

        display_df = forecast_df

    else:

        display_df = forecast_df[
            forecast_df["room_type"] == room
        ]

    # -----------------------------
    # Table
    # -----------------------------

    st.subheader("Forecast Results")

    st.dataframe(
        display_df,
        use_container_width=True
    )
    
     # Plot
    # -----------------------------

    st.subheader("Forecast Plot")

    if room == "All Rooms":

        fig = px.line(
            display_df,
            x="date",
            y="forecast",
            color="room_type",
            markers=True,
            title="Forecast by Room Type"
        )

    else:

        fig = px.line(
            display_df,
            x="date",
            y="forecast",
            markers=True,
            title=f"{room} Forecast"
        )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Forecast Bookings",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


