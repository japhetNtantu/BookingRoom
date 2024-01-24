from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class BookingRoom(BaseModel):
    id: str  
    owner_id: str  
    title: str
    description: str
    location: str
    capacity: int

class BookingRoomNoId(BaseModel):
    title: str
    description: str
    location: str
    capacity: int

class User(BaseModel):
    email: str  
    password: str  