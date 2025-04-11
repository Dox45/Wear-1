from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Base schema for temperature submission
class TemperatureBase(BaseModel):
    device_name: str
    temperature: float

# Auth schema for login
class DeviceAuth(BaseModel):
    device_name: str
    password: str

# Optional: response model after login
class DeviceResponse(BaseModel):
    id: int
    name: str
    is_admin: bool

    class Config:
        orm_mode = True

# Optional: schema for returning temperature readings
class TemperatureReadingResponse(BaseModel):
    temperature: float
    timestamp: datetime

    class Config:
        orm_mode = True

class AdminAuth(BaseModel):
    username: str
    password: str

class ReadingOut(BaseModel):
    temperature: float
    timestamp: str

    class Config:
        orm_mode = True

class AlertOut(BaseModel):
    device_name: str
    temperature: float
    alert_type: str
    timestamp: str

    class Config:
        orm_mode = True
