#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

UTC = timezone.utc
SLOT_MINUTES = 15
SLOT = timedelta(minutes=SLOT_MINUTES)

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph",
    "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy",
    "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna",
    "Joshua", "Michelle", "Kenneth", "Dorothy", "Kevin", "Carol", "Brian",
    "Amanda", "George", "Melissa", "Edward", "Deborah", "Ronald", "Stephanie",
    "Timothy", "Rebecca", "Jason", "Laura", "Jeffrey", "Helen", "Ryan", "Sharon",
    "Gary", "Cynthia",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner",
    "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
]

SPECIALTIES = [
    "Cardiology", "Dermatology", "Endocrinology", "Family Medicine",
    "Gastroenterology", "Neurology", "Obstetrics", "Oncology", "Orthopedics",
    "Pediatrics", "Psychiatry", "Radiology", "Urology", "Urgent Care",
    "Ophthalmology", "Pulmonology",
]

LOCATION_IDS = ["loc_1", "loc_2", "loc_3", "loc_4", "loc_5"]

VISIT_TYPES_BY_SLOTS = {
    1: ["FOLLOW_UP_15", "URGENT_15"],
    2: ["NEW_PATIENT_30", "THERAPY_30"],
    3: ["ANNUAL_45"],
    4: ["CONSULT_60"],
}

EMAIL_DOMAINS = ["example.com", "example.org", "demohealth.test", "clinic.example"]
AREA_CODES = ["212", "213", "305", "312", "415", "503", "617", "702", "808", "917"]


@dataclass
class Patient:
    id: str
    full_name: str
    phone: str | None
    email: str | None


@dataclass
class Provider:
    id: str
    full_name: str
    specialty: str
    location_id: str


class Jsonb:
    def __init__(self, value: dict) -> None:
        self.value = value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic patient/provider/appointment data.",
    )
    parser.add_argument("--patients", type=int, default=500, help="200-1000 recommended")
    parser.add_argument("--providers", type=int, default=25)
    parser.add_argument("--days", type=int, default=21)
    parser.add_argument("--start-date", default="2025-12-15", help="YYYY-MM-DD")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--fill-rate", type=float, default=0.55, help="0.1 to 0.9")
    parser.add_argument("--truncate", action="store_true", help="Add TRUNCATE statements")
    parser.add_argument("--output", default=None, help="Write SQL to a file")
    parser.add_argument("--stdout", action="store_true", help="Print SQL to stdout")
    parser.add_argument("--load", action="store_true", help="Load directly with psycopg")
    parser.add_argument("--dsn", default="postgresql://postgres:postgres@localhost:5432/postgres")
    return parser.parse_args()


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise SystemExit(f"Invalid --start-date {value}. Use YYYY-MM-DD.") from exc


def validate_args(args: argparse.Namespace) -> None:
    if not 200 <= args.patients <= 1000:
        raise SystemExit("--patients must be between 200 and 1000.")
    if args.providers < 1:
        raise SystemExit("--providers must be >= 1.")
    if args.days < 7:
        raise SystemExit("--days must be >= 7.")
    if not 0.1 <= args.fill_rate <= 0.9:
        raise SystemExit("--fill-rate must be between 0.1 and 0.9.")


def name_pairs(count: int, rnd: random.Random) -> list[tuple[str, str]]:
    combos = [(first, last) for first in FIRST_NAMES for last in LAST_NAMES]
    rnd.shuffle(combos)
    if count > len(combos):
        raise SystemExit("Not enough unique name combinations for requested count.")
    return combos[:count]


def build_phone_pool(rnd: random.Random) -> list[str]:
    pool = []
    for area in AREA_CODES:
        for line in range(100, 200):
            pool.append(f"{area}-555-{line:04d}")
    rnd.shuffle(pool)
    return pool


def make_email(full_name: str, rnd: random.Random, used: set[str]) -> str:
    base = "".join(ch for ch in full_name.lower() if ch.isalpha() or ch == " ").strip()
    local = ".".join(base.split())
    domain = rnd.choice(EMAIL_DOMAINS)
    candidate = f"{local}@{domain}"
    if candidate not in used:
        used.add(candidate)
        return candidate
    suffix = 2
    while True:
        candidate = f"{local}{suffix}@{domain}"
        if candidate not in used:
            used.add(candidate)
            return candidate
        suffix += 1


