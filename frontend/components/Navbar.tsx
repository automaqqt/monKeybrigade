import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Menu from '@mui/material/Menu';
import MenuIcon from '@mui/icons-material/Menu';
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';

import Link from '../src/Link';

import Image from 'next/image';

const pages = ['Check', 'Work', 'Winner'];
import { useTheme } from '@mui/material/styles';

interface Props {
  ThemeToggleButton: React.ElementType;
}

const ResponsiveAppBar = ({ ThemeToggleButton }: Props) => {
  const [anchorElNav, setAnchorElNav] = React.useState(null);
  const theme = useTheme();

  const handleOpenNavMenu = (event: any) => {
    setAnchorElNav(event.currentTarget);
  };

  const handleCloseNavMenu = () => {
    setAnchorElNav(null);
  };

  const getURI = (page: string) => {
    return "/" + page.toLowerCase()
  };




  return (
    <AppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ mt:2, mb:-2, display: { xs: 'none', md: 'flex' } }}
          >
            <Link href='/' sx={{ textDecoration: 'none' }}>
              <Image src="/icon-192x192.png" alt="brigade Logo" width={80} height={80} />
            </Link>
          </Typography>

          <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleOpenNavMenu}
              color="inherit"
            >
              <MenuIcon />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorElNav}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
              open={Boolean(anchorElNav)}
              onClose={handleCloseNavMenu}
              sx={{
                display: { xs: 'block', md: 'none' },
              }}
            >
              <MenuItem key={"hoe"} onClick={handleCloseNavMenu}>
                <Link href={"/"} sx={{ textDecoration: 'none' }}>
                  <Typography textAlign="center">Home</Typography>
                </Link>
              </MenuItem>
              {pages.map((page) => (

                <MenuItem key={page} onClick={handleCloseNavMenu}>
                  <Link href={getURI(page)} sx={{ textDecoration: 'none' }}>
                    <Typography textAlign="center" >{page}</Typography>
                  </Link>
                </MenuItem>
              ))}
            </Menu>
          </Box>
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}
          >
            <Link href='/' sx={{ textDecoration: 'none' }}>
              <Image src="/logo.png" alt="brigade Logo" width={95} height={80} />
            </Link>
          </Typography>
          <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' }, justifyContent: 'center' }}>
            <Button
              key={"faef"}
              onClick={handleCloseNavMenu}
              sx={{ my: 2, color: 'white', display: 'block' }}
            >
              <Link href={"/"} sx={{ textDecoration: 'none', color: theme.palette.secondary.dark }}>
                <Typography fontWeight={700} textAlign="center">Home</Typography>
              </Link>
            </Button>
            {pages.map((page) => (
              <Button
                key={page}
                onClick={handleCloseNavMenu}
                sx={{ my: 2, color: 'white', display: 'block' }}
              >
                <Link href={getURI(page)} sx={{ textDecoration: 'none !important', color: theme.palette.secondary.dark }}>
                  <Typography fontWeight={700} textAlign="center">{page}</Typography>
                </Link>
              </Button>
            ))}
          </Box>

          <Box sx={{ flexGrow: 0 }}>

            <ThemeToggleButton />
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};
export default ResponsiveAppBar;

