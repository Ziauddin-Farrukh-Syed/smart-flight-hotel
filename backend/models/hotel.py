from pydantic import BaseModel, Field


class Hotel(BaseModel):
    name: str

    city: str

    rating: float = Field(
        ge=1,
        le=5,
    )

    nightly_price: float = Field(
        gt=0,
    )

    currency: str = "GBP"

    address: str | None = None