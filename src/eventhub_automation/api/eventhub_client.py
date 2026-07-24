from dataclasses import dataclass
from typing import Any

import requests
from requests import Response

from eventhub_automation.api.assertions import parse_data, parse_data_list
from eventhub_automation.api.models import BookingResource, EventResource
from eventhub_automation.data.users import BookingCustomer, EventData


@dataclass
class EventHubClient:
    base_url: str
    token: str | None = None

    def __post_init__(self) -> None:
        self.base_url = self._normalize_api_url(self.base_url)
        self.session = requests.Session()
        if self.token:
            self.set_token(self.token)

    def set_token(self, token: str) -> None:
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def login(self, email: str, password: str) -> Response:
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password},
            timeout=15,
        )
        if response.ok and response.json().get("token"):
            self.set_token(response.json()["token"])
        return response

    def register(self, email: str, password: str) -> Response:
        response = self.session.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "password": password},
            timeout=15,
        )
        if response.ok and response.json().get("token"):
            self.set_token(response.json()["token"])
        return response

    def me(self) -> Response:
        return self.session.get(f"{self.base_url}/auth/me", timeout=15)

    def health_check(self) -> Response:
        return self.session.get(f"{self.base_url}/health", timeout=15)

    def config(self) -> Response:
        return self.session.get(f"{self.base_url}/config", timeout=15)

    def list_events(self) -> Response:
        return self.session.get(f"{self.base_url}/events", timeout=15)

    def events(self) -> list[EventResource]:
        return parse_data_list(self.list_events(), EventResource)

    def find_event_by_title(self, event_title: str) -> dict[str, Any] | None:
        response = self.list_events()
        response.raise_for_status()
        for event in response.json()["data"]:
            if event["title"] == event_title:
                return event
        return None

    def delete_event_by_title_if_present(self, event_title: str) -> None:
        event = self.find_event_by_title(event_title)
        if event:
            self.delete_event(event["id"])

    def get_event(self, event_id: int) -> Response:
        return self.session.get(f"{self.base_url}/events/{event_id}", timeout=15)

    def event(self, event_id: int) -> EventResource:
        return parse_data(self.get_event(event_id), EventResource)

    def create_event(self, event: EventData) -> Response:
        return self.session.post(
            f"{self.base_url}/events",
            json=self._event_payload(event),
            timeout=15,
        )

    def create_event_with_payload(self, payload: dict[str, Any]) -> Response:
        return self.session.post(f"{self.base_url}/events", json=payload, timeout=15)

    def update_event(self, event_id: int, event: EventData) -> Response:
        return self.session.put(
            f"{self.base_url}/events/{event_id}",
            json=self._event_payload(event),
            timeout=15,
        )

    def delete_event(self, event_id: int) -> Response:
        return self.session.delete(f"{self.base_url}/events/{event_id}", timeout=15)

    def list_bookings(self) -> Response:
        return self.session.get(f"{self.base_url}/bookings", timeout=15)

    def bookings(self) -> list[BookingResource]:
        return parse_data_list(self.list_bookings(), BookingResource)

    def get_booking(self, booking_id: int) -> Response:
        return self.session.get(f"{self.base_url}/bookings/{booking_id}", timeout=15)

    def booking(self, booking_id: int) -> BookingResource:
        return parse_data(self.get_booking(booking_id), BookingResource)

    def get_booking_by_reference(self, booking_reference: str) -> Response:
        return self.session.get(f"{self.base_url}/bookings/ref/{booking_reference}", timeout=15)

    def create_booking(
        self,
        event_id: int,
        customer: BookingCustomer,
        quantity: int = 1,
    ) -> Response:
        return self.session.post(
            f"{self.base_url}/bookings",
            json={
                "eventId": event_id,
                "customerName": customer.full_name,
                "customerEmail": customer.email,
                "customerPhone": customer.phone,
                "quantity": quantity,
            },
            timeout=15,
        )

    def cancel_booking(self, booking_id: int) -> Response:
        return self.session.delete(f"{self.base_url}/bookings/{booking_id}", timeout=15)

    @staticmethod
    def _normalize_api_url(base_url: str) -> str:
        base_url = base_url.rstrip("/")
        if not base_url.endswith("/api"):
            return f"{base_url}/api"
        return base_url

    @staticmethod
    def _event_payload(event: EventData) -> dict[str, Any]:
        return {
            "title": event.title,
            "description": event.description,
            "category": event.category,
            "city": event.city,
            "venue": event.venue,
            "eventDate": event.date_time,
            "price": int(event.price),
            "totalSeats": int(event.total_seats),
        }
