# ==============================================================
# FILE: main.py
# MỤC ĐÍCH: Điểm khởi đầu của toàn bộ app — chạy file này!
# Lệnh chạy: uvicorn main:app --reload
# ==============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import engine và Base để tạo bảng
from database import engine
import models

# Import các router
from routers import auth_router, donors, blood_stock

# ==============================================================
# BƯỚC 1: Tạo tất cả bảng trong database
# ==============================================================

# create_all() kiểm tra file .db:
#   - Nếu bảng chưa có → tạo mới
#   - Nếu đã có → giữ nguyên (không xóa data)
# checkfirst=True → không báo lỗi nếu bảng đã tồn tại
models.Base.metadata.create_all(bind=engine)

# ==============================================================
# BƯỚC 2: Tạo FastAPI app
# ==============================================================

app = FastAPI(
    title="Blood Bank API",
    description="API quản lý ngân hàng máu với authentication",
    version="1.0.0",
    # docs_url="/docs" → Swagger UI (mặc định)
    # redoc_url="/redoc" → ReDoc UI (mặc định)
)

# ==============================================================
# BƯỚC 3: CORS Middleware
# ==============================================================

# CORS = Cross-Origin Resource Sharing
# Browser chặn: webpage ở localhost:5500 gọi API ở localhost:8000
# (vì khác "origin" = khác port)
# → Ta phải cho phép điều này qua CORS middleware

app.add_middleware(
    CORSMiddleware,
    # allow_origins: danh sách domain được phép gọi API
    # ["*"] = cho phép tất cả (chỉ dùng trong development!)
    # Production: ["https://myapp.com", "https://www.myapp.com"]
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # GET, POST, PUT, DELETE, OPTIONS...
    allow_headers=["*"],   # Authorization, Content-Type...
)

# ==============================================================
# BƯỚC 4: Mount thư mục frontend
# ==============================================================

# StaticFiles phục vụ file HTML/CSS/JS tĩnh
# /static → URL prefix
# directory="frontend" → thư mục chứa file
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ==============================================================
# BƯỚC 5: Đăng ký các Router
# ==============================================================

# include_router() = "gắn" router vào app chính
# Tất cả route trong router sẽ có prefix của router đó
app.include_router(auth_router.router)    # /auth/...
app.include_router(donors.router)          # /donors/...
app.include_router(blood_stock.router)     # /stock/...

# ==============================================================
# BƯỚC 6: Route gốc — kiểm tra server đang chạy
# ==============================================================

@app.get("/")
def root():
    return {
        "message": "🩸 Blood Bank API đang chạy!",
        "docs": "Truy cập /docs để xem API documentation",
        "version": "1.0.0"
    }

# ==============================================================
# CHẠY APP:
#
# 1. Cài thư viện:
#    pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-jose[cryptography]
#
# 2. Chạy server:
#    uvicorn main:app --reload
#    (--reload = tự restart khi code thay đổi)
#
# 3. Mở trình duyệt:
#    http://localhost:8000/docs  → Swagger UI (test API)
#    http://localhost:8000/static/index.html → Frontend
#
# LUỒNG TEST NHANH QUA /docs:
#   1. POST /auth/register → tạo tài khoản
#   2. POST /auth/login → nhận token
#   3. Click "Authorize" → dán token vào
#   4. Thử các API khác
# ==============================================================
