# Predict Handwritting

โปรเจกต์นี้เป็นเว็บแอปสำหรับทำนายตัวเลขไทยที่เขียนด้วยมือ โดยผู้ใช้สามารถวาดตัวเลขบนหน้าเว็บ แล้วให้โมเดล Machine Learning ทำนายผลผ่าน API ของ FastAPI ได้ ระบบมีการเข้าสู่ระบบ เก็บประวัติการทำนาย รับข้อมูลตัวอย่างเพื่อใช้ปรับปรุงโมเดล และมีหน้าสำหรับผู้ดูแลระบบเพื่อจัดการโมเดล

## ภาพรวมของระบบ

ระบบแบ่งออกเป็น 3 ส่วนหลัก

- `frontend` เป็นหน้าเว็บแบบ HTML, CSS และ JavaScript สำหรับวาดตัวเลข ดูผลทำนาย ดูประวัติ และเข้าใช้งานหน้าผู้ดูแลระบบ
- `backend` เป็น API ที่พัฒนาด้วย FastAPI ใช้สำหรับสมัครสมาชิก เข้าสู่ระบบ ทำนายผล เก็บประวัติ และจัดการโมเดล
- `ml` เป็นส่วนของ Machine Learning สำหรับฝึกโมเดลจากชุดข้อมูลภาพ และบันทึกโมเดลเป็นไฟล์ `.keras`

โมเดลเริ่มต้นของโปรเจกต์อยู่ที่

```text
ml/models/thai_number_model.keras
```

## ความสามารถหลัก

- สมัครสมาชิกและเข้าสู่ระบบด้วย JWT
- วาดตัวเลขบนหน้าเว็บแล้วส่งไปทำนายผล
- ทำนายตัวเลขไทยจากภาพขนาด 28 x 28 พิกเซล
- บันทึกประวัติการทำนายของผู้ใช้
- ส่งข้อมูลตัวอย่างกลับเข้าระบบเพื่อใช้เป็นข้อมูลฝึกเพิ่มเติม
- ผู้ดูแลระบบสามารถดูรายการโมเดล อัปโหลดโมเดล และเปิดใช้งานโมเดลที่ต้องการได้
- รองรับการ deploy ด้วย Docker, Railway และ Render

## โครงสร้างโปรเจกต์

```text
Predict_Handwritting/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── routes/
│   │   └── utils/
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── predictor.html
│   ├── admin.html
│   └── api.js
├── ml/
│   ├── train.py
│   ├── notebooks/
│   └── models/
├── Dataset/
├── Dockerfile
├── railway.json
├── render.yaml
└── README.md
```

## สิ่งที่ต้องมีในเครื่อง

- Python 3.10 ขึ้นไป
- pip
- Git

ถ้าต้องการฝึกโมเดลใหม่ ควรมีพื้นที่และหน่วยความจำเพียงพอสำหรับ TensorFlow

## วิธีติดตั้งและรันโปรเจกต์

เริ่มจาก clone โปรเจกต์และเข้าไปที่โฟลเดอร์

```bash
git clone https://github.com/ThanaPRCPK2547/Predict_Handwritting.git
cd Predict_Handwritting
```

สร้าง virtual environment

```bash
python -m venv .venv
```

เปิดใช้งาน virtual environment

สำหรับ macOS หรือ Linux

```bash
source .venv/bin/activate
```

สำหรับ Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

ติดตั้ง dependencies

```bash
pip install -r backend/requirements.txt
```

รันเซิร์ฟเวอร์

```bash
uvicorn backend.app.main:app --reload --port 8000
```

จากนั้นเปิดเว็บได้ที่

```text
http://localhost:8000
```

เอกสาร API เปิดดูได้ที่

```text
http://localhost:8000/docs
```

## การตั้งค่า Environment Variables

โปรเจกต์อ่านค่าจากไฟล์ `.env` ที่ root ของโปรเจกต์ ถ้าไม่มีไฟล์นี้ ระบบยังรันได้ด้วยค่าเริ่มต้น แต่สำหรับการใช้งานจริงควรกำหนดค่าเอง

ตัวอย่าง

```env
SECRET_KEY=เปลี่ยนเป็นค่าสุ่มที่ปลอดภัย
DATABASE_URL=sqlite:///./thai_digit.db
MODEL_PATH=ml/models/thai_number_model.keras
```

คำอธิบาย

