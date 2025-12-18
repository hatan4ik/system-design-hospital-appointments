# Notifications & Waitlist

- Booking emits AppointmentCreated event
- Notification service sends confirmation + reminders
- Waitlist service watches for cancellations and offers slots with TTL

No-show reduction:
- confirmations with response
- automated re-offer on decline/cancel
