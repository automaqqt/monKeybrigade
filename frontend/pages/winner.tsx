import Container from '@mui/material/Container';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import { useState } from 'react';
import DropsTable from '../components/DropsTable';

export default function Drops() {

  return (
    <Container>
      <DropsTable/>
    </Container>
  );
}
