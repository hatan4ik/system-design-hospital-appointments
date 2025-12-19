import { AppBar, Box, Button, Container, Toolbar, Typography } from '@mui/material';
import { Link, Outlet } from 'react-router-dom';

export const Layout = () => {
  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar component="nav">
        <Toolbar>
          <Typography
            variant="h6"
            component="div"
            sx={{ flexGrow: 1, display: { xs: 'none', sm: 'block' } }}
          >
            Hospital Appointments
          </Typography>
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <Button sx={{ color: '#fff' }} component={Link} to="/">
              Book Appointment
            </Button>
            <Button sx={{ color: '#fff' }} component={Link} to="/appointments">
              My Appointments
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ p: 3 }}>
        <Toolbar />
        <Container>
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
};
