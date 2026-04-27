# ==============================================================
# FILE: auth.py
# MỤC ĐÍCH: Xử lý toàn bộ logic Authentication
# Gồm: hash password, tạo JWT token, xác thực token
#
# ĐỌC KỸ FILE NÀY — Authentication là trái tim của bảo mật app
# ==============================================================

# passlib: thư viện hash password (bcrypt là thuật toán mạnh nhất)
from passlib.context import CryptContext

# jose: thư viện tạo và giải mã JWT token
from jose import JWTError, jwt

# datetime để set thời hạn token
from datetime import datetime, timedelta

# FastAPI tools cho authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from database import get_db
import models

# ==============================================================
# PHẦN 1: CẤU HÌNH BẢO MẬT
# ==============================================================

# SECRET_KEY: chìa khóa bí mật để ký JWT token
# QUAN TRỌNG: Trong production, đặt giá trị này vào .env file!
# Không bao giờ hardcode trong code thật!
SECRET_KEY = "blood-bank-secret-key-change-in-production-2024"

# Thuật toán mã hóa JWT — HS256 là phổ biến nhất
ALGORITHM = "HS256"

# Token có hiệu lực bao lâu (tính bằng phút)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 tiếng

# ==============================================================
# PHẦN 2: HASH PASSWORD
# ==============================================================

# CryptContext: thiết lập context để hash/verify password
# schemes=["bcrypt"] → dùng bcrypt (không thể reverse, rất an toàn)
# deprecated="auto" → tự động nâng cấp hash cũ
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """
    Chuyển password thường → password đã hash
    
    Ví dụ:
      hash_password("mypassword123")
      → "$2b$12$EixZaYVK1fsbw1ZfbX3OXe..." (không thể đọc ngược lại)
    
    TẠI SAO HASH?
      Nếu database bị hack, hacker chỉ thấy hash, không thấy password thật.
      bcrypt hash ra chuỗi khác nhau mỗi lần dù cùng input (do "salt" ngẫu nhiên).
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra password nhập vào có khớp với hash trong database không
    
    Ví dụ:
      verify_password("mypassword123", "$2b$12$EixZaYVK1fsbw1ZfbX3OXe...")
      → True (đúng password)
      
      verify_password("wrongpassword", "$2b$12$EixZaYVK1fsbw1ZfbX3OXe...")
      → False (sai password)
    """
    return pwd_context.verify(plain_password, hashed_password)

# ==============================================================
# PHẦN 3: JWT TOKEN
# ==============================================================

# JWT = JSON Web Token
# Cấu trúc: header.payload.signature (3 phần ngăn cách bởi dấu chấm)
# Ví dụ: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.abc123
#
# LUỒNG JWT:
# 1. User đăng nhập → server tạo JWT → gửi cho client
# 2. Client lưu JWT (localStorage hoặc memory)
# 3. Mỗi request, client gửi JWT trong header: "Authorization: Bearer <token>"
# 4. Server giải mã JWT → biết user là ai → xử lý request

def create_access_token(data: dict) -> str:
    """
    Tạo JWT token từ dữ liệu user
    
    data: thông tin cần lưu trong token, ví dụ: {"sub": "admin", "role": "admin"}
    "sub" = subject = định danh chính (thường là username)
    """
    # Sao chép data để không sửa dict gốc
    to_encode = data.copy()
    
    # Thêm thời gian hết hạn vào payload
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # jwt.encode() = mã hóa payload thành token string
    # SECRET_KEY + ALGORITHM → chỉ server biết cách giải mã
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """
    Giải mã JWT token → lấy lại thông tin user
    Ném lỗi nếu token invalid hoặc hết hạn
    """
    try:
        # jwt.decode() kiểm tra: chữ ký hợp lệ? Token hết hạn chưa?
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # JWTError xảy ra khi: token giả mạo, bị sửa, hoặc hết hạn
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ==============================================================
# PHẦN 4: DEPENDENCY — bảo vệ các API route
# ==============================================================

# HTTPBearer: FastAPI tool đọc token từ header
# "Authorization: Bearer eyJhbGc..."
bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency: xác thực user từ JWT token
    
    Dùng trong route như sau:
        @router.get("/protected")
        def protected_route(user = Depends(get_current_user)):
            return {"message": f"Xin chào {user.username}"}
    
    Nếu token thiếu hoặc sai → FastAPI tự trả về 401 Unauthorized
    """
    # Lấy token string từ header
    token = credentials.credentials
    
    # Giải mã token → lấy payload
    payload = decode_token(token)
    
    # Lấy username từ payload ("sub" = subject)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token không có thông tin user")
    
    # Tìm user trong database
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User không tồn tại")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản đã bị khóa")
    
    return user

def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    Dependency: yêu cầu user phải là admin
    
    Dùng cho các route chỉ admin mới được phép:
        @router.delete("/users/{id}")
        def delete_user(user = Depends(require_admin)):
            ...
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền thực hiện thao tác này"
        )
    return current_user

# ==============================================================
# TÓM TẮT LUỒNG AUTHENTICATION:
#
# ĐĂNG KÝ:
#   password thuần → hash_password() → lưu hashed vào DB
#
# ĐĂNG NHẬP:
#   nhập password → verify_password(nhập, hash_từ_DB)
#   → nếu đúng → create_access_token({"sub": username})
#   → trả token về cho client
#
# GỌI API CÓ BẢO VỆ:
#   client gửi: Authorization: Bearer <token>
#   → get_current_user() đọc token
#   → decode_token() giải mã
#   → tìm user trong DB
#   → route handler nhận được user object
# ==============================================================
