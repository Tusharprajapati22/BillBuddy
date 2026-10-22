import uuid
import calendar
import logging
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth import AuthUser, get_current_user
from backend.database import get_supabase, is_supabase_configured
from backend.models import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductStats
)

logger = logging.getLogger("billbuddy.products")
router = APIRouter(prefix="/products", tags=["Products"])

# In-memory storage fallback when Supabase credentials haven't been provided yet
_in_memory_db: dict = {}

def calculate_warranty_info(purchase_date_str: str, warranty_months: int):
    """Calculates expiry date, days remaining, and status badge."""
    try:
        p_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
    except Exception:
        p_date = date.today()

    month_index = p_date.month - 1 + int(warranty_months)
    year = p_date.year + (month_index // 12)
    month = (month_index % 12) + 1
    _, max_day = calendar.monthrange(year, month)
    day = min(p_date.day, max_day)
    expiry = date(year, month, day)

    today = date.today()
    days_rem = (expiry - today).days

    if days_rem < 0:
        badge_status = "Expired"
    elif days_rem <= 30:
        badge_status = "Expiring Soon"
    else:
        badge_status = "Active"

    return expiry.isoformat(), days_rem, badge_status


def enrich_product(p: dict) -> ProductResponse:
    """Enriches a product dictionary with computed warranty info."""
    expiry_date, days_rem, status_badge = calculate_warranty_info(
        p.get("purchase_date", str(date.today())),
        p.get("warranty_months", 12)
    )

    return ProductResponse(
        id=str(p.get("id")),
        user_id=str(p.get("user_id")),
        user_email=p.get("user_email"),
        name=p.get("name", "Product"),
        brand=p.get("brand", ""),
        category=p.get("category", "Electronics"),
        price=float(p.get("price", 0.0)),
        warranty_months=int(p.get("warranty_months", 12)),
        purchase_date=p.get("purchase_date", str(date.today())),
        emoji=p.get("emoji", "📦"),
        bill_name=p.get("bill_name"),
        bill_url=p.get("bill_url"),
        created_at=str(p.get("created_at", "")),
        warranty_expiry_date=expiry_date,
        days_remaining=days_rem,
        status=status_badge
    )


@router.get("", response_model=List[ProductResponse])
async def list_products(
    search: Optional[str] = Query(None, description="Search term for name or brand"),
    category: Optional[str] = Query(None, description="Category filter"),
    status_filter: Optional[str] = Query("all", description="all | active | expiring | expired"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    user: AuthUser = Depends(get_current_user)
):
    """List all products for the current user with optional searching and filtering."""
    sb = get_supabase()

    products_data = []

    if sb and is_supabase_configured():
        try:
            query = sb.table("products").select("*").eq("user_id", user.uid)
            if category and category != "All":
                query = query.eq("category", category)

            # Order by created_at or purchase_date desc
            query = query.order("created_at", desc=True)
            res = query.execute()
            products_data = res.data or []
        except Exception as e:
            logger.error(f"Supabase select error: {e}")
            # Fallback to in-memory
            products_data = _in_memory_db.get(user.uid, [])
    else:
        products_data = _in_memory_db.get(user.uid, [])

    # Enrich with computed warranty values
    enriched = [enrich_product(p) for p in products_data]

    # Search filter in python
    if search:
        s = search.lower()
        enriched = [
            p for p in enriched
            if s in p.name.lower() or s in p.brand.lower() or s in p.category.lower()
        ]

    # Status filter
    if status_filter == "active":
        enriched = [p for p in enriched if p.status == "Active"]
    elif status_filter == "expiring":
        enriched = [p for p in enriched if p.status == "Expiring Soon"]
    elif status_filter == "expired":
        enriched = [p for p in enriched if p.status == "Expired"]

    return enriched[offset : offset + limit]


@router.get("/stats", response_model=ProductStats)
async def get_stats(user: AuthUser = Depends(get_current_user)):
    """Computes total count, active warranties, expiring soon warranties, and total purchase value."""
    sb = get_supabase()
    products_data = []

    if sb and is_supabase_configured():
        try:
            res = sb.table("products").select("*").eq("user_id", user.uid).execute()
            products_data = res.data or []
        except Exception as e:
            logger.error(f"Supabase stats query error: {e}")
            products_data = _in_memory_db.get(user.uid, [])
    else:
        products_data = _in_memory_db.get(user.uid, [])

    enriched = [enrich_product(p) for p in products_data]

    total_products = len(enriched)
    active = sum(1 for p in enriched if p.status == "Active")
    expiring = sum(1 for p in enriched if p.status == "Expiring Soon")
    expired = sum(1 for p in enriched if p.status == "Expired")
    total_val = sum(p.price for p in enriched)

    return ProductStats(
        total_products=total_products,
        active_warranties=active,
        expiring_soon=expiring,
        expired_warranties=expired,
        total_purchase_value=round(total_val, 2)
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    user: AuthUser = Depends(get_current_user)
):
    """Add a new product with warranty details into Supabase."""
    sb = get_supabase()
    product_id = str(uuid.uuid4())
    now_iso = datetime.utcnow().isoformat()

    record = {
        "id": product_id,
        "user_id": user.uid,
        "user_email": user.email,
        "name": product_in.name.strip(),
        "brand": product_in.brand.strip(),
        "category": product_in.category,
        "price": product_in.price,
        "warranty_months": product_in.warranty_months,
        "purchase_date": product_in.purchase_date,
        "emoji": product_in.emoji or "📦",
        "bill_name": product_in.bill_name,
        "bill_url": product_in.bill_url,
        "created_at": now_iso
    }

    if sb and is_supabase_configured():
        try:
            res = sb.table("products").insert(record).execute()
            if res.data:
                record = res.data[0]
        except Exception as e:
            logger.error(f"Supabase insert error: {e}")
            # Save to in-memory fallback
            if user.uid not in _in_memory_db:
                _in_memory_db[user.uid] = []
            _in_memory_db[user.uid].insert(0, record)
    else:
        if user.uid not in _in_memory_db:
            _in_memory_db[user.uid] = []
        _in_memory_db[user.uid].insert(0, record)

    return enrich_product(record)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, user: AuthUser = Depends(get_current_user)):
    """Retrieve single product by ID."""
    sb = get_supabase()
    record = None

    if sb and is_supabase_configured():
        try:
            res = sb.table("products").select("*").eq("id", product_id).eq("user_id", user.uid).execute()
            if res.data:
                record = res.data[0]
        except Exception as e:
            logger.error(f"Supabase get product error: {e}")

    if not record:
        user_products = _in_memory_db.get(user.uid, [])
        record = next((p for p in user_products if str(p.get("id")) == product_id), None)

    if not record:
        raise HTTPException(status_code=404, detail="Product not found")

    return enrich_product(record)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    user: AuthUser = Depends(get_current_user)
):
    """Update product information."""
    sb = get_supabase()
    update_data = {k: v for k, v in product_update.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update provided")

    updated_record = None

    if sb and is_supabase_configured():
        try:
            res = sb.table("products").update(update_data).eq("id", product_id).eq("user_id", user.uid).execute()
            if res.data:
                updated_record = res.data[0]
        except Exception as e:
            logger.error(f"Supabase update error: {e}")

    if not updated_record:
        user_products = _in_memory_db.get(user.uid, [])
        for p in user_products:
            if str(p.get("id")) == product_id:
                p.update(update_data)
                updated_record = p
                break

    if not updated_record:
        raise HTTPException(status_code=404, detail="Product not found or not owned by user")

    return enrich_product(updated_record)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, user: AuthUser = Depends(get_current_user)):
    """Delete a product from Supabase."""
    sb = get_supabase()
    deleted = False

    if sb and is_supabase_configured():
        try:
            res = sb.table("products").delete().eq("id", product_id).eq("user_id", user.uid).execute()
            deleted = True
        except Exception as e:
            logger.error(f"Supabase delete error: {e}")

    user_products = _in_memory_db.get(user.uid, [])
    _in_memory_db[user.uid] = [p for p in user_products if str(p.get("id")) != product_id]

    return None
