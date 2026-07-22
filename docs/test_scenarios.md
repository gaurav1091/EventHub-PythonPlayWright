# EventHub UI Automation Scenario Inventory

Generated from live exploration of `https://eventhub.rahulshettyacademy.com` using Playwright MCP on 22 July 2026.

## Smoke Scenarios

1. Registered user can log in and see the authenticated navigation.
2. User can open Events from the header and see upcoming event cards.
3. User can open an event details page from an event card.
4. User can book tickets for an event and see a booking confirmation reference.
5. Confirmed booking appears under My Bookings.
6. User can log out and is returned to the unauthenticated login experience.

## Authentication

1. Login page renders with email, password, Sign In, Register, and API Documentation links.
2. Valid registered credentials authenticate successfully.
3. Invalid password is rejected with an error message.
4. Invalid email format is rejected.
5. Empty email/password submission shows validation feedback.
6. Register link navigates to the registration page.
7. Authenticated-only routes redirect anonymous users to login.

## Home Page

1. Header shows Home, Events, My Bookings, API Docs, Admin, user email, and Logout.
2. Featured Events section shows seeded featured event cards.
3. Browse Events CTA opens `/events`.
4. My Bookings CTA opens `/bookings`.
5. Footer links render and point to expected destinations.

## Event Discovery

1. Events page renders search, category filter, city filter, and event cards.
2. Search by event title returns matching events.
3. Search by venue returns matching events.
4. Search with unmatched text displays "No events found".
5. Clear filters restores the default event list.
6. Category filter narrows results, for example Concert shows Hollywood Monsoon Night.
7. City filter narrows results, for example Delhi shows Dilli Diwali Mela.
8. Combining category and city filters returns the correct intersection or empty state.
9. Event card displays image, category, featured badge, date, venue/city, price, seats left, and Book Now.

## Event Details And Booking

1. Event detail page displays breadcrumb, title, category, featured badge, date, time, venue, city, availability, price, and description.
2. Ticket quantity starts at 1 and decrement is disabled.
3. Increment updates ticket count and total price.
4. Decrement updates ticket count and total price.
5. Ticket quantity cannot exceed available seats/max shown in the UI.
6. Empty booking form shows validation for name, email, and phone.
7. Invalid name shorter than 2 characters is rejected.
8. Invalid email is rejected.
9. Invalid phone number is rejected.
10. Valid customer details and quantity confirm the booking.
11. Booking confirmation shows reference, customer name, ticket quantity, and total.
12. Browse More Events returns to event discovery.
13. View My Bookings opens booking history.

## My Bookings

1. My Bookings page lists confirmed booking reference, status, event name, date, ticket count, city, booked date, and total.
2. New booking appears after confirmation.
3. Booking details action opens the booking details route or details view.
4. Cancel Booking cancels/removes the selected booking after confirmation.
5. Clear all bookings removes all user bookings and shows empty-state messaging.

## Admin Event Management

1. Admin Events page renders event creation form and All Events table.
2. Required admin fields are validated: title, category, city, venue, date/time, price, and total seats.
3. Admin can create a non-featured event with valid data.
4. Newly created event appears in the admin table.
5. Newly created event appears in Events discovery.
6. Created event can be edited if the UI exposes edit actions for user-created events.
7. Created event can be deleted if the UI exposes delete actions for user-created events.
8. Featured seed events are read-only.
9. User-created event limit behavior is respected: after 6 events, oldest event is replaced.

## Future API And Hybrid Scenarios

1. Login API returns token for valid credentials.
2. Events API returns the same seeded events shown in the UI.
3. Event detail API matches UI detail data.
4. Booking API can create test bookings for faster UI verification.
5. Booking API can clean test data before/after UI scenarios.
6. Admin/event API can create disposable events for UI search/filter/edit/delete tests.
7. Contract checks validate response status, schema, required fields, and business constraints.
