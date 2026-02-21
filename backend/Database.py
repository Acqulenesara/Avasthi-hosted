from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, create_engine, MetaData
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.schema import UniqueConstraint

# This Base will be imported by your main file
Base = declarative_base()


# --- All your models go here ---

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String, unique=True, index=True)
    preferences_collected = Column(Integer, default=0)
    stress_level = Column(Integer, default=0)

    appointments = relationship("Appointment", back_populates="user")


class ChatInteraction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    query = Column(String)
    response = Column(String)
    scenario = Column(String, nullable=True)
    timestamp = Column(String, default=datetime.utcnow().isoformat)


class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    preference_type = Column(String)
    content = Column(String)
    __table_args__ = (UniqueConstraint('username', 'preference_type', 'content', name='uix_user_pref'),)


class JournalEntry(Base):
    __tablename__ = "journal_entry"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    entry_text = Column(String)
    entry_date = Column(Date)
    mood = Column(String)
    sentiment = Column(String)


class Professional(Base):
    __tablename__ = "professionals"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    specialty = Column(String, index=True)
    bio = Column(String)

    availability_slots = relationship("AvailabilitySlot", back_populates="professional")
    appointments = relationship("Appointment", back_populates="professional")


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    id = Column(Integer, primary_key=True, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_booked = Column(Boolean, default=False)

    professional = relationship("Professional", back_populates="availability_slots")
    appointment = relationship("Appointment", back_populates="slot")


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    user_username = Column(String, ForeignKey("users.username"))
    professional_id = Column(Integer, ForeignKey("professionals.id"))
    slot_id = Column(Integer, ForeignKey("availability_slots.id"), unique=True)
    status = Column(String, default="booked")
    meeting_link = Column(String, nullable=True)

    # --- ADD THIS LINE ---
    host_meeting_link = Column(String, nullable=True)

    user = relationship("User", back_populates="appointments")
    professional = relationship("Professional", back_populates="appointments")
    slot = relationship("AvailabilitySlot", back_populates="appointment")