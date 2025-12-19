import { Route, Routes } from 'react-router-dom';
import { BookingForm } from './components/booking/BookingForm';
import { MyAppointments } from './components/appointments/MyAppointments';
import { Layout } from './components/layout/Layout';
import { Box } from '@mui/material';
import { AvailabilityViewer } from './components/availability/AvailabilityViewer';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={
          <Box>
            <AvailabilityViewer />
            <BookingForm />
          </Box>
        } />
        <Route path="appointments" element={<MyAppointments />} />
      </Route>
    </Routes>
  )
}

export default App