def random_uuid(rnd: random.Random) -> str:
    chars = "".join(rnd.choices("0123456789abcdef", k=32))
    return f"{chars[:8]}-{chars[8:12]}-{chars[12:16]}-{chars[16:20]}-{chars[20:]}"


def request_hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def generate_patients(count: int, rnd: random.Random) -> list[Patient]:
    pairs = name_pairs(count, rnd)
    phone_pool = build_phone_pool(rnd)
    used_emails: set[str] = set()
    patients = []
    phone_idx = 0
    for idx, (first, last) in enumerate(pairs, start=1):
        full_name = f"{first} {last}"
        phone = None
        email = None
        if rnd.random() > 0.12 and phone_idx < len(phone_pool):
            phone = phone_pool[phone_idx]
            phone_idx += 1
        if rnd.random() > 0.08:
            email = make_email(full_name, rnd, used_emails)
        patients.append(Patient(id=f"pat_{idx}", full_name=full_name, phone=phone, email=email))
    return patients


def generate_providers(count: int, rnd: random.Random) -> list[Provider]:
    pairs = name_pairs(count, rnd)
    providers = []
    for idx, (first, last) in enumerate(pairs, start=1):
        providers.append(
            Provider(
                id=f"prov_{idx}",
                full_name=f"{first} {last}",
                specialty=rnd.choice(SPECIALTIES),
                location_id=rnd.choice(LOCATION_IDS),
            )
        )
    return providers


def generate_schedules(
    providers: list[Provider],
    start_date: date,
    days: int,
    rnd: random.Random,
) -> tuple[list[tuple], dict[str, dict[date, tuple[datetime, datetime, list[tuple[datetime, datetime]]]]]]:
    schedules = []
    schedule_map: dict[str, dict[date, tuple[datetime, datetime, list[tuple[datetime, datetime]]]]] = {}
    sched_idx = 1
    for provider in providers:
        per_day = {}
        for day_offset in range(days):
            current = start_date + timedelta(days=day_offset)
            if current.weekday() >= 5:
                continue
            shift_start = datetime.combine(current, time(9, 0), tzinfo=UTC)
            shift_end = datetime.combine(current, time(17, 0), tzinfo=UTC)
            schedules.append((f"sch_{sched_idx:06d}", provider.id, shift_start, shift_end, "SHIFT"))
            sched_idx += 1
            blocks = []
            break_start = datetime.combine(current, time(12, 0), tzinfo=UTC)
            break_end = datetime.combine(current, time(13, 0), tzinfo=UTC)
            schedules.append((f"sch_{sched_idx:06d}", provider.id, break_start, break_end, "BREAK"))
            sched_idx += 1
            blocks.append((break_start, break_end))
            if rnd.random() < 0.15:
                block_start = datetime.combine(current, time(15, 30), tzinfo=UTC)
                block_end = datetime.combine(current, time(16, 0), tzinfo=UTC)
                schedules.append((f"sch_{sched_idx:06d}", provider.id, block_start, block_end, "BLOCK"))
                sched_idx += 1
                blocks.append((block_start, block_end))
            per_day[current] = (shift_start, shift_end, blocks)
        schedule_map[provider.id] = per_day
    return schedules, schedule_map


def find_possible_starts(blocked: list[bool], occupied: list[bool], length: int) -> list[int]:
    possible = []
    max_start = len(blocked) - length
    for i in range(max_start + 1):
        ok = True
        for j in range(i, i + length):
            if blocked[j] or occupied[j]:
                ok = False
                break
        if ok:
            possible.append(i)
    return possible


def choose_status(start_ts: datetime, ref_now: datetime, rnd: random.Random) -> str:
    if start_ts < ref_now:
        options = ["COMPLETED", "NO_SHOW", "CANCELLED", "CHECKED_IN", "CONFIRMED", "EXPIRED"]
        weights = [0.5, 0.1, 0.15, 0.1, 0.1, 0.05]
    else:
        options = ["CONFIRMED", "HELD", "CANCELLED"]
        weights = [0.8, 0.1, 0.1]
    return rnd.choices(options, weights=weights, k=1)[0]


