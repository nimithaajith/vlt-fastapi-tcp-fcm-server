from fastapi import FastAPI, Depends, HTTPException
from database import SessionLocal
from models import *
from thread import ServerThread
from sqlalchemy.orm import Session
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date, datetime
from decimal import Decimal



class UserCreate(BaseModel):
    username: str
    first_name: str
    email: str
    phone: str
    added_by: Optional[str] = None
    company_details: Optional[str] = None
    other_info: Optional[str] = None
    user_type: UserTypeEnum = UserTypeEnum.ADMIN

class DeviceCreate(BaseModel):
    imei: str
    device_company: str
    device_model: Optional[str]
    icc_id: str
    unique_id: Optional[str] = "N"
    primary_contact: Decimal
    secondary_contact: Optional[Decimal] = 0
    version: Optional[str] = "1"
    activation_status: bool
    activation_date: Optional[date]
    current_owner_username: str
    added_date: Optional[date] = None
    live_data: Optional[str] = None
    live_data_type: Optional[str] = None
    timestamp: Optional[datetime] = None
    fcm_token: Optional[str] = None

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

@app.post("/addUser")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "id": new_user.id}

@app.post("/addDevice")
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    # Check if device with same IMEI already exists
    existing_device = db.query(DeviceTable).filter(DeviceTable.imei == device.imei).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="Device with this IMEI already exists.")

    # Create device instance
    new_device = DeviceTable(**device.model_dump())

    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return {"message": "Device created successfully", "imei": new_device.imei}

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

