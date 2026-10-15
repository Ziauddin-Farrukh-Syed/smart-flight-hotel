from datetime import date

from pydantic import BaseModel, Field, field_validator


class TravelRequest(BaseModel):
    origin: str = Field(
        ...,
        min_length=2,
        description="Departure city or airport",
    )

    destination: str = Field(
        ...,
        min_length=2,
        description="Destination city or airport",
    )

    departure_date: date

    return_date: date

    passengers: int = Field(
        default=1,
        ge=1,
        le=20,
    )

    cabin_class: str = Field(
        default="economy",
    )

    max_budget: float = Field(
        ...,
        gt=0,
    )

    max_stops: int = Field(
        default=1,
        ge=0,
        le=5,
    )

    hotel_min_rating: float = Field(
        default=4.0,
        ge=1.0,
        le=5.0,
    )

    @field_validator("origin", "destination")
    @classmethod
    def validate_location(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Location cannot be empty")

        return value

    @field_validator("cabin_class")
    @classmethod
    def validate_cabin_class(cls, value: str) -> str:
        value = value.lower().strip()

        allowed_classes = {
            "economy",
            "premium_economy",
            "business",
            "first",
        }

        if value not in allowed_classes:
            raise ValueError(
                f"Invalid cabin class: {value}. "
                f"Allowed values: {sorted(allowed_classes)}"
            )

        return value

    @field_validator("return_date")
    @classmethod
    def validate_dates(
        cls,
        return_date: date,
        info,
    ) -> date:

        departure_date = info.data.get("departure_date")

        if departure_date and return_date <= departure_date:
            raise ValueError(
                "Return date must be after departure date."
            )

        return return_date