from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен быть минимум 8 символов")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── About ────────────────────────────────────────────────────────────────────

class AboutRequest(BaseModel):
    name: Optional[str] = None
    school: Optional[str] = None
    grade: Optional[str] = None


class AboutResponse(BaseModel):
    id: int
    user_id: int
    name: Optional[str]
    school: Optional[str]
    grade: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Academic ─────────────────────────────────────────────────────────────────

class AcademicRequest(BaseModel):
    gpa: Optional[float] = None
    sat: Optional[int] = None
    ielts: Optional[float] = None
    toefl: Optional[int] = None
    act: Optional[int] = None

    @field_validator("gpa")
    @classmethod
    def gpa_range(cls, v):
        if v is not None and not (0.0 <= v <= 4.0):
            raise ValueError("GPA должен быть от 0.0 до 4.0")
        return v

    @field_validator("sat")
    @classmethod
    def sat_range(cls, v):
        if v is not None and not (400 <= v <= 1600):
            raise ValueError("SAT должен быть от 400 до 1600")
        return v

    @field_validator("ielts")
    @classmethod
    def ielts_range(cls, v):
        if v is not None and not (1.0 <= v <= 9.0):
            raise ValueError("IELTS должен быть от 1.0 до 9.0")
        return v

    @field_validator("toefl")
    @classmethod
    def toefl_range(cls, v):
        if v is not None and not (0 <= v <= 120):
            raise ValueError("TOEFL должен быть от 0 до 120")
        return v

    @field_validator("act")
    @classmethod
    def act_range(cls, v):
        if v is not None and not (1 <= v <= 36):
            raise ValueError("ACT должен быть от 1 до 36")
        return v


class AcademicResponse(BaseModel):
    id: int
    user_id: int
    gpa: Optional[float]
    sat: Optional[int]
    ielts: Optional[float]
    toefl: Optional[int]
    act: Optional[int]
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Extracurricular ───────────────────────────────────────────────────────────

VALID_CATEGORIES = {"volunteering", "leadership", "club", "research", "olympiad", "sport"}


class ExtracurricularRequest(BaseModel):
    categories: List[str]
    years_active: Optional[str] = None

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, v):
        for cat in v:
            if cat not in VALID_CATEGORIES:
                raise ValueError(f"Недопустимая категория: {cat}. Допустимые: {VALID_CATEGORIES}")
        return v


class ExtracurricularResponse(BaseModel):
    id: int
    user_id: int
    category: str
    years_active: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── User ─────────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
    about: Optional[AboutResponse]
    academic: Optional[AcademicResponse]
    extracurriculars: List[ExtracurricularResponse]

    class Config:
        from_attributes = True


# ── Universities ─────────────────────────────────────────────────────────────

class UniversityResponse(BaseModel):
    id: int
    name: str
    country: str
    city: Optional[str]
    min_gpa: Optional[float]
    min_sat: Optional[int]
    min_ielts: Optional[float]
    min_toefl: Optional[int]
    probability: Optional[float]
    label: Optional[str]
    color: Optional[str]
    full_description: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    deadline: Optional[str]
    ranking: Optional[int]
    is_saved: bool = False

    class Config:
        from_attributes = True


# ── Opportunities ─────────────────────────────────────────────────────────────

class OpportunityResponse(BaseModel):
    id: int
    type: str
    title: str
    short_description: Optional[str]
    full_description: Optional[str]
    image_url: Optional[str]
    event_date: Optional[str]
    deadline: Optional[str]
    organizer: Optional[str]
    is_online: bool
    is_saved: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    greeting: str
    days_to_nearest_deadline: Optional[int]
    nearest_deadline_university: Optional[str]
    saved_universities_count: int
    profile_complete: bool


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: int
    title: str
    body: Optional[str]
    type: Optional[str]
    is_read: bool
    link_id: Optional[int]
    link_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Motivation Letter ────────────────────────────────────────────────────────

class MotivationLetterRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_length(cls, v):
        if len(v) < 100:
            raise ValueError("Текст должен быть минимум 100 символов")
        if len(v) > 10000:
            raise ValueError("Текст не должен превышать 10 000 символов")
        return v


class MotivationLetterResponse(BaseModel):
    score: int
    label: str
    color: str
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
