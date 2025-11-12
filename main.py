import os
from datetime import datetime, date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents

app = FastAPI(title="UMKM Business Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "UMKM Prediction Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Data models for requests
class MetricIn(BaseModel):
    period: date
    sales: float
    orders: int
    marketing_spend: float


class PredictIn(BaseModel):
    period: date
    sales: float
    orders: int
    marketing_spend: float


class ProfileIn(BaseModel):
    owner_name: str
    business_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None


class ReportIn(BaseModel):
    title: str
    notes: Optional[str] = None
    status: str = "open"


# Simple baseline prediction logic (can be replaced later)
# Uses a naive linear combination to estimate next period sales/orders

def baseline_predict(sales: float, orders: int, marketing_spend: float):
    # coefficients tuned heuristically; replace with ML model later if desired
    predicted_sales = sales * 1.05 + marketing_spend * 0.5
    predicted_orders = int(orders * 1.03 + marketing_spend * 0.02)
    return max(0.0, predicted_sales), max(0, predicted_orders)


# Profile endpoints
@app.post("/api/profile")
def create_profile(payload: ProfileIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    profile_id = create_document("profile", payload.model_dump())
    return {"id": profile_id, "message": "Profile created"}


@app.get("/api/profile")
def get_profiles():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    items = get_documents("profile")
    # convert ObjectId to string
    for i in items:
        i["_id"] = str(i["_id"]) if "_id" in i else None
    return items


# Metrics endpoints
@app.post("/api/metrics")
def create_metric(payload: MetricIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    metric_id = create_document("metric", payload.model_dump())
    return {"id": metric_id, "message": "Metric saved"}


@app.get("/api/metrics")
def list_metrics(limit: Optional[int] = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    items = get_documents("metric", limit=limit)
    for i in items:
        i["_id"] = str(i["_id"]) if "_id" in i else None
        # format dates to iso string
        if "period" in i and isinstance(i["period"], (datetime, date)):
            i["period"] = i["period"].isoformat()
    return items


# Prediction endpoint
@app.post("/api/predict")
def predict(payload: PredictIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    psales, porders = baseline_predict(payload.sales, payload.orders, payload.marketing_spend)
    data = payload.model_dump()
    data.update({"predicted_sales": psales, "predicted_orders": porders})
    pred_id = create_document("prediction", data)
    return {"id": pred_id, "predicted_sales": psales, "predicted_orders": porders}


# Reports endpoint
@app.post("/api/reports")
def create_report(payload: ReportIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    rep_id = create_document("report", payload.model_dump())
    return {"id": rep_id, "message": "Report created"}


@app.get("/api/reports")
def list_reports(limit: Optional[int] = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    items = get_documents("report", limit=limit)
    for i in items:
        i["_id"] = str(i["_id"]) if "_id" in i else None
    return items


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
