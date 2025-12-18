# Testing the Appointment Service

This document outlines the testing strategy for the `appointment-service` and provides details on the implemented unit tests.

## How to Run Tests

1.  **Navigate to the service directory:**
    ```bash
    cd services/appointment_service
    ```

2.  **Install dependencies (including test dependencies):**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the tests:**
    ```bash
    python -m pytest
    ```

## Testing Strategy

The unit tests are designed to run in isolation without any external dependencies (like a running PostgreSQL database or Redis instance). This is achieved by:

-   **Mocking Redis:** The `fakeredis` library is used to create an in-memory Redis server for each test session.
-   **Mocking PostgreSQL:** The `unittest.mock.patch` utility is used to mock the `psycopg` library. This allows us to simulate database responses and assert that the correct SQL commands are being executed (e.g., `COMMIT`, `ROLLBACK`).

## Test Suite Breakdown

The test suite is located in `app/test_main.py`.

### Fixtures

-   `mock_redis`: This `pytest` fixture sets up and tears down a `fakeredis` instance for tests that require Redis.
-   `mock_psycopg`: This fixture patches the `psycopg` library and provides a mock cursor object, allowing us to control the return values of database queries.

### Test Cases

-   `test_healthz()`: A simple test to ensure the `/healthz` endpoint is working and returns a `200 OK` status.

-   `test_book_missing_idempotency_key()`: Verifies that a `400 Bad Request` is returned if the `Idempotency-Key` header is missing from a booking request.

-   `test_book_cached_response(mock_redis)`: Ensures that if a response for a given `Idempotency-Key` is already cached in Redis, the service returns the cached response without hitting the database.

-   `test_book_busy_retry(mock_redis)`: Simulates a scenario where another request is currently processing for the same provider and day. It verifies that the service returns a `409 Conflict` with a "Busy, retry" message.

-   `test_book_time_conflict(mock_redis, mock_psycopg)`: Tests the case where there is a conflicting appointment in the database. It ensures that the database transaction is rolled back and a `409 Conflict` with a "Time conflict" message is returned.

-   `test_book_successful(mock_redis, mock_psycopg)`: Covers the "happy path" scenario. It verifies that:
    -   A new appointment is successfully created in the database (`COMMIT` is called).
    -   A `200 OK` status is returned with the new appointment's details.
    -   The successful response is cached in Redis against the `Idempotency-Key` to handle future retries.
