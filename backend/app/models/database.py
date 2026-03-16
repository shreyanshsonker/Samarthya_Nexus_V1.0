import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Household(Base):
    __tablename__ = "households"

    household_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    inverter_type = Column(String, nullable=False)
    capacity_kw = Column(Float, nullable=False)
    grid_zone = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("UserAccount", back_populates="household")
    inverters = relationship("InverterDevice", back_populates="household")
    energy_reports = relationship("EnergyReport", back_populates="household")
    recommendations = relationship("Recommendation", back_populates="household")

class UserAccount(Base):
    __tablename__ = "user_accounts"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.household_id"), nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    inverter_token = Column(String, nullable=True) # AES-256 encrypted
    jwt_refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    household = relationship("Household", back_populates="users")

class InverterDevice(Base):
    __tablename__ = "inverter_devices"

    device_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.household_id"), nullable=False)
    brand = Column(String, nullable=False) # Growatt, SMA, Mock
    serial_number = Column(String, unique=True, nullable=False)
    status = Column(String, default="offline")
    last_online = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    household = relationship("Household", back_populates="inverters")

class EnergyReport(Base):
    __tablename__ = "energy_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.household_id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    daily_generation_kwh = Column(Float, default=0.0)
    daily_consumption_kwh = Column(Float, default=0.0)
    grid_import_kwh = Column(Float, default=0.0)
    grid_export_kwh = Column(Float, default=0.0)
    carbon_offset_kg = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    household = relationship("Household", back_populates="energy_reports")

class Recommendation(Base):
    __tablename__ = "recommendations"

    rec_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.household_id"), nullable=False)
    category = Column(String, nullable=False) # load_shifting, efficiency, optimization
    message = Column(String, nullable=False)
    saving_kg = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    followed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    household = relationship("Household", back_populates="recommendations")
