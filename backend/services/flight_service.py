from backend.models.flight import Flight
from backend.models.travel import TravelRequest


def search_flights(request: TravelRequest) -> list[Flight]:
    """
    Development flight provider.

    Later this function can be replaced with
    a real flight API without changing the
    rest of the application.
    """

    return [
        Flight(
            airline="Demo Airways",
            flight_number="DA101",
            origin=request.origin,
            destination=request.destination,
            departure_date=str(request.departure_date),
            departure_time="09:00",
            arrival_time="21:30",
            cabin_class=request.cabin_class,
            price=1150,
            stops=1,
            duration_hours=8.5,
        ),
        Flight(
            airline="Demo Airlines",
            flight_number="DA202",
            origin=request.origin,
            destination=request.destination,
            departure_date=str(request.departure_date),
            departure_time="12:00",
            arrival_time="23:00",
            cabin_class=request.cabin_class,
            price=920,
            stops=0,
            duration_hours=8.0,
        ),
        Flight(
            airline="Example Air",
            flight_number="EA303",
            origin=request.origin,
            destination=request.destination,
            departure_date=str(request.departure_date),
            departure_time="16:00",
            arrival_time="04:30",
            cabin_class=request.cabin_class,
            price=780,
            stops=1,
            duration_hours=9.5,
        ),
    ]