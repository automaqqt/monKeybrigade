import * as React from 'react';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';
import Image from 'next/image';

function Copyright() {
  return (
    <Typography variant="body2" color="text.secondary">
      {'Copyright © '}

      {new Date().getFullYear()}
      {'  '}
      <Link color="inherit" href="https://twitter.com/GCmstats">
        Green
      </Link>{'  '}
    </Typography>
  );
}

export default function StickyFooter() {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
      }}
    >

      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
        }}
      >




        <Grid container spacing={2} sx={{ display: 'flex', alignItems: 'center' }} >
          <Grid item xs={4} sm={6}>
            <Link href='https://www.cryptomonkeys.cc/monkeytrains' sx={{ textDecoration: 'none', paddingLeft: 2 }}>
              <Image src="/sticker.png" alt="miing Logo" width={120} height={120} />
            </Link>
          </Grid>
          <Grid item xs={8} sm={6} >
            <Container >
              <Typography variant="body1">
                This page is powered by <Link color="inherit" href="https://connect.cryptomonkeys.cc/">
                  connect.cryptomonKeys
                </Link>{' '}
              </Typography>
              <Copyright />
            </Container>

          </Grid>


        </Grid>



      </Box>
    </Box>
  );
}
