import { amber, teal } from '@mui/material/colors';
import { createTheme } from '@mui/material/styles';

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: teal,
    secondary: amber,
  },
});

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: amber,
    secondary: teal,
  },
});
