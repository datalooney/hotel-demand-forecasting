import joblib
import pandas as pd
import numpy as np

def forecast_bookings(data_path, model1_path, model2_path, 
                      encoder_path, feature_path, start_date,end_date):
    
    # ---------------------------
    # Load artifacts
    # ---------------------------
    model1 = joblib.load(model1_path)

    model2 = joblib.load( model2_path )

    encoders = joblib.load(encoder_path)
  
    feature_cols = joblib.load(feature_path)

    # ---------------------------
    # Read source data
    # ---------------------------
    df = pd.read_excel( data_path,  skiprows=1)

    df['date'] = pd.to_datetime(df['date'])
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    history_start = start_date - pd.Timedelta(days=7)
    history_end = start_date - pd.Timedelta(days=1)
    
    history_df = df[
    (df['date'] >= history_start) &
    (df['date'] <= history_end)
    ].copy()
    
    future_dates = pd.date_range(start=start_date, end=end_date)
    
    predictions = []

    # ---------------------------
    # Event calendar
    # ---------------------------
    event_lookup = (df[['date', 'event_name', 'event_flag']].drop_duplicates())

    # ---------------------------
    # Forecast
    # ---------------------------
    for room in ['Deluxe', 'Standard', 'Suite']:

        room_hist = history_df[history_df['room_type'] == room].copy()

        history1 = room_hist['bookings'].tolist()   # For model1
        history2 = room_hist['bookings'].tolist()   # For model2

        price_history = room_hist['price_inr'].tolist()
        
        for forecast_date in future_dates:
    
            #------------------------------
            #lag features for past bookings
            #------------------------------
        
            lag_1 = history1[-1]
            lag_7 = history1[-7]
            rolling_7 = np.mean(history1[-7:])
                
            lag_1_price = history2[-1]
            lag_7_price = history2[-7]
            rolling_7_price = np.mean(history2[-7:])
            
            #------------------------------
            #lag features for past price
            #------------------------------
            price_lag_1 = price_history[-1]
            price_lag_7 = price_history[-7]
            price_rolling_7 = np.mean(price_history[-7:])
            
            #------------------------------
            # Date and Month features
            #-------------------------------

            month = forecast_date.month
            week = int(forecast_date.isocalendar().week)

            day_name = forecast_date.day_name()

        
            lookup_row = df[(df['date'] == forecast_date) &
                        (df['room_type'] == room)].iloc[0]
            is_weekend = lookup_row['is_weekend']

            room_enc = encoders['room_type'].transform([room])[0]

            day_enc = encoders['day_of_week'].transform( [day_name])[0]
            
            # --------------------
            # Event columns
            # --------------------
         
            event_row = event_lookup[event_lookup['date']==forecast_date]
        
            if len(event_row) > 0:
                event_name = event_row.iloc[0]['event_name']
            else:
                event_name = np.nan
        
            event_name_Diwali = int(event_name == 'Diwali' )

            event_name_New_Year = int(event_name == 'New Year')

            event_name_Tamil_New_Year = int(event_name == 'Tamil New Year'  )

            event_name_Valentines_Day = int(event_name == "Valentine's Day" )
            
            
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
        
            X_price = pd.DataFrame({
            'room_type':[room_enc],
            'day_of_week':[day_enc],
            'is_weekend':[is_weekend],
            'month':[month],
            'week':[week],
            'lag_1':[lag_1_price],
            'lag_7':[lag_7_price],
            'rolling_7':[rolling_7_price],
            'price_lag_1':[price_lag_1],
            'price_lag_7': [price_lag_7],
            'price_rolling_7':[price_rolling_7],
            'event_name_Diwali':[event_name_Diwali],
            'event_name_New Year':[event_name_New_Year],
            'event_name_Tamil New Year':[event_name_Tamil_New_Year],
            "event_name_Valentine's Day":[event_name_Valentines_Day]
            })

        
            pred1 = model1.predict(X)[0]
            pred2 = model2.predict(X_price)[0]
            
            final_pred = np.median( [pred1, pred2])
        
            predictions.append({
            'date': forecast_date,
            'room_type': room,
            'prediction_xgb': pred1,
            'prediction_xgb_price': pred2,
            'forecast': final_pred
            })

            # VERY IMPORTANT
            history1.append(pred1)
            history2.append(pred2)
            price_history.append(lookup_row['price_inr'])

    # ---------------------------
    # Final dataframe
    #---------------------------
    forecast_df = pd.DataFrame(predictions)

    #print("History1:",history1)
    #print("History2:",history2)
    print(forecast_df.head())

       
    return forecast_df

model1_path = "/workspaces/hotel-demand-forecasting/models/hotel_demand_xgb.pkl"
model2_path = "/workspaces/hotel-demand-forecasting/models/hotel_demand_xgb_price.pkl"
encoder_path = "/workspaces/hotel-demand-forecasting/models/label_encoders.pkl"
feature_path = "/workspaces/hotel-demand-forecasting/models/features.pkl"
hoteldata_path = "/workspaces/hotel-demand-forecasting/data/hotel_daily_booking_data_2024_2025.xlsx"
starting_date = "2025-12-02"
ending_date = "2025-12-31"

forecast_daily = forecast_bookings(data_path = hoteldata_path, model1_path = model1_path, model2_path = model2_path,
encoder_path = encoder_path, feature_path = feature_path, start_date = starting_date, end_date = ending_date)

print(forecast_daily)
