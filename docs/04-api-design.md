# API Design

This document outlines the design of the RESTful APIs for the Hospital Appointment & Scheduling System. The APIs are designed to be intuitive, consistent, and easy to use.

## 1. Design Principles

-   **RESTful:** The API follows RESTful principles, using standard HTTP verbs and status codes.
-   **JSON:** All request and response bodies are in JSON format.
-   **Idempotency:** All `POST` requests that create a resource support an `Idempotency-Key` header to prevent duplicate resource creation.
-   **Authentication:** All endpoints require authentication (e.g., via OAuth 2.0). The specific authentication mechanism is handled by the API Gateway.
-   **Error Handling:** The API uses standard HTTP status codes to indicate the success or failure of a request. Error responses include a `code` and a `message` field.

## 2. Patient-Facing APIs

### GET /providers

-   **Description:** Searches for available healthcare providers.
-   **Query Parameters:**
    -   `specialty` (string, optional): Filter by provider specialty (e.g., "Cardiology").
    -   `location` (string, optional): Filter by location (e.g., "San Francisco").
-   **Response (200 OK):**
    ```json
    {
      "providers": [
        {
          "id": "prov_123",
          "name": "Dr. Alice Smith",
          "specialty": "Cardiology"
        }
      ]
    }
    ```

### GET /availability

-   **Description:** Retrieves available appointment slots for a provider.
-   **Query Parameters:**
    -   `provider_id` (string, required): The ID of the provider.
    -   `start_date` (date, required): The start of the date range to search.
    -   `end_date` (date, required): The end of the date range to search.
    -   `visit_type_id` (string, required): The type of visit, which determines the slot duration.
-   **Response (200 OK):**
    ```json
    {
      "slots": [
        {
          "start_time": "2024-10-28T10:00:00Z",
          "end_time": "2024-10-28T10:30:00Z"
        }
      ]
    }
    ```

### POST /appointments

-   **Description:** Books a new appointment. This endpoint must be idempotent.
-   **Headers:**
    -   `Idempotency-Key` (string, required): A unique key to prevent duplicate bookings.
-   **Request Body:**
    ```json
    {
      "provider_id": "prov_123",
      "patient_id": "pat_456",
      "visit_type_id": "vt_789",
      "start_time": "2024-10-28T10:00:00Z"
    }
    ```
-   **Response (201 Created):**
    ```json
    {
      "id": "appt_abc",
      "status": "CONFIRMED",
      "start_time": "2024-10-28T10:00:00Z",
      "end_time": "2024-10-28T10:30:00Z"
    }
    ```
-   **Error Responses:**
    -   `409 Conflict`: If the requested slot is no longer available.

### POST /appointments/{id}/cancel

-   **Description:** Cancels an existing appointment.
-   **Parameters:**
    -   `id` (string, required): The ID of the appointment to cancel.
-   **Response (200 OK):**
    ```json
    {
      "id": "appt_abc",
      "status": "CANCELLED"
    }
    ```

### GET /appointments/{id}

-   **Description:** Retrieves the details of a single appointment.
-   **Parameters:**
    -   `id` (string, required): The ID of the appointment.
-   **Response (200 OK):**
    ```json
    {
      "id": "appt_abc",
      "status": "CONFIRMED",
      "start_time": "2024-10-28T10:00:00Z",
      "end_time": "2024-10-28T10:30:00Z",
      "provider": {
        "id": "prov_123",
        "name": "Dr. Alice Smith"
      },
      "patient": {
        "id": "pat_456",
        "name": "John Doe"
      }
    }
    ```

## 3. Staff & Admin APIs

These APIs are for internal use by hospital staff and administrators. They provide more extensive capabilities for managing schedules and overriding system behavior.

### Provider Schedule CRUD

-   `POST /providers/{provider_id}/schedules`: Create a new schedule block for a provider.
-   `PUT /providers/{provider_id}/schedules/{schedule_id}`: Update an existing schedule block.
-   `DELETE /providers/{provider_id}/schedules/{schedule_id}`: Remove a schedule block.

### Bulk Operations

-   `POST /schedules/reschedule`: A powerful endpoint for bulk rescheduling of appointments, for example, if a doctor calls in sick. This would be an asynchronous operation.

### Overrides

-   The staff-facing version of `POST /appointments` may include a flag like `"override_rules": true`, which would allow a scheduler to bypass certain business rules (e.g., double-booking). All such overrides must be logged in the audit trail.

## Next Steps

- **[05-core-architecture.md](./05-core-architecture.md):** The technical architecture that implements these APIs.