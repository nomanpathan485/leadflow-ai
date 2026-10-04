from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
)


class LeadInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr | None = None

    # International format: + followed by 8–15 digits.
    phone: str | None = Field(
        default=None,
        pattern=r"^\+[1-9]\d{7,14}$",
    )

    preferred_contact: Literal["email", "phone", "whatsapp"] = "email"
    whatsapp_consent: bool = False

    course: str = Field(min_length=2, max_length=100)
    message: str = Field(min_length=10, max_length=2000)

    @model_validator(mode="after")
    def validate_contact_details(self) -> Self:
        if self.preferred_contact == "email" and self.email is None:
            raise ValueError("Email is required for email contact.")

        if self.preferred_contact in {"phone", "whatsapp"} and self.phone is None:
            raise ValueError(
                "Phone number with country code is required."
            )

        if self.preferred_contact == "whatsapp" and not self.whatsapp_consent:
            raise ValueError(
                "Permission is required to respond through WhatsApp."
            )

        if self.whatsapp_consent and self.phone is None:
            raise ValueError(
                "WhatsApp permission requires a phone number."
            )

        return self


class LeadStatusUpdate(BaseModel):
    status: Literal["New", "Contacted", "Booked", "Closed"]