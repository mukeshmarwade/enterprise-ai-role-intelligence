from sqlalchemy import (
    Column, Integer, String, Boolean, Float, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship

from backend.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True, nullable=False)
    level = Column(String)
    industry = Column(String, default="Finance")
    processes = Column(JSON)          # list[str]
    current_skills = Column(JSON)     # list[str]
    ai_exposure_today = Column(Text)
    new_responsibilities = Column(JSON)   # list[str]
    future_skills = Column(JSON)          # list[str]

    # Derived / cached scoring outputs (computed by scoring.py, stored for fast reads)
    automation_pct = Column(Float, default=0.0)
    augmentation_pct = Column(Float, default=0.0)
    unaffected_pct = Column(Float, default=0.0)
    confidence = Column(String, default="medium")  # high / medium / low
    future_role_profile = Column(Text)
    reason_codes = Column(JSON)       # list[str] — explainability

    activities = relationship("Activity", back_populates="role", cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    name = Column(String, nullable=False)
    weight = Column(Float, default=0.0)  # % of role's time

    structured = Column(Boolean, default=False)
    repetitive = Column(Boolean, default=False)
    rule_based = Column(Boolean, default=False)
    requires_judgment = Column(Boolean, default=False)
    requires_creativity = Column(Boolean, default=False)
    interpersonal = Column(Boolean, default=False)

    automation_score = Column(Float, default=0.0)   # 0-100, this activity's automation potential
    augmentation_score = Column(Float, default=0.0)  # 0-100
    classification = Column(String)   # "automated" / "augmented" / "human-led"
    reason = Column(Text)             # per-activity explainability sentence

    role = relationship("Role", back_populates="activities")
