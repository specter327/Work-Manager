import os
import json

import firebase_admin
from firebase_admin import credentials, db

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# =========================
# APP
# =========================

app = FastAPI(
    title="Work Manager Endpoint Verification",
    version="1.0.0"
)


# =========================
# FIREBASE INIT
# =========================

def init_firebase():
    # Evitar doble inicialización (importante en Render)
    if firebase_admin._apps:
        return

    firebase_creds_json = os.getenv("FIREBASE_CREDENTIALS")
    firebase_db_url = os.getenv(
        "FIREBASE_DB_URL",
        "https://work-manager-verification-default-rtdb.firebaseio.com"
    )

    if not firebase_creds_json:
        raise RuntimeError("FIREBASE_CREDENTIALS environment variable not set")

    try:
        creds_dict = json.loads(firebase_creds_json)
    except json.JSONDecodeError:
        raise RuntimeError("FIREBASE_CREDENTIALS is not valid JSON")

    cred = credentials.Certificate(creds_dict)

    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_db_url
    })


init_firebase()


# =========================
# MODELOS
# =========================

class VerifyRequest(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=128)


class VerifyResponse(BaseModel):
    device_id: str
    status: str
    reason: str


# =========================
# CONSTANTS
# =========================
STATUS_APPROVED = "APPROVED"
STATUS_DENIED = "DENIED"

DENY_NO_WHITELIST = "NO_WHITELIST"
DENY_NOT_REGISTERED = "NOT_REGISTERED"
DENY_DISABLED = "DISABLED"

# =========================
# ENDPOINTS
# =========================

@app.get("/")
def root():
    return {
        "status": "OK",
        "service": "Work Manager Endpoint Verification"
    }


@app.post("/verify", response_model=VerifyResponse)
def verify_device(payload: VerifyRequest):
    device_id = payload.device_id

    ref = db.reference("whitelist")
    whitelist = ref.get()

    # 1️⃣ No existe la whitelist
    if not isinstance(whitelist, dict):
        return VerifyResponse(
            device_id=device_id,
            status=STATUS_DENIED,
            reason=DENY_NO_WHITELIST
        )

    device = whitelist.get(device_id)

    # 2️⃣ Device no registrado
    if not isinstance(device, dict):
        return VerifyResponse(
            device_id=device_id,
            status=STATUS_DENIED,
            reason=DENY_NOT_REGISTERED
        )

    # 3️⃣ Device deshabilitado
    if device.get("enabled") is not True:
        return VerifyResponse(
            device_id=device_id,
            status=STATUS_DENIED,
            reason=DENY_DISABLED
        )

    # 4️⃣ Autorizado
    return VerifyResponse(
        device_id=device_id,
        status=STATUS_APPROVED,
        reason="AUTHORIZED"
    )
