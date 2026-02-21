from pydantic import BaseModel
from datetime import datetime, date
from typing import List

# --- Schemas for Consultation ---

class ProfessionalBase(BaseModel):
    full_name: str
    specialty: str
    bio: str

class ProfessionalResponse(ProfessionalBase):
    id: int
    class Config:
        from_attribute = True

class AvailabilitySlotBase(BaseModel):
    start_time: datetime
    end_time: datetime

class AvailabilitySlotResponse(AvailabilitySlotBase):
    id: int
    professional_id: int
    is_booked: bool
    class Config:
        from_attribute = True

class AppointmentBookingRequest(BaseModel):
    slot_id: int

class AppointmentResponse(BaseModel):
    id: int
    status: str
    meeting_link: str | None
    professional: ProfessionalResponse
    slot: AvailabilitySlotResponse
    class Config:
        from_attribute = True

# --- Other Schemas ---

class UserRegister(BaseModel):
    username: str
    password: str

class QueryPayload(BaseModel):
    query: str

class JournalEntryRequest(BaseModel):
    entry: str

class JournalEntryResponse(BaseModel):
    entry_text: str
    entry_date: str
    mood: str
    sentiment: float