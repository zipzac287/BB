# 🩸 Blood Bank App — Hướng dẫn học từng bước

## Cấu trúc thư mục

```
blood-bank/
│
├── database.py        ← ĐỌC TRƯỚC TIÊN: kết nối DB
├── models.py          ← Định nghĩa các bảng SQL
├── schemas.py         ← Validate dữ liệu vào/ra
├── auth.py            ← Hash password + JWT token
│
├── routers/
│   ├── auth_router.py ← API đăng ký / đăng nhập
│   ├── donors.py      ← CRUD donors
│   └── blood_stock.py ← Quản lý tồn kho
│
├── main.py            ← Điểm khởi đầu, chạy file này
├── requirements.txt   ← Danh sách thư viện
│
└── frontend/
    └── index.html     ← Toàn bộ frontend (HTML+CSS+JS)
```

---

## Thứ tự đọc code (quan trọng!)

1. `database.py` — hiểu engine, session, Base
2. `models.py`  — hiểu cách định nghĩa bảng
3. `schemas.py` — hiểu Pydantic validate
4. `auth.py`    — hiểu hash password + JWT
5. `routers/auth_router.py` — API login/register
6. `routers/donors.py`      — CRUD có bảo vệ
7. `main.py`    — ghép tất cả lại
8. `frontend/index.html` — học fetch() + DOM

---

## Cài đặt & Chạy

```bash
# 1. Tạo virtual environment
python -m venv venv
source venv/bin/activate     # Mac/Linux
# venv\Scripts\activate      # Windows

# 2. Cài thư viện
pip install -r requirements.txt

# 3. Chạy server
uvicorn main:app --reload

# 4. Mở trình duyệt
# API docs: http://localhost:8000/docs
# Frontend: http://localhost:8000/static/index.html
```

---

## Thứ tự test (qua /docs)

1. **POST /auth/register** — tạo tài khoản admin
   ```json
   { "username": "admin", "email": "admin@test.com", "password": "123456" }
   ```

2. **POST /auth/login** — đăng nhập, copy token
   ```json
   { "username": "admin", "password": "123456" }
   ```

3. Click **"Authorize"** → dán token vào

4. **POST /stock/init** — khởi tạo tồn kho 8 nhóm máu

5. **GET /stock/** — xem tồn kho

6. **POST /donors/** — thêm donor

7. **GET /donors/** — xem danh sách

---

## Kiến thức đạt được sau dự án này

| Chủ đề | Học được |
|--------|----------|
| SQL | Tạo bảng, quan hệ FK, CRUD |
| SQLAlchemy ORM | Model, Session, Query |
| FastAPI | Router, Dependency, HTTPException |
| Pydantic | Schema, Validator |
| Authentication | Password hash (bcrypt), JWT |
| HTML/JS | fetch API, async/await, DOM |
| HTTP | Status codes, Headers, CORS |

---

## Các lỗi thường gặp

### Lỗi CORS
```
Access-Control-Allow-Origin missing
```
→ Kiểm tra CORSMiddleware trong main.py

### Lỗi 401 Unauthorized
```
Token không hợp lệ hoặc đã hết hạn
```
→ Đăng nhập lại để lấy token mới

### Lỗi 422 Unprocessable Entity
```
field required / value is not valid
```
→ Kiểm tra format JSON gửi lên có đúng schema không

### Frontend không gọi được API
→ Đảm bảo server đang chạy: `uvicorn main:app --reload`
→ Kiểm tra API_URL trong index.html có khớp port không

---

## Bước tiếp theo (nâng cao)

- [ ] Thêm bảng `BloodRequest` (yêu cầu máu từ bệnh viện)
- [ ] Admin panel quản lý users (đổi role, khóa tài khoản)
- [ ] Tìm kiếm donor theo thành phố + nhóm máu
- [ ] Refresh token (tự động gia hạn)
- [ ] Chuyển SQLite → PostgreSQL
- [ ] Deploy lên Railway/Render (miễn phí)
