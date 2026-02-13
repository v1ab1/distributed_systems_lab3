class TicketNotFoundError(Exception):
    def __init__(self, ticket_uid: str):
        message = f"Ticket with ticket_uid={ticket_uid} not found"
        super().__init__(message)
        self.ticket_uid = ticket_uid
        self.message = message


class FlightNotFoundError(Exception):
    def __init__(self, flight_number: str):
        message = f"Flight with flight_number={flight_number} not found"
        super().__init__(message)
        self.flight_number = flight_number
        self.message = message


class InsufficientBalanceError(Exception):
    def __init__(self, balance: int, required: int):
        message = f"Insufficient balance. Available: {balance}, Required: {required}"
        super().__init__(message)
        self.balance = balance
        self.required = required
        self.message = message
