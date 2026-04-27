# ==============================================================
# FILE: routers/blood_stock.py
# MỤC ĐÍCH: Quản lý tồn kho máu theo nhóm
# ==============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from auth import get_current_user, require_admin

router = APIRouter(prefix="/stock", tags=["Blood Stock"])

# Các nhóm máu hợp lệ — dùng để khởi tạo tồn kho
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

# ==============================================================
# Khởi tạo tồn kho (gọi 1 lần khi setup)
# POST /stock/init
# ==============================================================

@router.post("/init", tags=["Blood Stock"])
def init_blood_stock(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    """
    Tạo sẵn các dòng tồn kho cho 8 nhóm máu
    Chỉ admin mới được gọi. Gọi 1 lần khi setup app.
    """
    created = []
    for bt in BLOOD_TYPES:
        # Kiểm tra xem nhóm máu này đã có trong DB chưa
        existing = db.query(models.BloodStock).filter(
            models.BloodStock.blood_type == bt
        ).first()
        
        if not existing:
            stock = models.BloodStock(blood_type=bt, units=0)
            db.add(stock)
            created.append(bt)
    
    db.commit()
    return {"message": f"Đã khởi tạo: {created}"}

# ==============================================================
# READ — Xem tất cả tồn kho
# GET /stock/
# ==============================================================

@router.get("/", response_model=List[schemas.BloodStockResponse])
def get_all_stock(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Lấy tồn kho tất cả nhóm máu"""
    return db.query(models.BloodStock).all()

# ==============================================================
# UPDATE — Cập nhật số đơn vị máu
# PUT /stock/{blood_type}
# ==============================================================

@router.put("/{blood_type}", response_model=schemas.BloodStockResponse)
def update_stock(
    blood_type: str,
    stock_data: schemas.BloodStockUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cập nhật số đơn vị máu cho 1 nhóm
    
    Ví dụ PUT /stock/O%2B với body {"units": 50}
    → Cập nhật O+ thành 50 đơn vị
    
    Lưu ý: "O+" trong URL phải encode thành "O%2B"
    """
    stock = db.query(models.BloodStock).filter(
        models.BloodStock.blood_type == blood_type
    ).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail=f"Nhóm máu {blood_type} không tìm thấy")
    
    stock.units = stock_data.units
    db.commit()
    db.refresh(stock)
    return stock
