import pytest

from eventhub_automation.api.eventhub_client import EventHubClient
from eventhub_automation.data.factories import EventFactory
from eventhub_automation.flows.admin_event_flow import AdminEventFlow


@pytest.mark.e2e
@pytest.mark.admin
def test_admin_can_create_publish_and_delete_event(
    authenticated_page,
    settings,
    authenticated_api_client: EventHubClient,
):
    admin_event_flow = AdminEventFlow(authenticated_page, settings.base_url)
    event = EventFactory.workshop()

    try:
        admin_event_flow.create_event(event, "15 Dec 2026")
        admin_event_flow.open_published_event(event.title)

        admin_event_flow.event_detail_page.assert_event_details_visible(
            event.title,
            event.category,
            "$99",
        )
        admin_event_flow.event_detail_page.assert_description_visible(event.description)
    finally:
        admin_event_flow.delete_event_if_present(event.title)
        authenticated_api_client.delete_event_by_title_if_present(event.title)
