from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="patient") # 'patient' or 'doctor'
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    sessions = relationship("ConversationSession", back_populates="user")

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    specialization = Column(String(100))
    slack_id = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Extended Profile Fields
    experience_years = Column(Integer, default=0)
    qualification = Column(String(255))
    consultation_fee = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="doctor_profile")
    appointments = relationship("Appointment", back_populates="doctor")
    availability_slots = relationship("AvailabilitySlot", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_name = Column(String(100), nullable=False)
    patient_email = Column(String(100), nullable=False)
    appointment_time = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="scheduled")
    google_calendar_event_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    doctor = relationship("Doctor", back_populates="appointments")

class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    slot_duration_minutes = Column(Integer, default=30)

    doctor = relationship("Doctor", back_populates="availability_slots")

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    session_id = Column(String(100), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = Column(JSON, default=[])
    context = Column(JSON, default={})
    user = relationship("User", back_populates="sessions")
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
