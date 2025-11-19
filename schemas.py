"""
Database Schemas for Assmat Pro

Each Pydantic model maps to a MongoDB collection using its lowercase class name.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import date

Role = Literal["parent", "assistant"]

class User(BaseModel):
    """
    Users collection schema
    Collection: "user"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    role: Role = Field(..., description="User role: parent or assistant")
    avatar_url: Optional[str] = Field(None, description="Profile image URL")
    provider: Optional[str] = Field(None, description="Auth provider (google/apple/facebook)")
    phone: Optional[str] = Field(None, description="Phone number")
    city: Optional[str] = Field(None, description="City of residence")
    bio: Optional[str] = Field(None, description="Short description/bio")
    is_active: bool = Field(True, description="Whether user is active")

class Announcement(BaseModel):
    """
    Announcements for matching parents and assistants
    Collection: "announcement"
    """
    title: str = Field(..., description="Title")
    description: str = Field(..., description="Description")
    author_email: EmailStr = Field(..., description="Owner email")
    author_role: Role = Field(..., description="Role of author")
    city: Optional[str] = Field(None, description="City")
    availability: Optional[str] = Field(None, description="Availability notes")

class Contract(BaseModel):
    """
    Employment contract data
    Collection: "contract"
    """
    parent_email: EmailStr
    assistant_email: EmailStr
    child_name: str
    start_date: date
    hours_per_week: float = Field(..., ge=0)
    hourly_rate: float = Field(..., ge=0)
    paid_vacation_days: int = Field(25, ge=0)
    notes: Optional[str] = None

class ScheduleEntry(BaseModel):
    """
    Weekly planning entries
    Collection: "scheduleentry"
    """
    user_email: EmailStr
    weekday: Literal["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    start_time: str = Field(..., description="HH:MM")
    end_time: str = Field(..., description="HH:MM")
    note: Optional[str] = None

# Additional simple calculator request models
class SalaryCalc(BaseModel):
    hours: float
    rate: float

class LeaveCalc(BaseModel):
    accrued_days: float
    days_taken: float

class BalanceCalc(BaseModel):
    credits: float
    debits: float
