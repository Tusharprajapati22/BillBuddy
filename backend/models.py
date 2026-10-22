from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, example="Samsung Galaxy S25")
    brand: str = Field(..., min_length=1, max_length=80, example="Samsung")
    category: str = Field("Electronics", example="Mobile")
    price: float = Field(..., ge=0, example=74999.0)
    warranty_months: int = Field(12, ge=0, le=600, example=12)
    purchase_date: str = Field(..., example="2025-01-15")
    emoji: Optional[str] = Field("📦", example="📱")
    bill_name: Optional[str] = Field(None, example="galaxy_s25_invoice.pdf")
    bill_url: Optional[str] = Field(None, example="https://xyz.supabase.co/storage/v1/object/public/bills/...")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    warranty_months: Optional[int] = None
    purchase_date: Optional[str] = None
    emoji: Optional[str] = None
    bill_name: Optional[str] = None
    bill_url: Optional[str] = None

class ProductResponse(ProductBase):
    id: str
    user_id: str
    user_email: Optional[str] = None
    created_at: Optional[str] = None
    # Computed fields for convenience
    warranty_expiry_date: Optional[str] = None
    days_remaining: Optional[int] = None
    status: Optional[str] = None  # "Active", "Expiring Soon", "Expired"

    class Config:
        from_attributes = True

class ProductStats(BaseModel):
    total_products: int = 0
    active_warranties: int = 0
    expiring_soon: int = 0
    expired_warranties: int = 0
    total_purchase_value: float = 0.0

class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    public_url: str
    file_size: int
    content_type: str

class UserProfile(BaseModel):
    uid: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
