from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiEnvelope(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool | None = None
    data: Any | None = None
    error: str | None = None
    details: list[dict[str, Any]] = Field(default_factory=list)


class UserResource(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    email: str
    name: str | None = None


class EventResource(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    title: str
    description: str | None = None
    category: str | None = None
    city: str | None = None
    venue: str | None = None
    price: str | int | None = None
    total_seats: int | None = Field(default=None, alias="totalSeats")
    available_seats: int | None = Field(default=None, alias="availableSeats")


class BookingResource(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    booking_ref: str | None = Field(default=None, alias="bookingRef")
    event_id: int | None = Field(default=None, alias="eventId")
    customer_name: str | None = Field(default=None, alias="customerName")
    customer_email: str | None = Field(default=None, alias="customerEmail")
    quantity: int | None = None
    total_price: str | int | None = Field(default=None, alias="totalPrice")
