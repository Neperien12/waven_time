from pydantic import BaseModel

class PlayerCreate(BaseModel):
    name: str
    password: str

class SessionCreate(BaseModel):
    name: str
    password: str
    station_id: int
    duration: int