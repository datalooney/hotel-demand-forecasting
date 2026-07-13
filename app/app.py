import streamlit as st
from predfunc import forecast_bookings
st.set_page_config(page_title="Hotel Demand Forecasting",
                   layout= "wide")

st.title("Hotel Demand Forecating")
st.write( "Forecast hotel room bookings using trained XGBoost models.")

#---------------------#
#  SideBar            #
#---------------------#
st.sidebar.header("Forecast Settings")
start_date = st.sidebar.date_input("Forecast Start Date",value=None)
end_date = st.sidebar.date_input("Forecast End Date",value=None)

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

    #---------------------#
    #  Display Forecasts  #
    #---------------------#
    st.subheader("Forecast Results")
    st.dataframe(forecast_df, use_container_width = True)

    
    # ---------------------
    # Room Type Selector
    # ---------------------

    room = st.selectbox("Select Room Type", forecast_df["room_type"].unique())

    room_df = forecast_df[ forecast_df["room_type"] == room]

    st.subheader(f"{room} Forecast")

    st.dataframe(room_df, use_container_width=True)
    
    room = st.sidebar.selectbox(    "Room Type",    ["Deluxe", "Standard", "Suite"])
    room_df = forecast_df[ forecast_df["room_type"] == room]
    