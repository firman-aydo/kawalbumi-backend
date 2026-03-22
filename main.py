from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from db import SessionLocal, engine, Base
import models
import shutil
import os

# buat folder uploads kalau belum ada
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# buat tabel database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- TAMBAHAN: CORS Middleware ---
# Mengizinkan aplikasi mobile untuk menembak API tanpa diblokir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- TAMBAHAN: Akses Folder Uploads ---
# Agar foto bisa dibuka di aplikasi mobile dengan URL: http://<ip-laptop>:8000/uploads/namafoto.jpg
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# endpoint utama
@app.get("/")
def home():
    return {"message": "API SmartWaste jalan!"}

# 🔥 POST laporan (kirim laporan + simpan foto)
@app.post("/report")
async def create_report(
    photo: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    db = SessionLocal()

    # simpan file ke folder uploads
    file_location = f"uploads/{photo.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    # simpan ke database
    new_report = models.Report(
        filename=file_location,
        latitude=latitude,
        longitude=longitude,
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    db.close()

    return {
        "message": "Laporan tersimpan!",
        "id": new_report.id
    }

# 🔥 GET semua laporan
@app.get("/reports")
def get_reports():
    db = SessionLocal()
    reports = db.query(models.Report).all()
    db.close()

    result = []
    for r in reports:
        result.append({
            "id": r.id,
            "filename": r.filename,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "status": r.status
        })

    return result

# 🔥 UPDATE status laporan
@app.put("/report/{report_id}")
def update_status(report_id: int, status: str):
    db = SessionLocal()

    report = db.query(models.Report).filter(models.Report.id == report_id).first()

    if not report:
        db.close()
        return {"message": "Laporan tidak ditemukan"}

    report.status = status
    db.commit()

    db.close()

    return {"message": "Status berhasil diupdate"}