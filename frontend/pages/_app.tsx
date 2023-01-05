import { CacheProvider, EmotionCache } from '@emotion/react';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { IconButton } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { AppProps } from 'next/app';
import Head from 'next/head';
import { useEffect, useMemo, useState } from 'react';
import Navbar from '../components/Navbar';

import StickyFooter from '../components/StickyFooter';
import createEmotionCache from '../src/createEmotionCache';
import { darkTheme, lightTheme } from '../src/theme';
const clientSideEmotionCache = createEmotionCache();

interface MyAppProps extends AppProps {
  emotionCache?: EmotionCache;
}

export default function MyApp(props: MyAppProps) {
  const [mode, setMode] = useState<'light' | 'dark'>('dark');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const theme = window.localStorage.getItem('theme');
      if (theme === 'dark' || theme === 'light') {
        setMode(theme);
      } else {
        setMode(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'dark');
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('theme', mode);
    }
  }, [mode]);

  const colorMode = useMemo(
    () => ({
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
    }),
    []
  );

  const theme = useMemo(() => (mode === 'dark' ? darkTheme : lightTheme), [mode]);

  const ThemeToggleButton = () => (
    <IconButton onClick={colorMode.toggleColorMode}>
      {theme.palette.mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
    </IconButton>
  );

  const { Component, emotionCache = clientSideEmotionCache, pageProps } = props;
  return (
    <CacheProvider value={emotionCache}>
      <Head>
        <meta name='viewport' content='initial-scale=1, width=device-width' />
        <title>
          monKeybrigade
        </title>

        <meta name="description" content="monKeybrigade" />
        <meta name="keywords" content="NFT,WAX,cryptomonkeys,connect,Discord,Twitter,telegram" />
        <meta name="author" content="Green" />

        <meta name="twitter:card" content="summary" />
        <meta name="twitter:url" content="https://taco.cryptomonkeys.cc/" />
        <meta name="twitter:title" content="monKeybrigade" />
        <meta name="twitter:description" content="Earn cryptomonKeys by playing Taco Brigade!" />
        <meta name="twitter:image" content="https://taco.cryptomonkeys.cc/logo.png" />
        <meta name="twitter:site" content="@Crypt0monKeys" />

        <meta name="og:type" content="website" />
        <meta name="og:url" content="https://taco.cryptomonkeys.cc/" />
        <meta name="og:title" content="monKeybrigade" />
        <meta content="Earn cryptomonKeys by working on the monkeybrigade in Taco." property="og:description" />
        <meta content="taco.cryptomonkeys.cc" property="og:site_name" />
        <meta content='https://taco.cryptomonkeys.cc/logo.png' property='og:image' />
        <meta name="theme-color" content="#0006A7" />
        <link rel="apple-touch-icon" sizes="180x180" href="icon-192x192.png"></link>

      </Head>
      <ThemeProvider theme={theme}>

        <CssBaseline />
        <Navbar ThemeToggleButton={ThemeToggleButton} />
        <br />
        <Component {...pageProps} />

        <StickyFooter />
      </ThemeProvider>
    </CacheProvider>

  );
}
