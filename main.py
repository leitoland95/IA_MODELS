import os
import threading
import time
import requests
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta frontend
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

logs = []

@app.get("/")
def serve_index():
    return FileResponse(os.path.join("frontend", "index.html"))

@app.post("/like")
async def like_button(request: Request):
    logs.append("Botón 'Me gusta' presionado")
    return {"status": "ok"}

@app.get("/logs")
async def get_logs():
    return logs

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