# ==============================================================
# FILE: models.py
# MỤC ĐÍCH: Định nghĩa các BẢNG trong database bằng Python
# Mỗi class = 1 bảng | Mỗi Column = 1 cột
# ==============================================================

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Import Base từ database.py — tất cả Model phải kế thừa Base
from database import Base

# ==============================================================
# BẢNG 1: User — lưu thông tin tài khoản đăng nhập
# ==============================================================

class User(Base):
    # __tablename__ = tên bảng thực tế trong database
    __tablename__ = "users"

    # PRIMARY KEY: mỗi bảng cần 1 cột ID duy nhất
    # index=True → tạo index để tìm kiếm nhanh hơn
    id = Column(Integer, primary_key=True, index=True)

    # String(100) → giới hạn tối đa 100 ký tự
    # unique=True → không cho phép 2 user có cùng username
    # nullable=False → bắt buộc phải có giá trị (NOT NULL trong SQL)
    username = Column(String(100), unique=True, nullable=False, index=True)

    email = Column(String(200), unique=True, nullable=False)

    # Lưu PASSWORD ĐÃ ĐƯỢC MÃ HÓA (hash), KHÔNG BAO GIỜ lưu plain text!
    # Xem auth.py để hiểu cách hash password
    hashed_password = Column(String(200), nullable=False)

    # Boolean: True/False — user có đang active không?
    # default=True → mặc định là active khi tạo mới
    is_active = Column(Boolean, default=True)

    # Vai trò: "admin" hoặc "staff"
    role = Column(String(50), default="staff")

    # func.now() → tự động lưu thời điểm tạo record
    created_at = Column(DateTime, default=func.now())

    # ===========================================================
    # RELATIONSHIP: liên kết với bảng Donor
    # "back_populates" = 2 chiều: User biết Donor, Donor biết User
    # ===========================================================
    # donors = relationship("Donor", back_populates="created_by_user")

# ==============================================================
# BẢNG 2: Donor — lưu thông tin người hiến máu
# ==============================================================

class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)

    # Nhóm máu: A+, A-, B+, B-, O+, O-, AB+, AB-
    blood_type = Column(String(10), nullable=False, index=True)

    phone = Column(String(20))  # nullable=True (mặc định) → có thể để trống

    city = Column(String(100))

    date_of_birth = Column(String(20))  # lưu dạng "YYYY-MM-DD"

    # ForeignKey: liên kết với bảng users.id
    # Cho biết: donor này được tạo bởi user nào
    created_by = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=func.now())

    # updated_at tự động cập nhật khi record bị sửa
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# ==============================================================
# BẢNG 3: BloodStock — lưu tồn kho máu theo nhóm
# ==============================================================

class BloodStock(Base):
    __tablename__ = "blood_stock"

    id = Column(Integer, primary_key=True, index=True)

    # unique=True → mỗi nhóm máu chỉ có 1 dòng
    blood_type = Column(String(10), unique=True, nullable=False)

    # Số đơn vị máu hiện có
    units = Column(Integer, default=0)

    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# ==============================================================
# BẢNG 4: BloodRequest — yêu cầu lấy máu từ kho
# ==============================================================

class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True, index=True)

    blood_type = Column(String(10), nullable=False)

    units_requested = Column(Integer, nullable=False)

    # Trạng thái: "pending", "approved", "rejected"
    status = Column(String(20), default="pending")

    # Tên bệnh viện/người yêu cầu
    requested_by = Column(String(200))

    note = Column(String(500))

    created_at = Column(DateTime, default=func.now())

# ==============================================================
# SQL TƯƠNG ĐƯƠNG — để hiểu SQLAlchemy tạo ra gì:
#
# CREATE TABLE users (
#     id INTEGER PRIMARY KEY,
#     username VARCHAR(100) UNIQUE NOT NULL,
#     email VARCHAR(200) UNIQUE NOT NULL,
#     hashed_password VARCHAR(200) NOT NULL,
#     is_active BOOLEAN DEFAULT TRUE,
#     role VARCHAR(50) DEFAULT 'staff',
#     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
# );
#
# CREATE TABLE donors (
#     id INTEGER PRIMARY KEY,
#     name VARCHAR(200) NOT NULL,
#     blood_type VARCHAR(10) NOT NULL,
#     phone VARCHAR(20),
#     city VARCHAR(100),
#     date_of_birth VARCHAR(20),
#     created_by INTEGER REFERENCES users(id),
#     created_at DATETIME,
#     updated_at DATETIME
# );
# ==============================================================
