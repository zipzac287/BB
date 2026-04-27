# ==============================================================
# FILE: routers/donors.py
# MỤC ĐÍCH: CRUD API cho Donors (người hiến máu)
# CRUD = Create, Read, Update, Delete
# ==============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from auth import get_current_user, require_admin

router = APIRouter(prefix="/donors", tags=["Donors"])

# ==============================================================
# READ — Lấy danh sách donors
# GET /donors/
# ==============================================================

@router.get("/", response_model=List[schemas.DonorResponse])
def get_all_donors(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # Phải đăng nhập
):
    """
    Lấy tất cả donors
    
    List[schemas.DonorResponse] = trả về mảng (danh sách) DonorResponse
    
    SQL tương đương: SELECT * FROM donors;
    """
    donors = db.query(models.Donor).all()
    return donors

# ==============================================================
# READ — Tìm donor theo nhóm máu
# GET /donors/search?blood_type=O%2B
# ==============================================================

@router.get("/search", response_model=List[schemas.DonorResponse])
def search_donors(
    blood_type: str,               # Query parameter: /donors/search?blood_type=O+
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Tìm donor theo nhóm máu
    
    SQL tương đương: SELECT * FROM donors WHERE blood_type = 'O+';
    """
    donors = db.query(models.Donor).filter(
        models.Donor.blood_type == blood_type
    ).all()
    
    return donors  # Trả về mảng rỗng [] nếu không tìm thấy

# ==============================================================
# READ — Lấy 1 donor theo ID
# GET /donors/{donor_id}
# ==============================================================

@router.get("/{donor_id}", response_model=schemas.DonorResponse)
def get_donor(
    donor_id: int,   # Path parameter: /donors/5
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    SQL tương đương: SELECT * FROM donors WHERE id = 5 LIMIT 1;
    """
    donor = db.query(models.Donor).filter(models.Donor.id == donor_id).first()
    
    if not donor:
        raise HTTPException(status_code=404, detail="Không tìm thấy donor")
    
    return donor

# ==============================================================
# CREATE — Thêm donor mới
# POST /donors/
# ==============================================================

@router.post("/", response_model=schemas.DonorResponse, status_code=201)
def create_donor(
    donor_data: schemas.DonorCreate,  # Request body (JSON)
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Tạo donor mới
    
    SQL tương đương:
    INSERT INTO donors (name, blood_type, phone, city, created_by)
    VALUES ('Nguyễn Văn A', 'O+', '0901234567', 'HCM', 1);
    """
    # model_dump() = chuyển Pydantic schema → dict
    # (trong Pydantic v1 dùng .dict(), v2 dùng .model_dump())
    new_donor = models.Donor(
        **donor_data.model_dump(),
        created_by=current_user.id  # Ghi nhận ai tạo donor này
    )
    
    db.add(new_donor)
    db.commit()
    db.refresh(new_donor)
    return new_donor

# ==============================================================
# UPDATE — Cập nhật thông tin donor
# PUT /donors/{donor_id}
# ==============================================================

@router.put("/{donor_id}", response_model=schemas.DonorResponse)
def update_donor(
    donor_id: int,
    donor_data: schemas.DonorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Cập nhật donor
    
    SQL tương đương:
    UPDATE donors SET name='...', blood_type='...' WHERE id = 5;
    """
    donor = db.query(models.Donor).filter(models.Donor.id == donor_id).first()
    
    if not donor:
        raise HTTPException(status_code=404, detail="Không tìm thấy donor")
    
    # Cập nhật từng field
    for field, value in donor_data.model_dump().items():
        setattr(donor, field, value)  # donor.name = value, v.v.
    
    db.commit()
    db.refresh(donor)
    return donor

# ==============================================================
# DELETE — Xóa donor
# DELETE /donors/{donor_id}
# ==============================================================

@router.delete("/{donor_id}", response_model=schemas.MessageResponse)
def delete_donor(
    donor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)  # Chỉ ADMIN mới xóa được!
):
    """
    Xóa donor (chỉ admin)
    
    SQL tương đương: DELETE FROM donors WHERE id = 5;
    
    Lưu ý: dùng Depends(require_admin) thay vì get_current_user
    → FastAPI tự kiểm tra role trước khi chạy code
    """
    donor = db.query(models.Donor).filter(models.Donor.id == donor_id).first()
    
    if not donor:
        raise HTTPException(status_code=404, detail="Không tìm thấy donor")
    
    db.delete(donor)
    db.commit()
    
    return {"message": f"Đã xóa donor ID {donor_id}"}
