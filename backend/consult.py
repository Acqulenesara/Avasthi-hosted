from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import datetime
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
WHEREBY_API_KEY = os.getenv("WHEREBY_API_KEY")
WHEREBY_API_URL = "https://api.whereby.dev/v1/meetings"
# --- Import from your new modules ---
from Database import Professional, AvailabilitySlot, Appointment
from schemas import (
    ProfessionalResponse,
    AvailabilitySlotResponse,
    AppointmentBookingRequest,
    AppointmentResponse
)
# --- Import from your main file (or move these to database.py and auth.py) ---
from recom.backend.database import get_db
from recom.backend.auth import extract_username_from_token, oauth2_scheme

# Create the new router for consultation
router = APIRouter(
    prefix="/consult",
    tags=["Consultation"],
    dependencies=[Depends(oauth2_scheme)]  # All routes here require auth
)


@router.get("/professionals", response_model=List[ProfessionalResponse])
async def list_professionals(db: Session = Depends(get_db)):
    professionals = db.query(Professional).all()
    return professionals


@router.get("/professionals/{professional_id}/slots", response_model=List[AvailabilitySlotResponse])
async def get_professional_availability(professional_id: int, db: Session = Depends(get_db)):
    slots = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.professional_id == professional_id,
        AvailabilitySlot.is_booked == False
    ).order_by(AvailabilitySlot.start_time).all()
    return slots


@router.post("/book", response_model=AppointmentResponse)
async def book_appointment(
        booking_req: AppointmentBookingRequest,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    username = extract_username_from_token(token)

    # Make sure the slot isn't already booked (for safety)
    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == booking_req.slot_id
    ).with_for_update().first()

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found.")

    if slot.is_booked:
        raise HTTPException(status_code=400, detail="This slot is already booked.")

    # --- API Call Part ---
    patient_meeting_link = None
    host_meeting_link = None  # --- CHANGED ---

    try:
        headers = {
            "Authorization": f"Bearer {WHEREBY_API_KEY}",
            "Content-Type": "application/json"
        }

        # --- CHANGED ---
        # Make sure end_time is in UTC 'Z' format for the API
        end_date_utc = slot.end_time.isoformat() + "Z"

        payload = {
            "isLocked": True,
            "endDate": end_date_utc,  # --- CHANGED ---
            "roomMode": "group"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(WHEREBY_API_URL, headers=headers, json=payload)

            # This will print the error from Whereby if something fails
            response.raise_for_status()

            data = response.json()

            # --- CHANGED ---
            # Get BOTH links
            patient_meeting_link = data.get("roomUrl")
            host_meeting_link = data.get("hostRoomUrl")

            print(f"Patient Link: {patient_meeting_link}")
            print(f"Host Link: {host_meeting_link}")

    except httpx.HTTPStatusError as e:
        print(f"API Error: {e.response.text}")  # --- CHANGED --- (prints more detail)
        raise HTTPException(status_code=500, detail=f"Failed to create video room: {e.response.text}")
    except Exception as e:
        print(f"Generic Error: {e}")
        raise HTTPException(status_code=500, detail="Video room creation failed.")

    # --- CHANGED ---
    if not patient_meeting_link or not host_meeting_link:
        raise HTTPException(status_code=500, detail="Failed to get valid meeting links from API.")

    # --- Save to DB ---
    slot.is_booked = True
    new_appointment = Appointment(
        user_username=username,
        professional_id=slot.professional_id,
        slot_id=slot.id,
        status="booked",
        meeting_link=patient_meeting_link,  # Use the patient link
        host_meeting_link=host_meeting_link  # --- CHANGED --- (save the host link)
    )

    db.add(new_appointment)
    db.add(slot)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment  # This will return the full appointment object


@router.get("/my-appointments", response_model=List[AppointmentResponse])
async def get_my_appointments(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get all appointments for the currently logged-in user.
    """
    username = extract_username_from_token(token)

    appointments = db.query(Appointment).options(
        joinedload(Appointment.professional),
        joinedload(Appointment.slot)
    ).filter(Appointment.user_username == username).order_by(Appointment.id.desc()).all()

    return appointments