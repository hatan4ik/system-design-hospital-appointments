import { Typography, TextField, Button, Paper, Box, CircularProgress, Alert } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { bookAppointment } from '../../api/api';
import { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

export const BookingForm = () => {
    const [patientId, setPatientId] = useState('');
    const [providerId, setProviderId] = useState('1'); // Hardcoded for now
    const [visitType, setVisitType] = useState('ROUTINE');
    const [startTime, setStartTime] = useState('');
    const [endTime, setEndTime] = useState('');
    const [locationId, setLocationId] = useState('1'); // Hardcoded for now

    const mutation = useMutation({
        mutationFn: (idempotencyKey: string) => bookAppointment({
            patient_id: patientId,
            provider_id: providerId,
            visit_type: visitType,
            start_ts: new Date(startTime).toISOString(),
            end_ts: new Date(endTime).toISOString(),
            location_id: locationId,
        }, idempotencyKey),
        onSuccess: () => {
            // In a real app, you would probably want to refetch the appointments
            // or navigate to a confirmation page.
            alert('Appointment booked successfully!');
        },
    });


    const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const idempotencyKey = uuidv4();
        mutation.mutate(idempotencyKey);
    };

    return (
        <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
            <Typography variant="h5" gutterBottom>Book Appointment</Typography>
            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    id="patientId"
                    label="Patient ID"
                    name="patientId"
                    autoFocus
                    value={patientId}
                    onChange={(e) => setPatientId(e.target.value)}
                />
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    id="startTime"
                    label="Start Time"
                    name="startTime"
                    type="datetime-local"
                    InputLabelProps={{
                        shrink: true,
                    }}
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                />
                <TextField
                    margin="normal"
                    required
                    fullWidth
                    id="endTime"
                    label="End Time"
                    name="endTime"
                    type="datetime-local"
                    InputLabelProps={{
                        shrink: true,
                    }}
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                />

                <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2 }}
                    disabled={mutation.isPending}
                >
                    {mutation.isPending ? <CircularProgress size={24} /> : 'Book'}
                </Button>
                {mutation.isError && (
                    <Alert severity="error">{mutation.error.message}</Alert>
                )}
            </Box>
        </Paper>
    );
};
