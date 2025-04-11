from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI()

HIGH_THRESHOLD = 30.0
LOW_THRESHOLD = 20.0

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



def send_alert(device_name: str, temperature: float, alert_type: str):
    # This is a simple mock function, can be expanded to send real-time alerts to the user/admin
    if alert_type == "high":
        print(f"ALERT: {device_name} has exceeded the high temperature threshold: {temperature}°C!")
    elif alert_type == "low":
        print(f"ALERT: {device_name} has dropped below the low temperature threshold: {temperature}°C!")


@app.post("/send-temp/")
def receive_temp(data: schemas.TemperatureBase, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter_by(name=data.device_name).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    reading = models.TemperatureReading(device_id=device.id, temperature=data.temperature)
    db.add(reading)
    db.commit()

    if data.temperature > HIGH_THRESHOLD:
        background_tasks.add_task(send_alert, data.device_name, data.temperature, "high")
    elif data.temperature < LOW_THRESHOLD:
        # Alert user and admin about low temperature
        background_tasks.add_task(send_alert, data.device_name, data.temperature, "low")

    return {"msg": "Temperature recorded"}


@app.post("/login/")
def login(auth: schemas.DeviceAuth, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter_by(name=auth.device_name, password=auth.password).first()
    if not device:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"msg": "Login successful"}

@app.post("/admin/login/")
def admin_login(auth: schemas.AdminAuth, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter_by(username=auth.username, password=auth.password).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return {"msg": "Admin login successful"}

@app.get("/admin/readings/{device_name}", response_model=list[schemas.ReadingOut])
def get_readings(device_name: str, db: Session = Depends(get_db)):
    device = db.query(models.Device).filter_by(name=device_name).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    readings = db.query(models.TemperatureReading).filter_by(device_id=device.id).order_by(models.TemperatureReading.timestamp.desc()).all()
    return readings

@app.get("/admin/alerts", response_model=list[schemas.AlertOut])
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).order_by(models.Alert.timestamp.desc()).all()
    return alerts
