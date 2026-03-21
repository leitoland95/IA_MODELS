import os
import threading
import time
import requests
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Montar carpeta frontend
app.mount("/public", StaticFiles(directory="public"), name="public")

logs = []

@app.get("/")
def serve_index():
    return FileResponse(os.path.join("public", "index.html"))

@app.post("/like")
async def like_button(request: Request):
    logs.append("Botón 'Me gusta' presionado")
    return {"status": "ok"}

@app.get("/logs")
async def get_logs():
    return logs
    
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Render expone la URL base en RENDER_EXTERNAL_URL
        base_url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
        file_url = f"{base_url}/uploads/{file.filename}"

        return JSONResponse({"url": file_url})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)    

# -------------------------------
# Keep-alive para Render
# -------------------------------
def keep_alive():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        print("No se encontró RENDER_EXTERNAL_URL, keep_alive desactivado")
        return
    while True:
        try:
            requests.get(url)
            print(f"Ping a {url} para mantener vivo el servicio")
        except Exception as e:
            print(f"Error en keep_alive: {e}")
        time.sleep(60)  # cada 60 segundos

# Lanzar el keep_alive en un hilo aparte
threading.Thread(target=keep_alive, daemon=True).start()