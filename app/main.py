import asyncio
import json
import random
import math
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import datetime

app = FastAPI(title="Bike Connect Telemetry API")

class LogData(BaseModel):
    data: str

@app.post("/log_telemetry")
async def log_telemetry(log_req: LogData):
    with open("server.log", "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {log_req.data}\n")
    return {"status": "ok"}

@app.get("/replay_log", response_class=PlainTextResponse)
async def replay_log():
    try:
        with open("server.log", "r") as f:
            return f.read()
    except Exception as e:
        return ""

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TelemetrySimulator:
    def __init__(self):
        self.speed = 0.0
        self.rpm = 1000
        self.gear = 1
        self.engine_temp = 85.0
        self.battery = 14.2
        self.lean_angle = 0.0
        self.throttle = 0.0
        
        # State variables for simulation
        self._target_speed = 0.0
        self._time = 0.0

    def update(self):
        self._time += 0.1
        
        # Simulate throttle and speed
        # Smoothly vary target speed
        if random.random() < 0.05:
            self._target_speed = random.uniform(0, 200)
            
        # Move speed towards target
        diff = self._target_speed - self.speed
        if diff > 0:
            self.throttle = min(100.0, diff * 2)
            self.speed += min(diff * 0.1, 2.0)
        else:
            self.throttle = 0.0
            self.speed += max(diff * 0.1, -3.0)
            
        if self.speed < 0:
            self.speed = 0

        # Simulate Gear and RPM based on speed
        if self.speed == 0:
            self.gear = 1
            self.rpm = 1000 + random.uniform(-50, 50)
        else:
            # Simple gear calculation
            self.gear = max(1, min(6, int((self.speed / 35) + 1)))
            # RPM calculation based on speed and gear
            speed_in_gear = self.speed - ((self.gear - 1) * 35)
            self.rpm = 2000 + (speed_in_gear * 200) + random.uniform(-100, 100)
            
        if self.rpm > 14000:
            self.rpm = 14000 - random.uniform(0, 500)

        # Simulate Engine Temp
        target_temp = 85.0 + (self.rpm / 14000) * 30.0
        self.engine_temp += (target_temp - self.engine_temp) * 0.01

        # Simulate Lean Angle
        target_lean = math.sin(self._time * 0.5) * min(self.speed * 0.5, 45.0)
        self.lean_angle += (target_lean - self.lean_angle) * 0.1

        return {
            "speed": round(self.speed),
            "rpm": round(self.rpm),
            "gear": self.gear,
            "engine_temp": round(self.engine_temp, 1),
            "battery": round(self.battery, 1),
            "lean_angle": round(self.lean_angle, 1),
            "throttle": round(self.throttle, 1)
        }

simulator = TelemetrySimulator()

@app.get("/")
def read_root():
    return {"status": "Bike Connect Backend is Running"}

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Generate simulated data
            data = simulator.update()
            await websocket.send_text(json.dumps(data))
            # Wait for 100ms for a real-time feel
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
