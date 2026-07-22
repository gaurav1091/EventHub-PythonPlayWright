from uuid import uuid4

from eventhub_automation.data.users import BookingCustomer, EventData


class CustomerFactory:
    @staticmethod
    def booking_customer(
        name_prefix: str = "Codex E2E",
        email_prefix: str = "codex.e2e",
    ) -> BookingCustomer:
        unique_id = uuid4().hex[:6]
        return BookingCustomer(
            full_name=f"{name_prefix} {unique_id}",
            email=f"{email_prefix}+{unique_id}@example.com",
            phone="9876500001",
        )


class EventFactory:
    @staticmethod
    def workshop(title_prefix: str = "Codex E2E Workshop") -> EventData:
        return EventData(
            title=f"{title_prefix} {uuid4().hex[:6]}",
            description="Temporary event created by the automated E2E suite.",
            category="Workshop",
            city="Pune",
            venue="Codex QA Lab",
            date_time="2026-12-15T10:30",
            price="99",
            total_seats="25",
        )
