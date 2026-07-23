from collections.abc import Generator

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.data.users import BookingCustomer, EventData


class TestDataManager:
    __test__ = False

    def __init__(self, api_client: EventHubClient) -> None:
        self.api_client = api_client
        self._booking_ids: list[int] = []
        self._event_ids: list[int] = []

    def create_event(self, event: EventData) -> dict:
        response = self.api_client.create_event(event)
        response.raise_for_status()
        event_payload = response.json()["data"]
        self._event_ids.append(event_payload["id"])
        return event_payload

    def create_booking(
        self,
        event_id: int,
        customer: BookingCustomer,
        quantity: int = 1,
    ) -> dict:
        response = self.api_client.create_booking(event_id, customer, quantity=quantity)
        response.raise_for_status()
        booking_payload = response.json()["data"]
        self._booking_ids.append(booking_payload["id"])
        return booking_payload

    def track_event(self, event_id: int) -> None:
        if event_id not in self._event_ids:
            self._event_ids.append(event_id)

    def track_booking(self, booking_id: int) -> None:
        if booking_id not in self._booking_ids:
            self._booking_ids.append(booking_id)

    def delete_event_by_title_if_present(self, event_title: str) -> None:
        self.api_client.delete_event_by_title_if_present(event_title)

    def cleanup(self) -> None:
        for booking_id in reversed(self._booking_ids):
            self.api_client.cancel_booking(booking_id)
        self._booking_ids.clear()

        for event_id in reversed(self._event_ids):
            self.api_client.delete_event(event_id)
        self._event_ids.clear()


def managed_test_data(api_client: EventHubClient) -> Generator[TestDataManager, None, None]:
    manager = TestDataManager(api_client)
    try:
        yield manager
    finally:
        manager.cleanup()
