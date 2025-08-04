from fastapi import FastAPI, Depends, HTTPException
from database import SessionLocal
from models import DeviceTable
from thread import ServerThread
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/startup")
def index():
    print("Starting TCP server in background thread...")
    tcp_server_thread = ServerThread()
    tcp_server_thread.start()
    print("TCP server  running.")
    return {"message": "TCP server is running now!"}

@app.get("/devicedata/{imei}")
def get_device_data(imei: str, db=Depends(get_db)):
    device = db.query(DeviceTable).filter(DeviceTable.imei == imei).first()
    if not device:
        return {"message" : "Device not found"}
    all_messages = []
    for entry in device.data:
        all_messages.append({
            "message": entry.message,
            "received_at": entry.received_at.isoformat()
        })

    return {
        "imei": device.imei,
        "device_model": device.device_model,
        "data": all_messages
    }
from pydantic import BaseModel
class FCMTokenRequest(BaseModel):
    imei: str
    fcm_token: str


@app.post("/register-fcm-token/")
def register_fcm_token(payload: FCMTokenRequest,db: Session = Depends(get_db)):
    device = db.query(DeviceTable).filter(DeviceTable.imei == payload.imei).first()

    if not device:
        return {"message" : "Device not found"}

    device.fcm_token = payload.fcm_token
    db.commit()
    return {"message": "FCM token registered successfully"}

