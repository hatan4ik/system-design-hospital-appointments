export interface Appointment {
    id: string;
    patient_id: string;
    provider_id: string;
    start_ts: string;
    end_ts: string;
    status: string;
    visit_type: string;
    location_id: string;
}

export interface AvailabilitySlot {
    start: string;
    end: string;
}

export interface Availability {
    provider_id: string;
    from: string;
    to: string;
    slots: AvailabilitySlot[];
}
