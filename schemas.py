"""
Database Schemas for University App

Each Pydantic model represents a collection in MongoDB. The collection name
is the lowercase of the class name (e.g., Class -> "class").
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Class(BaseModel):
    code: str = Field(..., description="Unique class code, e.g., CS101")
    name: str = Field(..., description="Class title")
    instructor: str = Field(..., description="Instructor full name")
    schedule: str = Field(..., description="When the class meets, e.g., Mon/Wed 10:00-11:15")


class Notification(BaseModel):
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification content")
    class_code: Optional[str] = Field(None, description="Optional class code if targeted to a specific class")


class Payment(BaseModel):
    student_id: str = Field(..., description="Student identifier")
    amount: float = Field(..., ge=0, description="Amount to be paid")
    term: str = Field(..., description="Term/semester identifier, e.g., Fall 2025")
    status: str = Field("pending", description="Payment status: pending, paid, failed")


class Message(BaseModel):
    class_code: str = Field(..., description="Class code to which this message belongs")
    author: str = Field(..., description="Display name or student id of sender")
    content: str = Field(..., description="Message text content")
