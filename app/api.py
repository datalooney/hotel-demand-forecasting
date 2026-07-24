from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from predfunc import forecast_bookings


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "hotel_daily_booking_data_2024_2025.xlsx"
MODEL1_PATH = BASE_DIR / "models" / "hotel_demand_xgb.pkl"
MODEL2_PATH = BASE_DIR / "models" / "hotel_demand_xgb_price.pkl"
ENCODER_PATH = BASE_DIR / "models" / "label_encoders.pkl"
FEATURE_PATH = BASE_DIR / "models" / "features.pkl"


app = FastAPI(
    title="Hotel Demand Forecast API",
    version="1.0"
)


class ForecastRequest(BaseModel):
    start_date: str
    end_date: str


@app.get("/")
def home():
    return {
        "message": "Hotel Demand Forecast API is running"
    }


@app.post("/forecast")
def forecast(request: ForecastRequest):

    forecast_df = forecast_bookings(
        data_path=DATA_PATH,
        model1_path=MODEL1_PATH,
        model2_path=MODEL2_PATH,
        encoder_path=ENCODER_PATH,
        feature_path=FEATURE_PATH,
        start_date=request.start_date,
        end_date=request.end_date
    )

    return forecast_df.to_dict(orient="records")