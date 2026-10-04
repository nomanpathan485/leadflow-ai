from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EnquiryAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=300)

    course_interest: str | None = Field(max_length=100)
    start_preference: str | None = Field(max_length=200)

    contact_method: Literal["email", "phone", "whatsapp"] | None
    contact_time: str | None = Field(max_length=200)

    requested_information: list[
        Literal[
            "fees",
            "syllabus",
            "schedule",
            "duration",
            "certification",
            "placement_support",
            "demo_class",
            "other",
        ]
    ]

    needs_human_review: bool
    review_reason: str | None = Field(max_length=300)