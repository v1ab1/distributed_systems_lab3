class AirportNotFoundError(Exception):
    def __init__(self, id: int):
        message = f"Airport with id={id} not found"
        super().__init__(message)
        self.id = id
        self.message = message


class FlightNotFoundError(Exception):
    def __init__(self, id: int):
        message = f"Flight with id={id} not found"
        super().__init__(message)
        self.id = id
        self.message = message