- `SECRET_KEY` ใช้สำหรับสร้างและตรวจสอบ JWT
- `DATABASE_URL` ใช้กำหนดตำแหน่งฐานข้อมูล ค่าเริ่มต้นเป็น SQLite
- `MODEL_PATH` ใช้กำหนด path ของโมเดลที่ต้องการโหลด

สามารถสร้าง `SECRET_KEY` ได้ด้วยคำสั่งนี้

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## การใช้งาน

เมื่อเปิดเว็บครั้งแรก ให้สมัครสมาชิกผ่านหน้า login/register จากนั้นเข้าสู่ระบบแล้วไปที่หน้าทำนายผล ผู้ใช้สามารถวาดตัวเลขบน canvas แล้วส่งไปให้ระบบทำนายได้

ถ้าต้องการใช้งานหน้าผู้ดูแลระบบ ต้องสมัครหรือสร้างผู้ใช้ที่มี role เป็น `admin` เพราะ endpoint สำหรับจัดการโมเดลจะตรวจสอบสิทธิ์ผู้ใช้ก่อนทุกครั้ง

## API ที่สำคัญ

| Method | Path | คำอธิบาย |
| --- | --- | --- |
| `POST` | `/register` | สมัครสมาชิก |
| `POST` | `/login` | เข้าสู่ระบบและรับ access token |
| `POST` | `/predict` | ส่งข้อมูลภาพเพื่อทำนายตัวเลข |
| `POST` | `/train` | ส่งข้อมูลตัวอย่างพร้อม label ที่ถูกต้อง |
| `GET` | `/predictions/history` | ดูประวัติการทำนายของผู้ใช้ |
| `GET` | `/admin/models` | ดูรายการโมเดลทั้งหมด |
| `POST` | `/admin/models/upload` | อัปโหลดโมเดลใหม่ |
| `POST` | `/admin/models/activate/{model_id}` | เปิดใช้งานโมเดลที่เลือก |
| `GET` | `/admin/stats` | ดูสถิติการใช้งาน |

API ส่วนใหญ่ต้องส่ง token ใน header

```text
Authorization: Bearer <access_token>
```

## การฝึกโมเดลใหม่

ชุดข้อมูลสำหรับฝึกโมเดลอยู่ในโฟลเดอร์ `Dataset` โดยสคริปต์ `ml/train.py` จะอ่านข้อมูลจากโฟลเดอร์ตัวเลข `10` ถึง `15` แล้ว map เป็น label ภายในสำหรับการฝึกโมเดล

ติดตั้ง dependencies ที่จำเป็นสำหรับงานฝึกโมเดล

```bash
pip install -r backend/requirements.txt
pip install opencv-python scikit-learn
```

รันคำสั่งฝึกโมเดล

```bash
python ml/train.py
```

เมื่อฝึกเสร็จ โมเดลจะถูกบันทึกที่

```text
ml/models/thai_number_model.keras
```

## การรันด้วย Docker

สร้าง image

```bash
docker build -t predict-handwritting .
```

รัน container

```bash
docker run -p 8000:8000 predict-handwritting
```

เปิดเว็บที่

```text
http://localhost:8000
```

## การ Deploy

โปรเจกต์มีไฟล์สำหรับ deploy อยู่แล้ว

- `Dockerfile` สำหรับ build และรันแอปด้วย Docker
- `railway.json` สำหรับ deploy บน Railway โดยใช้ Dockerfile
- `render.yaml` สำหรับ deploy บน Render
- `nixpacks.toml` สำหรับสภาพแวดล้อมที่ใช้ Nixpacks

ในการ deploy จริงควรกำหนด `SECRET_KEY` และ `DATABASE_URL` ในระบบ environment variables ของ platform ที่ใช้งาน

## หมายเหตุ

- ชื่อ repository ใช้คำว่า `Handwritting` ตามชื่อโปรเจกต์เดิม
- ฐานข้อมูลเริ่มต้นเป็น SQLite และจะถูกสร้างอัตโนมัติเมื่อรัน backend
- ถ้าไฟล์โมเดลหาย ระบบจะไม่สามารถทำนายผลได้ ต้องมีไฟล์ `.keras` ตาม path ที่กำหนดไว้
- ค่า `SECRET_KEY` เริ่มต้นในโค้ดเหมาะสำหรับการทดสอบเท่านั้น ไม่ควรใช้ในการ deploy จริง
