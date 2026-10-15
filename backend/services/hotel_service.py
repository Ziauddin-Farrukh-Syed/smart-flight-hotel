from backend.models.hotel import Hotel
from backend.models.travel import TravelRequest


def search_hotels(request: TravelRequest) -> list[Hotel]:
    """
    Development hotel provider.

    Later this can be replaced with a real
    hotel API.
    """

    return [
        Hotel(
            name="Demo Grand Hotel",
            city=request.destination,
            rating=4.5,
            nightly_price=180,
            currency="GBP",
            address="123 Demo Street",
        ),
        Hotel(
            name="Example Central Hotel",
            city=request.destination,
            rating=4.2,
            nightly_price=145,
            currency="GBP",
            address="45 Example Avenue",
        ),
        Hotel(
            name="Budget Business Hotel",
            city=request.destination,
            rating=3.8,
            nightly_price=95,
            currency="GBP",
            address="78 Business Road",
        ),
    ]