from .config import settings
import psycopg
from psycopg import conninfo

DB_CONNINFO = conninfo.make_conninfo(
    settings.DB_DSN,
    sslmode=settings.DB_SSLMODE,
    connect_timeout=settings.DB_CONNECT_TIMEOUT,
)

def get_db_connection():
    return psycopg.connect(conninfo=DB_CONNINFO)
