from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Secure DevSecOps App"}

@app.get("/health")
def health():
    return {"status": "healthy"}
