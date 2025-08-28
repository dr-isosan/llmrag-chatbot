import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import './App.css';
import AnimatedBackground from './components/AnimatedBackground';
import ChatBot from './components/ChatBot';
import { NotificationProvider } from './components/NotificationProvider';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AdminPanel from './components/AdminPanel';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#4a90e2',
      light: '#7bb3f0',
      dark: '#2e5d8c',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#6c757d',
      light: '#9ca5ad',
      dark: '#495057',
      contrastText: '#ffffff',
    },
    background: {
      default: '#0a0a0a',
      paper: 'rgba(20, 20, 20, 0.95)',
    },
    text: {
      primary: '#ffffff',
      secondary: '#e0e0e0',
    },
    success: {
      main: '#00c851',
      light: '#44d977',
      dark: '#009639',
    },
    warning: {
      main: '#ffbb33',
      light: '#ffcd5c',
      dark: '#cc9426',
    },
    error: {
      main: '#ff4444',
      light: '#ff7777',
      dark: '#cc3636',
    },
    info: {
      main: '#33b5e5',
      light: '#5cc4ea',
      dark: '#2991b7',
    },
    divider: 'rgba(100, 150, 200, 0.2)',
  },
  typography: {
    fontFamily: '"Inter", "JetBrains Mono", "SF Pro Display", "Roboto", sans-serif',
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.025em',
    },
    h6: {
      fontWeight: 600,
      letterSpacing: '-0.015em',
    },
    body1: {
      fontSize: '0.95rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.85rem',
      opacity: 0.8,
    },
  },
  shape: {
    borderRadius: 16,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(100, 150, 200, 0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 8,
          padding: '8px 16px',
        },
        contained: {
          background: '#4a90e2',
          '&:hover': {
            background: '#2e5d8c',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            background: 'rgba(255, 255, 255, 0.05)',
            '& fieldset': {
              borderColor: 'rgba(100, 150, 200, 0.2)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(100, 150, 200, 0.3)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#4a90e2',
            },
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(100, 150, 200, 0.1)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'rgba(74, 144, 226, 0.9)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
  },
});

function App() {
  // Örnek istatistik verisi (backend entegrasyonu sonrası API'den alınacak)
  const dummyStats = {
    totalQuestions: 123,
    uniqueQuestions: 87,
    topSources: [
      { source: 'eduroam_data.json', count: 45 },
      { source: 'kalite.pdf', count: 22 },
      { source: 'omü.pdf', count: 15 },
      { source: 'yönerge.pdf', count: 10 },
      { source: 'diğer.pdf', count: 7 },
    ],
    topQuestions: [
      { question: 'Eduroam şifremi nasıl alırım?', count: 12 },
      { question: 'WiFi bağlantı sorunu', count: 9 },
      { question: 'Kalite yönetim sistemi nedir?', count: 7 },
      { question: 'OMÜ öğrenci işleri', count: 5 },
      { question: 'Ders kaydı nasıl yapılır?', count: 4 },
    ],
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <NotificationProvider>
        <Router>
          <div className="App">
            <AnimatedBackground />
            <Routes>
              <Route path="/" element={<ChatBot />} />
              <Route path="/admin" element={<AdminPanel />} />
            </Routes>
          </div>
        </Router>
      </NotificationProvider>
    </ThemeProvider>
  );
}

export default App;
