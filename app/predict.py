import joblib
import pandas as pd
import numpy as np

# ---------------------------
# Load artifacts
# ---------------------------
model1 = joblib.load(
    "/workspaces/hotel-demand-forecasting/models/hotel_demand_xgb.pkl"
)

model2 = joblib.load(
    "/workspaces/hotel-demand-forecasting/models/hotel_demand_xgb_price.pkl"
)

encoders = joblib.load(
    "/workspaces/hotel-demand-forecasting/models/label_encoders.pkl"
)

feature_cols = joblib.load(
    "/workspaces/hotel-demand-forecasting/models/features.pkl"
)

# ---------------------------
# Read source data
# ---------------------------
df = pd.read_excel(
    "/workspaces/hotel-demand-forecasting/data/hotel_daily_booking_data_2024_2025.xlsx",
    skiprows=1
)

df['date'] = pd.to_datetime(df['date'])

# ---------------------------
# History window
# ---------------------------
history_df = df[
    (df['date'] >= '2025-11-25') &
    (df['date'] <= '2025-12-01')
].copy()

# ---------------------------
# Future dates
# ---------------------------
future_dates = pd.date_range(
    start='2025-12-02',
    end='2025-12-31'
)

predictions = []

# ---------------------------
# Event calendar
# ---------------------------
event_lookup = (
    df[['date', 'event_name', 'event_flag']]
    .drop_duplicates()
)

# ---------------------------
# Forecast
# ---------------------------

X_df = []
for room in ['Deluxe', 'Standard', 'Suite']:

    room_hist = history_df[
        history_df['room_type'] == room
    ].copy()

    history = room_hist['bookings'].tolist()

    for forecast_date in future_dates:
    
        #------------------------------
        #lag features for past bookings
        #------------------------------
        
        lag_1 = history[-1]
        lag_7 = history[-7]
        rolling_7 = np.mean(history[-7:])
        
        #------------------------------
        # Date and Month features
        #-------------------------------

        month = forecast_date.month
        week = int(forecast_date.isocalendar().week)

        day_name = forecast_date.day_name()

        
        lookup_row = df[(df['date'] == forecast_date) &
                        (df['room_type'] == room)].iloc[0]
        is_weekend = lookup_row['is_weekend']

        room_enc = encoders['room_type'].transform(
            [room]
        )[0]

        day_enc = encoders['day_of_week'].transform(
            [day_name]
        )[0]
       
        # --------------------
        # Event columns
        # --------------------
         
        event_row = event_lookup[event_lookup['date']==forecast_date]
        
        if len(event_row) > 0:
            event_name = event_row.iloc[0]['event_name']
        else:
            event_name = np.nan
        
        event_name_Diwali = int(
            event_name == 'Diwali'
        )

        event_name_New_Year = int(
            event_name == 'New Year'
        )

        event_name_Tamil_New_Year = int(
            event_name == 'Tamil New Year'
        )

        event_name_Valentines_Day = int(
            event_name == "Valentine's Day"
        )

        # --------------------
        # Build row
        # --------------------

        X = pd.DataFrame({
            'room_type':[room_enc],
            'day_of_week':[day_enc],
            'is_weekend':[is_weekend],
            'month':[month],
            'week':[week],
            'lag_1':[lag_1],
            'lag_7':[lag_7],
            'rolling_7':[rolling_7],
            'event_name_Diwali':[event_name_Diwali],
            'event_name_New Year':[event_name_New_Year],
            'event_name_Tamil New Year':[event_name_Tamil_New_Year],
            "event_name_Valentine's Day":[event_name_Valentines_Day]
        })

        # Ensure same order as training
        features = ['room_type', 'day_of_week','is_weekend','month',
            'week', 'lag_1','lag_7','rolling_7', 'event_name_Diwali',
            'event_name_New Year','event_name_Tamil New Year',
            "event_name_Valentine's Day"]
        X = X[features]
        #X_df.append(X.T)
        pred1 = model1.predict(X)[0]

        #pred2 = model2.predict(X)[0]

        #final_pred = np.median( [pred1, pred2])
        
        predictions.append({
            'date': forecast_date,
            'room_type': room,
            'prediction_xgb': pred1})
            #'prediction_xgb_price': pred2,
            #'forecast': final_pred
        #})

        # VERY IMPORTANT
        history.append(pred1)

# ---------------------------
# Final dataframe
# ---------------------------
forecast_df = pd.DataFrame(predictions)
#Xdf = pd.DataFrame(X_df)
print(history)
print(forecast_df.head())