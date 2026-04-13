from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from .database import SessionLocal
from .models import Player, Session as GameSession
from .schemas import SessionCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/start-session")
def start_session(data: SessionCreate, db: Session = Depends(get_db)):
    if data.duration < 30:
        raise HTTPException(status_code=400, detail="Minimum 30 min")

    player = db.query(Player).filter(Player.name == data.name).first()

    if not player:
        player = Player(name=data.name, password=data.password)
        db.add(player)
        db.commit()
        db.refresh(player)

    end_time = datetime.utcnow() + timedelta(minutes=data.duration)

    session = GameSession(
        player_id=player.id,
        station_id=data.station_id,
        end_time=end_time
    )

    db.add(session)
    db.commit()

    return {"message": "Session started", "end_time": end_time}

@router.post("/get-session")
def get_session(name: str, password: str, db: Session = Depends(get_db)):
    player = db.query(Player).filter(
        Player.name == name,
        Player.password == password
    ).first()

    if not player:
        raise HTTPException(status_code=404, detail="Not found")

    session = db.query(GameSession).filter(
        GameSession.player_id == player.id,
        GameSession.is_active == True
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="No active session")

    remaining = session.end_time - datetime.utcnow()

    return {"remaining_seconds": remaining.total_seconds()}