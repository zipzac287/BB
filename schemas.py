# ==============================================================
# FILE: schemas.py
# MỤC ĐÍCH: Định nghĩa "hình dạng" dữ liệu vào/ra của API
# Pydantic tự động validate (kiểm tra) dữ liệu cho ta
# ==============================================================

# Pydantic = thư viện kiểm tra dữ liệu
# BaseModel = class cha của tất cả schema
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

# ==============================================================
# HIỂU VỀ SCHEMA PATTERN:
#
# Thường mỗi entity có 3 schema:
#   1. XxxBase   → các field chung (dùng để kế thừa)
#   2. XxxCreate → data CLIENT gửi lên (tạo mới)
#   3. XxxResponse → data SERVER trả về (thêm id, created_at...)
#
# Tại sao phân biệt? Vì:
#   - Client không gửi "id" (server tự tạo)
#   - Client không gửi "created_at" (server tự gán)
#   - Server không trả về "hashed_password" (bảo mật)
# ==============================================================

# ==============================================================
# SCHEMAS CHO USER
# ==============================================================

class UserBase(BaseModel):
    username: str
    email: str   # Pydantic tự validate đúng format email

class UserCreate(UserBase):
    # Thêm password khi tạo user mới
    # "password" thuần — server sẽ hash trước khi lưu
    password: str

    # Validator tùy chỉnh: kiểm tra độ dài password
    @validator("password")
    def password_must_be_strong(cls, v):
        if len(v) < 6:
            raise ValueError("Password phải có ít nhất 6 ký tự")
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: str
    created_at: Optional[datetime] = None

    # Config.from_attributes = True:
    #   Cho phép Pydantic đọc dữ liệu từ SQLAlchemy object
    #   (không phải dict thuần, mà là object có .id, .username...)
    class Config:
        from_attributes = True

# ==============================================================
# SCHEMAS CHO AUTHENTICATION (Đăng nhập)
# ==============================================================

class LoginRequest(BaseModel):
    # Data client gửi khi đăng nhập
    username: str
    password: str

class TokenResponse(BaseModel):
    # Data server trả về sau khi đăng nhập thành công
    access_token: str         # JWT token — client lưu cái này
    token_type: str = "bearer"  # Luôn là "bearer" theo chuẩn OAuth2
    user: UserResponse        # Thông tin user luôn

# ==============================================================
# SCHEMAS CHO DONOR
# ==============================================================

class DonorBase(BaseModel):
    name: str
    blood_type: str
    phone: Optional[str] = None   # Optional = không bắt buộc
    city: Optional[str] = None
    date_of_birth: Optional[str] = None

    # Validator: kiểm tra nhóm máu hợp lệ
    @validator("blood_type")
    def validate_blood_type(cls, v):
        valid = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        if v not in valid:
            raise ValueError(f"Nhóm máu phải là một trong: {valid}")
        return v

class DonorCreate(DonorBase):
    pass  # Không thêm gì — dùng y chang DonorBase

class DonorResponse(DonorBase):
    id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==============================================================
# SCHEMAS CHO BLOOD STOCK
# ==============================================================

class BloodStockResponse(BaseModel):
    id: int
    blood_type: str
    units: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BloodStockUpdate(BaseModel):
    # Khi cập nhật tồn kho, chỉ cần gửi số đơn vị mới
    units: int

# ==============================================================
# SCHEMAS CHO BLOOD REQUEST
# ==============================================================

class BloodRequestCreate(BaseModel):
    blood_type: str
    units_requested: int
    requested_by: Optional[str] = None
    note: Optional[str] = None

    @validator("units_requested")
    def units_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Số đơn vị phải lớn hơn 0")
        return v

class BloodRequestResponse(BloodRequestCreate):
    id: int
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==============================================================
# SCHEMA CHUNG CHO THÔNG BÁO LỖI / THÀNH CÔNG
# ==============================================================

class MessageResponse(BaseModel):
    message: str  # {"message": "Đã xóa thành công"}
