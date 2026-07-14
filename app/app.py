import streamlit as st
from predfunc import forecast_bookings
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Hotel Demand Forecasting",
                   layout= "wide")

st.title("Hotel Demand Forecating")
st.write( "Forecast hotel room bookings using trained XGBoost models.")

#---------------------#
#  SideBar            #
#---------------------#
st.sidebar.header("Forecast Settings")

start_date = st.sidebar.date_input(
    "Forecast Start Date",
    value=None)

end_date = st.sidebar.date_input(
    "Forecast End Date",
    value=None)

room = st.sidebar.selectbox(
    "Room Type",
    ["All Rooms", "Deluxe", "Standard", "Suite"]
)


#--------------------#
#       Predict      #
# -------------------#  
predict = st.sidebar.button("Generate Forecast")

#--------------------#
#   Call Function    #
#--------------------#
if predict:

    with st.spinner("Generating forecasts..."):

        forecast_df = forecast_bookings(
            data_path= "/workspaces/hotel-demand-forecasting/data/hotel_daily_booking_data_2024_2025.xlsx",
            model1_path="/workspaces/hotel-demand-forecasting/models/hotel_demand_xgb.pkl",
            model2_path="/workspaces/hotel-demand-forecasting/models/hotel_demand_xgb_price.pkl",
            encoder_path="/workspaces/hotel-demand-forecasting/models/label_encoders.pkl",
            feature_path="/workspaces/hotel-demand-forecasting/models/features.pkl",
            start_date=start_date,
            end_date=end_date
        )

    st.success("Forecast Complete!")

      
    # ---------------------
    # Room Type Selector
    # ---------------------

    
    if room == "All Rooms":
        display_df = forecast_df.copy()
    else:
        display_df = forecast_df[
        forecast_df["room_type"] == room]

    st.subheader("Forecast Results")
    st.dataframe(display_df, use_container_width=True)
    
    st.subheader("Forecast Plot")

    if room == "All Rooms":
        fig = px.line(
        display_df,
        x="date",
        y="forecast",
        color="room_type",
        markers=True,
        title="Forecasted Bookings by Room Type"
        )

        fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Forecast Bookings",
        hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

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

        st.plotly_chart(fig, use_container_width=True)