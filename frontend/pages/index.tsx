import { Grid } from '@mui/material';
import Container from '@mui/material/Container';
import DarkCard from '../components/cards/DarkCard'
import LightCard from '../components/cards/LightCard'

import humanizeDuration from "humanize-duration";

import axios from 'axios';
import useSWR from 'swr';
import Image from 'next/image'
import { Typography } from '@mui/material';
import PowerSettingsNewIcon from '@mui/icons-material/PowerSettingsNew';
import QueryBuilderIcon from '@mui/icons-material/QueryBuilder';
import MovingIcon from '@mui/icons-material/Moving';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import { Box, Stack, Button } from '@mui/material';

export default function Home() {
  const { data: db } = useSWR(
    ['https://taco.api.cryptomonkeys.cc/status_db'],
    (url) => axios.get(url).then((res) => res.data),
    { refreshInterval: 6000, }
  );
  if (!db) return (
    <Container>

      <Grid item xs={12} md={12}>
        <LightCard icon={<PowerSettingsNewIcon />} label={"service status"} value={"Offline"} />
      </Grid>
    </Container>

  );
  const next_elec = Date.now() - 2 * 3600000 - Date.parse(db.db_state.last_elec + "Z");
  let next_election = "verifying and raffling right now";
  if (next_elec < 0) {
    next_election = humanizeDuration(next_elec, { round: true });
  }
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
            <Box sx={{ display: { xs: 'none', md: 'flex' } }}>
              <Image src="/head.png" alt="mining Logo" width={550} height={90} />
            </Box>
            <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
              <Image src="/head.png" alt="mining Logo" width={340} height={60} />
            </Box>
          </Typography>
          <Typography variant="h5" align="center" color="text.secondary" paragraph>
            Welcome to monKeybrigade! You can earn cryptomonKeys by playing Taco Brigade and working for our venue.
          </Typography>
          <Stack
            sx={{ pt: 4 }}
            direction="row"
            spacing={2}
            justifyContent="center"
          >
            <Button variant="outlined" size='large' target="_blank" href="https://connect.cryptomonkeys.cc">Signup for monKeybrigade</Button>
            <Button variant="contained" size='large' target="_blank" href="https://www.cryptomonkeys.cc/monkeybrigade">How does this work?</Button>
          </Stack>
        </Container>
      </Box>
      <br />

      <Grid container spacing={2}>
        <Grid item xs={12} md={12}>
          <Typography variant='h5'>Distribution Status</Typography>
        </Grid>

        <Grid item xs={6} md={6}>
          <DarkCard icon={<QueryBuilderIcon />} label={"CD for raffle"} value={"72 hrs"} />
        </Grid>
        <Grid item xs={12} md={6}>
          <DarkCard icon={<CheckCircleOutlineIcon />} label={"eligible for next raffle"} value={db.db_state.eligible} />
        </Grid>

        <Grid item xs={12} md={12}>
          <DarkCard icon={<QueryBuilderIcon />} label={"next raffle in"} value={next_election} />
        </Grid>
        <Grid item xs={12} md={12}>
          <DarkCard icon={<HourglassEmptyIcon />} label={"total CMs distributed in week / month / 2022 / total"} value={db.db_state.mining_hist.join(" / ") + " / " + (db.db_state.mining_hist[2]).toString()} />
        </Grid>

        <Grid item xs={12} md={12}>
          <Typography variant='h5'>Database Status</Typography>
        </Grid>
        <Grid item xs={6} md={4}>
          <LightCard icon={<MovingIcon />} label={"mnky work last hr"} value={db.db_state.count_work[0]} />
        </Grid>
        <Grid item xs={6} md={4}>
          <LightCard icon={<MovingIcon />} label={"mnky work last 24 hrs"} value={db.db_state.count_work[1]} />
        </Grid>
        <Grid item xs={12} md={4}>
          <DarkCard icon={<MovingIcon />} label={"total work last hr"} value={db.db_state.count_work[2]} />
        </Grid>



      </Grid>
    </Container>
  );
}
