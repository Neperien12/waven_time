from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Table
class SessionDB(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String)
    station = Column(String)
    end_time = Column(String)
    active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

# ➜ Créer session
@app.post("/start")
def start_session(player_name: str, station: str, minutes: int):
    if minutes < 30:
        raise HTTPException(status_code=400, detail="Minimum 30 minutes")

    db = SessionLocal()
    end_time = datetime.now() + timedelta(minutes=minutes)

    session = SessionDB(
        player_name=player_name,
        station=station,
        end_time=end_time.isoformat(),
        active=True
    )

    db.add(session)
    db.commit()
    db.close()

    return {"message": "Session créée"}

# ➜ Sessions
@app.get("/sessions")
def get_sessions():
    db = SessionLocal()
    sessions = db.query(SessionDB).filter(SessionDB.active == True).all()

    result = []
    for s in sessions:
        remaining = datetime.fromisoformat(s.end_time) - datetime.now()
        seconds = max(0, int(remaining.total_seconds()))

        if seconds == 0:
            s.active = False
            db.commit()

        result.append({
            "id": s.id,
            "player_name": s.player_name,
            "station": s.station,
            "remaining_seconds": seconds
        })

    db.close()
    return result

# ➜ Stop
@app.post("/stop/{session_id}")
def stop_session(session_id: int):
    db = SessionLocal()
    s = db.query(SessionDB).get(session_id)

    if s:
        s.active = False
        db.commit()

    db.close()
    return {"message": "Session stoppée"}