def generate_appointments(
    patients: list[Patient],
    providers: list[Provider],
    schedule_map: dict[str, dict[date, tuple[datetime, datetime, list[tuple[datetime, datetime]]]]],
    start_date: date,
    days: int,
    fill_rate: float,
    rnd: random.Random,
) -> tuple[list[tuple], list[tuple], list[tuple]]:
    appointments = []
    audits = []
    idempotency = []
    apt_idx = 1
    ref_now = datetime.combine(start_date, time(0, 0), tzinfo=UTC) + timedelta(days=days // 2)
    patient_ids = [p.id for p in patients]
    frequent = set(rnd.sample(patient_ids, k=max(1, len(patient_ids) // 5)))
    frequent_list = sorted(frequent)
    length_weights = [0.4, 0.35, 0.15, 0.1]
    for provider in providers:
        per_day = schedule_map.get(provider.id, {})
        for current_day, (shift_start, shift_end, blocks) in per_day.items():
            total_slots = int((shift_end - shift_start) / SLOT)
            blocked = [False] * total_slots
            for b_start, b_end in blocks:
                for i in range(total_slots):
                    slot_start = shift_start + SLOT * i
                    slot_end = slot_start + SLOT
                    if not (slot_end <= b_start or slot_start >= b_end):
                        blocked[i] = True
            occupied = [False] * total_slots
            available_slots = sum(1 for i in range(total_slots) if not blocked[i])
            target_occupied = int(available_slots * fill_rate)
            occupied_count = 0
            attempts = 0
            max_attempts = available_slots * 4
            while occupied_count < target_occupied and attempts < max_attempts:
                attempts += 1
                length_slots = rnd.choices([1, 2, 3, 4], weights=length_weights, k=1)[0]
                possible = find_possible_starts(blocked, occupied, length_slots)
                if not possible:
                    for alt in [1, 2, 3, 4]:
                        possible = find_possible_starts(blocked, occupied, alt)
                        if possible:
                            length_slots = alt
                            break
                if not possible:
                    break
                start_idx = rnd.choice(possible)
                for j in range(start_idx, start_idx + length_slots):
                    occupied[j] = True
                occupied_count += length_slots
                start_ts = shift_start + SLOT * start_idx
                end_ts = start_ts + SLOT * length_slots
                if rnd.random() < 0.6:
                    patient_id = rnd.choice(frequent_list)
                else:
                    patient_id = rnd.choice(patient_ids)
                visit_type = rnd.choice(VISIT_TYPES_BY_SLOTS[length_slots])
                status = choose_status(start_ts, ref_now, rnd)
                appointment_id = f"apt_{apt_idx:06d}"
                apt_idx += 1
                appointments.append(
                    (
                        appointment_id,
                        patient_id,
                        provider.id,
                        start_ts,
                        end_ts,
                        status,
                        visit_type,
                        provider.location_id,
                    )
                )
                payload = {
                    "appointment_id": appointment_id,
                    "patient_id": patient_id,
                    "provider_id": provider.id,
                    "start_ts": start_ts.isoformat(),
                    "end_ts": end_ts.isoformat(),
                    "status": status,
                    "visit_type": visit_type,
                    "location_id": provider.location_id,
                }
                audits.append(
                    (
                        appointment_id,
                        patient_id,
                        f"APPOINTMENT_{status}",
                        start_ts.isoformat(),
                        Jsonb(payload),
                    )
                )
                if status == "CONFIRMED":
                    idem_key = random_uuid(rnd)
                    req_payload = {
                        "patient_id": patient_id,
                        "provider_id": provider.id,
                        "visit_type": visit_type,
                        "start_ts": start_ts.isoformat(),
                        "end_ts": end_ts.isoformat(),
                        "location_id": provider.location_id,
                    }
                    idempotency.append(
                        (
                            idem_key,
                            patient_id,
                            request_hash(req_payload),
                            json.dumps({"appointment_id": appointment_id, "status": "CONFIRMED"}),
                        )
                    )
    return appointments, audits, idempotency


def sql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, Jsonb):
        blob = json.dumps(value.value, sort_keys=True)
        return f"'{blob.replace(\"'\", \"''\")}'::jsonb"
    if isinstance(value, datetime):
        return f"'{value.isoformat()}'"
    if isinstance(value, str):
        return f"'{value.replace(\"'\", \"''\")}'"
    return str(value)


def render_insert(table: str, columns: list[str], rows: list[tuple]) -> list[str]:
    if not rows:
        return []
    lines = [f"INSERT INTO {table} ({', '.join(columns)}) VALUES"]
    for idx, row in enumerate(rows):
        values = ", ".join(sql_literal(value) for value in row)
        suffix = "," if idx < len(rows) - 1 else ";"
        lines.append(f"  ({values}){suffix}")
    return lines


def generate_sql(
    patients: list[Patient],
    providers: list[Provider],
    schedules: list[tuple],
    appointments: list[tuple],
    idempotency: list[tuple],
    audits: list[tuple],
    args: argparse.Namespace,
) -> str:
    lines = [
        "-- Synthetic seed data generated by labs/01-local-demo/seed_data.py",
        f"-- patients={len(patients)} providers={len(providers)} schedules={len(schedules)} appointments={len(appointments)}",
        f"-- seed={args.seed} start_date={args.start_date} days={args.days} fill_rate={args.fill_rate}",
    ]
    if args.truncate:
        lines.append(
            "TRUNCATE TABLE appointment_audit, idempotency_keys, appointments, provider_schedules, providers, patients RESTART IDENTITY;"
        )
    lines.extend(
        render_insert(
            "patients",
            ["id", "full_name", "phone", "email"],
            [(p.id, p.full_name, p.phone, p.email) for p in patients],
        )
    )
    lines.extend(
        render_insert(
            "providers",
            ["id", "full_name", "specialty", "location_id"],
            [(p.id, p.full_name, p.specialty, p.location_id) for p in providers],
        )
    )
    lines.extend(
        render_insert(
            "provider_schedules",
            ["id", "provider_id", "start_ts", "end_ts", "kind"],
            schedules,
        )
    )
    lines.extend(
        render_insert(
            "appointments",
            ["id", "patient_id", "provider_id", "start_ts", "end_ts", "status", "visit_type", "location_id"],
            appointments,
        )
    )
    lines.extend(
        render_insert(
            "idempotency_keys",
            ["idempotency_key", "user_id", "request_hash", "response_ref"],
            idempotency,
        )
    )
    lines.extend(
        render_insert(
            "appointment_audit",
            ["appointment_id", "actor_id", "action", "ts", "payload"],
            audits,
        )
    )
    return "\n".join(lines) + "\n"


def write_output(sql: str, output_path: str | None, stdout: bool) -> None:
    if stdout or not output_path:
        sys.stdout.write(sql)
        return
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(sql)


def load_sql(sql: str, dsn: str) -> None:
    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit("psycopg is required for --load. Install with pip.") from exc
    statements = [stmt.strip() for stmt in sql.split(";\n") if stmt.strip()]
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()


def main() -> None:
    args = parse_args()
    validate_args(args)
    rnd = random.Random(args.seed)
    start_date = parse_date(args.start_date)

    patients = generate_patients(args.patients, rnd)
    providers = generate_providers(args.providers, rnd)
    schedules, schedule_map = generate_schedules(providers, start_date, args.days, rnd)
    appointments, audits, idempotency = generate_appointments(
        patients, providers, schedule_map, start_date, args.days, args.fill_rate, rnd
    )
    sql = generate_sql(patients, providers, schedules, appointments, idempotency, audits, args)

    output_path = args.output
    if not output_path and not args.stdout:
        output_path = os.path.join(os.path.dirname(__file__), "seed.sql")
    write_output(sql, output_path, args.stdout)

    if args.load:
        load_sql(sql, args.dsn)


if __name__ == "__main__":
    main()
