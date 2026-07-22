from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    email: str
    password: str


@dataclass(frozen=True)
class BookingCustomer:
    full_name: str
    email: str
    phone: str


@dataclass(frozen=True)
class EventData:
    title: str
    description: str
    category: str
    city: str
    venue: str
    date_time: str
    price: str
    total_seats: str
