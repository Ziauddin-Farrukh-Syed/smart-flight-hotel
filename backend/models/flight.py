from pydantic import BaseModel, Field


class Flight(BaseModel):
    airline: str
    flight_number: str

    origin: str
    destination: str

    departure_date: str
    departure_time: str
    arrival_time: str

    cabin_class: str

    price: float = Field(gt=0)

    stops: int = Field(ge=0)

    duration_hours: float = Field(gt=0)