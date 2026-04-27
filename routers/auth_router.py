# ==============================================================
# FILE: routers/auth_router.py
# MỤC ĐÍCH: Các API endpoint cho Đăng ký / Đăng nhập
# ==============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import hash_password, verify_password, create_access_token, get_current_user

# APIRouter = mini-app chứa nhóm các route liên quan
# prefix="/auth" → tất cả route trong file này bắt đầu bằng /auth
# tags=["Auth"] → nhóm hiển thị trong /docs
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==============================================================
# ROUTE 1: Đăng ký tài khoản
# POST /auth/register
# ==============================================================

@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản mới
    
    Client gửi lên (JSON body):
    {
        "username": "admin",
        "email": "admin@bloodbank.com",
        "password": "secret123"
    }
    
    Server trả về: thông tin user (KHÔNG có password)
    """
    
    # BƯỚC 1: Kiểm tra username đã tồn tại chưa
    # db.query(Model) = "SELECT * FROM users"
    # .filter() = "WHERE username = ?"
    # .first() = lấy 1 kết quả đầu tiên (hoặc None)
    existing_user = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    
    if existing_user:
        # HTTPException = lỗi có HTTP status code
        # 400 Bad Request = client gửi dữ liệu không hợp lệ
        raise HTTPException(
            status_code=400,
            detail="Username đã được sử dụng"
        )
    
    # BƯỚC 2: Kiểm tra email đã tồn tại chưa
    existing_email = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    
    if existing_email:
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")
    
    # BƯỚC 3: Hash password trước khi lưu
    # KHÔNG BAO GIỜ lưu plain text password!
    hashed_pw = hash_password(user_data.password)
    
    # BƯỚC 4: Tạo user object
    # **user_data.dict() = unpack dict: username=..., email=...
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        role="staff"  # Mặc định là staff, chỉ admin mới có thể đổi
    )
    
    # BƯỚC 5: Lưu vào database
    db.add(new_user)    # Thêm vào session (chưa lưu thật)
    db.commit()         # Commit → lưu vào file .db thật sự
    db.refresh(new_user)  # Refresh để lấy id, created_at được server tạo
    
    return new_user

# ==============================================================
# ROUTE 2: Đăng nhập
# POST /auth/login
# ==============================================================

@router.post("/login", response_model=schemas.TokenResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Đăng nhập → nhận JWT token
    
    Client gửi lên:
    {
        "username": "admin",
        "password": "secret123"
    }
    
    Server trả về:
    {
        "access_token": "eyJhbGc...",
        "token_type": "bearer",
        "user": { "id": 1, "username": "admin", ... }
    }
    """
    
    # BƯỚC 1: Tìm user theo username
    user = db.query(models.User).filter(
        models.User.username == login_data.username
    ).first()
    
    # BƯỚC 2: Kiểm tra user tồn tại VÀ password đúng
    # Lưu ý: không nói rõ "sai username" hay "sai password"
    # → tránh kẻ xấu biết username có tồn tại hay không
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username hoặc password không đúng"
        )
    
    # BƯỚC 3: Kiểm tra tài khoản còn active không
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản đã bị khóa")
    
    # BƯỚC 4: Tạo JWT token
    # "sub" (subject) = định danh chính trong token
    token = create_access_token(data={
        "sub": user.username,
        "role": user.role
    })
    
    # BƯỚC 5: Trả về token + thông tin user
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

# ==============================================================
# ROUTE 3: Lấy thông tin user hiện tại (cần đăng nhập)
# GET /auth/me
# ==============================================================

@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Lấy thông tin của user đang đăng nhập
    
    Client gửi: Authorization: Bearer <token> trong header
    Server tự giải mã token và trả về thông tin user
    
    Route này dùng Depends(get_current_user):
    → FastAPI tự động xác thực token trước khi chạy code này
    → Nếu token sai/hết hạn → trả về 401 tự động
    """
    return current_user
