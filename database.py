# ==============================================================
# FILE: database.py
# MỤC ĐÍCH: Kết nối Python với database SQLite
# ĐỌC FILE NÀY TRƯỚC — đây là nền tảng của mọi thứ
# ==============================================================

# SQLAlchemy là thư viện giúp Python "nói chuyện" với database
# Thay vì viết SQL thuần, ta dùng Python objects — gọi là ORM
# ORM = Object Relational Mapper
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ==============================================================
# BƯỚC 1: Chỉ định loại database và vị trí file
# ==============================================================

# DATABASE_URL = địa chỉ kết nối database
# Cú pháp: "loại_db:///đường_dẫn_file"
# sqlite:///  → dùng SQLite (lưu vào file .db, không cần cài server)
# ./bloodbank.db → file database nằm cùng thư mục với main.py
DATABASE_URL = "sqlite:///./bloodbank.db"

# ==============================================================
# BƯỚC 2: Tạo Engine — "động cơ" kết nối với database
# ==============================================================

# create_engine() = mở kết nối đến database
# connect_args={"check_same_thread": False}
#   → Chỉ cần cho SQLite: cho phép nhiều request dùng chung kết nối
#   → PostgreSQL/MySQL không cần dòng này
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ==============================================================
# BƯỚC 3: Tạo SessionLocal — "phiên làm việc" với database
# ==============================================================

# Session = một phiên làm việc với database
# Giống như mở tab mới trong trình duyệt: mỗi request có 1 session riêng
# autocommit=False → ta phải tự gọi db.commit() để lưu thay đổi
# autoflush=False  → không tự động gửi SQL trước khi commit
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==============================================================
# BƯỚC 4: Tạo Base — class cha cho tất cả các bảng
# ==============================================================

# declarative_base() tạo ra 1 class "Base"
# Tất cả các Model (bảng) sẽ kế thừa từ Base này
# Base giúp SQLAlchemy biết: "đây là class đại diện cho bảng database"
Base = declarative_base()

# ==============================================================
# BƯỚC 5: Tạo hàm get_db — cung cấp session cho mỗi API request
# ==============================================================

# Đây là hàm "dependency" — FastAPI tự động gọi nó trước mỗi route
# Mỗi request → mở 1 session mới → xử lý → đóng session
def get_db():
    db = SessionLocal()   # Mở session
    try:
        yield db          # "yield" = cho route mượn session này
        # Code trong route chạy ở đây
    finally:
        db.close()        # Dù thành công hay lỗi, vẫn đóng session

# ==============================================================
# TÓM TẮT LUỒNG:
# engine → kết nối vật lý với file .db
# SessionLocal → factory tạo ra các session
# Base → class cha của tất cả Model/bảng
# get_db() → FastAPI dùng để inject session vào mỗi route
# ==============================================================
