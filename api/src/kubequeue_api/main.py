from fastapi import FastAPI
import socket

app = FastAPI()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "hostname": socket.gethostname()
    }


@app.get("/")
def root():
    return {"message": "KubeQueue API running"}