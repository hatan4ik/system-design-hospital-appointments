from datetime import datetime

def get_provider_schedules(cursor, provider_id: str, start: datetime, end: datetime):
    cursor.execute(
        """
        SELECT start_ts, end_ts, kind FROM provider_schedules
        WHERE provider_id = %s
          AND start_ts < %s AND end_ts > %s
        ORDER BY start_ts
        """,
        (provider_id, end, start),
    )
    return cursor.fetchall()

def get_appointments(cursor, provider_id: str, start: datetime, end: datetime):
    cursor.execute(
        """
        SELECT start_ts, end_ts FROM appointments
        WHERE provider_id = %s
          AND status IN ('HELD','CONFIRMED')
          AND start_ts < %s AND end_ts > %s
        ORDER BY start_ts
        """,
        (provider_id, end, start),
    )
    return cursor.fetchall()
