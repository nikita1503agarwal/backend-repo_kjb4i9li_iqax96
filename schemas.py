"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

# Example domain for UMKM (small business) prediction app

class Profile(BaseModel):
    """
    Business profile schema
    Collection name: "profile"
    """
    owner_name: str = Field(..., description="Owner full name")
    business_name: str = Field(..., description="Business name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")
    address: Optional[str] = Field(None, description="Business address")
    industry: Optional[str] = Field(None, description="Business industry type")

class Metric(BaseModel):
    """
    Daily/Monthly metrics captured for dashboard monitoring
    Collection name: "metric"
    """
    period: date = Field(..., description="Date representing the period (e.g., first day of month)")
    sales: float = Field(..., ge=0, description="Sales revenue for period")
    orders: int = Field(..., ge=0, description="Total orders")
    marketing_spend: float = Field(..., ge=0, description="Marketing spend")

class Prediction(BaseModel):
    """
    Prediction inputs and outputs
    Collection name: "prediction"
    """
    period: date = Field(..., description="Target period for prediction")
    sales: float = Field(..., ge=0, description="Recent sales reference")
    orders: int = Field(..., ge=0, description="Recent orders reference")
    marketing_spend: float = Field(..., ge=0, description="Planned marketing budget")
    predicted_sales: Optional[float] = Field(None, ge=0, description="Predicted sales output")
    predicted_orders: Optional[int] = Field(None, ge=0, description="Predicted orders output")

class Report(BaseModel):
    """
    Monitoring report entries
    Collection name: "report"
    """
    title: str = Field(..., description="Report title")
    notes: Optional[str] = Field(None, description="Observation notes")
    status: str = Field("open", description="Status of the item: open, in_progress, done")

# Keep example schemas for reference (not used by the app directly)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
