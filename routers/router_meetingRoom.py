import json
from fastapi import APIRouter,Depends, HTTPException
from typing import List
from database.firebase import db
from routers.router_auth import get_current_user

from classes.schema_dto import BookingRoom, BookingRoomNoId
import uuid

router = APIRouter(
    prefix='/bookingroom',
    tags=["bookingroom"]
)

meetingRooms=[]

@router.get('/', response_model=List[BookingRoom])
async def get_all_meeting_rooms(userData: int = Depends(get_current_user)):
    BookingRoomsData = db.child("BookingRooms").get(userData['idToken']).val()
    if userData and BookingRoomsData:
        # Si des données sont disponibles, convertissez-les en une liste de BookingRoom
        meeting_rooms_list = []
        for room_id, room_data in BookingRoomsData.items():
            room = BookingRoom(**room_data)
            room.id = room_id
            meeting_rooms_list.append(room)
        return meeting_rooms_list
    else:
        return []
    
@router.get('/{meeting_id}', response_model=BookingRoom)
async def get_meeting_room_by_id(meeting_id: str,userData: int = Depends(get_current_user)):
    BookingRoomData = db.child("BookingRooms").child(meeting_id).get(userData['idToken']).val()
    raise HTTPException(status_code=404, detail="Booking room not found")

@router.post('/', response_model=BookingRoom, status_code=201)
async def add_new_meeting_room(given_room: BookingRoomNoId, userData: int = Depends(get_current_user)):
    # Générez un ID unique pour la salle de réunio
    generated_id = uuid.uuid4()
    owner_id = userData['uid']
    
    # Créez une nouvelle instance de la salle de réunion
    new_meeting_room = BookingRoom(
        id=str(generated_id),
        owner_id=owner_id,
        title=given_room.title,
        description=given_room.description,
        location=given_room.location,
        capacity=given_room.capacity,
    )

    # Convertissez la salle de réunion en un dictionnaire Python
    BookingRoom.append(new_meeting_room)
    # Stockez le dictionnaire dans la base de données Firebase en tant que JSON
    db.child("BookingRooms").child(str(generated_id)).set(new_meeting_room.model_dump(), userData['idToken'])
    return new_meeting_room

@router.delete('/{meeting_id}', response_model=dict)
async def delete_meeting_room_by_id(meeting_id: str, userData: int = Depends(get_current_user)):
    BookingRoomData = db.child("BookingRooms").child(meeting_id).get(userData['idToken']).val()
    if BookingRoomData:
        # Vérifiez si l'owner_id de la salle de réunion correspond à l'uid de l'utilisateur actuel
        if BookingRoomData.get('owner_id') == userData['uid']:
            # Supprimez la salle de réunion de la base de données Firebase
            db.child("BookingRooms").child(meeting_id).remove()
            return {"message": "Meeting room deleted"}
        else:
            raise HTTPException(status_code=403, detail="Permission denied. You are not the owner of this meeting room")
    else:
        raise HTTPException(status_code=404, detail="Meeting room not found")

    
@router.patch('/{meeting_id}', response_model=BookingRoom)
async def patch_meeting_room_by_id(meeting_id: str, updated_meeting_room: BookingRoomNoId,userData: int = Depends(get_current_user)):
    BookingRoomData = db.child("BookingRooms").child(meeting_id).get(userData['idToken']).val()
    if BookingRoomData and BookingRoomData.get('owner_id') == userData['uid']:
        # Mettez à jour partiellement la salle de réunion dans la base de données Firebase
        update_data = {
            "title": updated_meeting_room.title,
            "description": updated_meeting_room.description,
            "location": updated_meeting_room.location,
            "capacity": updated_meeting_room.capacity,
            "priceOnHours": updated_meeting_room.priceOnHours,
        }
        db.child("BookingRooms").child(meeting_id).update(update_data)
        
        updated_meeting_room_data = db.child("BookingRooms").child(meeting_id).get(userData['idToken']).val()
        updated_meeting_room = BookingRoom(**updated_meeting_room_data)
        return updated_meeting_room
    else:
        raise HTTPException(status_code=404, detail="Meeting room not found")

