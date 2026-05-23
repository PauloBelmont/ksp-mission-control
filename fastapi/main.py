from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from krpc_client import get_vessel_data

app = FastAPI(title="KSP Telemetry API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/telemetry")
def telemetry():
    try:
        data = get_vessel_data()
        return data
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
