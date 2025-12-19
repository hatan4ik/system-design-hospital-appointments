# Frontend

This directory contains the frontend application for the hospital appointment system. It is a single-page application built with React, TypeScript, and Vite.

## How to Run

1.  **Install dependencies:**
    ```bash
    npm install
    ```
2.  **Run the development server:**
    ```bash
    npm run dev
    ```
    This will start the development server at `http://localhost:5173`.

## Frontend and Backend Interaction

The frontend application communicates with the backend services through a REST API. The API client is defined in `src/api/api.ts`.

### API Client

The `apiClient` is an Axios instance configured to make requests to the backend. The `baseURL` is set to `/api`, which means that all requests will be proxied to the backend services. This is configured in `vite.config.ts`.

### Data Fetching

We use TanStack Query (`@tanstack/react-query`) to manage data fetching, caching, and state management. This simplifies the process of fetching data from the backend and keeps the UI in sync with the server state.

### Endpoints

The frontend consumes the following endpoints:

*   **`GET /availability`**: Fetches available appointment slots.
    *   Used in: `src/components/availability/AvailabilityViewer.tsx`
*   **`POST /appointments`**: Books a new appointment.
    *   Used in: `src/components/booking/BookingForm.tsx`
*   **`GET /appointments/{appointmentId}`**: Fetches a single appointment.
    *   Used in: `src/api/api.ts` (but not yet used in any component)
