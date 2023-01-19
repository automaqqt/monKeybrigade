import { Grid, Box } from '@mui/material';
import Container from '@mui/material/Container';
import DarkCard from '../components/cards/DarkCard'
import { Typography } from '@mui/material';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';

export default function Off() {

  return (
    <Container>
      <Box
          sx={{
            bgcolor: 'background.paper',
            pt: 8,
            pb: 6,
          }}
        >
          <Container maxWidth="sm">
            <Typography
              component="h1"
              variant="h1"
              align="center"
              color="text.primary"
              gutterBottom
            >
              Your device is offline.
            </Typography>
            <Typography variant="h5" align="center" color="text.secondary" paragraph>
              To use this app you need a working internet connection.
            </Typography>
          </Container>
        </Box>
      <Grid item xs={12} md={12}>
          <DarkCard icon={<PowerSettingsNewIcon/>} label={"service status"} value={"Offline"} />
      </Grid>
    </Container>
  );
}