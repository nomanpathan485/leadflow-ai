from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    course: str = Field(min_length=2, max_length=100)
    message: str = Field(min_length=10, max_length=2000)


class LeadStatusUpdate(BaseModel):
    status: Literal["New", "Contacted", "Booked", "Closed"]