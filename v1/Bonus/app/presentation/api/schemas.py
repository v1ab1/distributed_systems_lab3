from uuid import UUID
from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict, constr


class PrivilegeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: constr(min_length=1, max_length=80)  # type: ignore
    status: constr(min_length=1, max_length=80) = Field(default="BRONZE")  # type: ignore
    balance: int | None = None


class SetBalanceRequest(BaseModel):
    balance: int


class CreateHistoryRequest(BaseModel):
    ticketUid: UUID
    balanceDiff: int
    operationType: constr(min_length=1, max_length=20)  # type: ignore


class HistoryItem(BaseModel):
    date: datetime
    ticketUid: UUID
    balanceDiff: int
    operationType: str


class MeResponse(BaseModel):
    balance: int
    status: str
    history: list[HistoryItem]
