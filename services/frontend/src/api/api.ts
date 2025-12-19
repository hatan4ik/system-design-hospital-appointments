import axios from 'axios';
import { Appointment } from './schemas';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAvailability = async (providerId: string, start: Date, end: Date, slotMinutes: number) => {
  const params = {
    provider_id: providerId,
    start: start.toISOString(),
    end: end.toISOString(),
    slot_minutes: slotMinutes,
  };
  const response = await apiClient.get('/availability', { params });
  return response.data;
};

export const bookAppointment = async (data: {
  patient_id: string;
  provider_id: string;
  visit_type: string;
  start_ts: string;
  end_ts: string;
  location_id: string;
}, idempotencyKey: string) => {
  const response = await apiClient.post('/appointments', data, {
    headers: {
      'Idempotency-Key': idempotencyKey,
    },
  });
  return response.data;
};

export const getAppointment = async (appointmentId: string): Promise<Appointment> => {
    const response = await apiClient.get(`/appointments/${appointmentId}`);
    return response.data;
};
