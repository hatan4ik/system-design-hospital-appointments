import { Typography, CircularProgress, Alert, List, ListItem, ListItemText, Paper } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { getAvailability } from '../../api/api';
import { Availability } from '../../api/schemas';

export const AvailabilityViewer = () => {
  // Hardcoded for now, in a real app this would be dynamic
  const providerId = '1';
  const slotMinutes = 30;
  const start = new Date();
  const end = new Date();
  end.setDate(start.getDate() + 7);


  const { data, error, isLoading } = useQuery<Availability, Error>({
    queryKey: ['availability', providerId, start, end, slotMinutes],
    queryFn: () => getAvailability(providerId, start, end, slotMinutes),
  });

  if (isLoading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">{error.message}</Alert>;
  }

  return (
    <Paper elevation={3} sx={{ p: 2, mt: 2 }}>
      <Typography variant="h5" gutterBottom>Available Slots</Typography>
      <List>
        {data?.slots.map((slot, index) => (
          <ListItem key={index}>
            <ListItemText
              primary={`${new Date(slot.start).toLocaleTimeString()} - ${new Date(slot.end).toLocaleTimeString()}`}
              secondary={new Date(slot.start).toLocaleDateString()}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};
