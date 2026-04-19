from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    about = relationship("About", back_populates="user", uselist=False, cascade="all, delete-orphan")
    academic = relationship("Academic", back_populates="user", uselist=False, cascade="all, delete-orphan")
    extracurriculars = relationship("Extracurricular", back_populates="user", cascade="all, delete-orphan")
    saved_universities = relationship("SavedUniversity", back_populates="user", cascade="all, delete-orphan")
    saved_opportunities = relationship("SavedOpportunity", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class About(Base):
    __tablename__ = "abouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=True)
    school = Column(String, nullable=True)
    grade = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="about")


class Academic(Base):
    __tablename__ = "academics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    gpa = Column(Float, nullable=True)
    sat = Column(Integer, nullable=True)
    ielts = Column(Float, nullable=True)
    toefl = Column(Integer, nullable=True)
    act = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="academic")


class Extracurricular(Base):
    __tablename__ = "extracurriculars"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)  # volunteering, leadership, club, research, olympiad, sport
    years_active = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="extracurriculars")


class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=True)
    full_description = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    ranking = Column(Integer, nullable=True)

    # Requirements
    min_gpa = Column(Float, nullable=True)
    min_sat = Column(Integer, nullable=True)
    min_ielts = Column(Float, nullable=True)
    min_toefl = Column(Integer, nullable=True)

    # Label: Сложно / Средне / Реально
    label = Column(String, nullable=True)
    color = Column(String, nullable=True)  # red / yellow / green

    # Deadline info
    deadline = Column(String, nullable=True)
    deadline_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    saved_by = relationship("SavedUniversity", back_populates="university", cascade="all, delete-orphan")


class SavedUniversity(Base):
    __tablename__ = "saved_universities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_universities")
    university = relationship("University", back_populates="saved_by")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # internship / volunteering / hackathon
    title = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    full_description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    event_date = Column(String, nullable=True)
    deadline = Column(String, nullable=True)
    deadline_date = Column(DateTime, nullable=True)
    organizer = Column(String, nullable=True)
    is_online = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    saved_by = relationship("SavedOpportunity", back_populates="opportunity", cascade="all, delete-orphan")


class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_opportunities")
    opportunity = relationship("Opportunity", back_populates="saved_by")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=True)
    type = Column(String, nullable=True)  # deadline / opportunity / system
    is_read = Column(Boolean, default=False)
    link_id = Column(Integer, nullable=True)   # id университета или возможности
    link_type = Column(String, nullable=True)  # university / opportunity
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
