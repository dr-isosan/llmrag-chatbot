import {
  SmartToy as BotIcon,
  ContentCopy as CopyIcon,
  Person as PersonIcon,
  School as SchoolIcon,
  Send as SendIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import {
  alpha,
  AppBar,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Fade,
  IconButton,
  LinearProgress,
  List,
  ListItem,
  Paper,
  Stack,
  TextField,
  Toolbar,
  Tooltip,
  Typography,
  useTheme,
  Zoom,
} from '@mui/material';
import axios from 'axios';
import React, { useEffect, useRef, useState } from 'react';
import { NotificationContext } from './NotificationProvider';
import TypingEffect from './TypingEffect';
import { useNavigate } from 'react-router-dom';
import NewOMULogo from '../pics/WhatsApp Görsel 2025-07-11 saat 09.43.41_ab073c19.jpg';

const API = process.env.REACT_APP_API_URL || '';

interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
  sources?: string[];
  isTyping?: boolean;
  type?: string;
  category?: string;
  confidence?: number;
  quality_level?: string;
}

interface ConversationEntry {
  user: string;
  assistant: string;
  timestamp: string;
}

interface DocumentData {
  filename: string;
  keyword: string;
  content: string;
}

const ChatBot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [currentRequestController, setCurrentRequestController] = useState<AbortController | null>(null);
  const [topQuestion, setTopQuestion] = useState<string>("");
  const [userId] = useState(() => `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [conversationHistory, setConversationHistory] = useState<ConversationEntry[]>([]);
  const [documentData, setDocumentData] = useState<DocumentData[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const theme = useTheme();
  const { showNotification } = React.useContext(NotificationContext);
  const navigate = useNavigate();

  // Topic bilgisini temizleyen helper fonksiyon
  const cleanTopicFromQuestion = (question: string): string => {
    // [topic] formatındaki metinleri kaldır
    return question.replace(/\[.*?\]/g, '').trim();
  };

  const scrollToInput = () => {
    inputRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  const focusInput = () => {
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    // Input alanına da scroll ve focus
    setTimeout(() => {
      scrollToInput();
      if (!isLoading) { // Sadece yükleme bittiyse focus et
        focusInput();
      }
    }, 300);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Sayfa yüklenir yüklenmez stil uygula - flash'ı tamamen engelle
  useEffect(() => {
    // Önce mevcut stilleri hemen uygula - OMU Teması
    document.body.style.setProperty('background', 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1e40af 100%)', 'important');
    document.documentElement.style.setProperty('background', 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1e40af 100%)', 'important');
    
    // Güçlü CSS stilleri ekle
    const style = document.createElement('style');
    style.id = 'chatbot-theme-fix';
    style.textContent = `
      /* Hızlı yüklenen temel stiller - OMU Teması */
      body, html, #root {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1e40af 100%) !important;
        background-attachment: fixed !important;
        transition: none !important;
        min-height: 100vh !important;
      }
      
      /* ChatBot container için sabit stil */
      .chatbot-container {
        background: transparent !important;
        min-height: 100vh !important;
        transform: translateZ(0) !important;
        backface-visibility: hidden !important;
        will-change: transform !important;
      }
      
      /* Anti-flash için hardware acceleration */
      * {
        -webkit-backface-visibility: hidden !important;
        backface-visibility: hidden !important;
        -webkit-transform: translate3d(0, 0, 0) !important;
        transform: translate3d(0, 0, 0) !important;
      }
      
      /* MUI stilleri için override - OMU Header */
      .chatbot-header .MuiAppBar-root,
      .MuiAppBar-root {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1e40af 100%) !important;
        backdrop-filter: blur(10px) !important;
        border-bottom: 1px solid rgba(59, 130, 246, 0.2) !important;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.15) !important;
      }
      
      /* OMU Card Styling */
      .chatbot-container .MuiCard-root,
      .MuiCard-root {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(59, 130, 246, 0.1) !important;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.15) !important;
        border-radius: 16px !important;
      }
      
      /* OMU Paper Styling */
      .chatbot-container .MuiPaper-root {
        background-color: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(59, 130, 246, 0.1) !important;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.15) !important;
      }
      
      /* OMU TextField Styling */
      .chatbot-container .MuiTextField-root {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 16px !important;
      }
      
      .chatbot-container .MuiTextField-root .MuiOutlinedInput-root {
        border-radius: 16px !important;
        border: 2px solid rgba(59, 130, 246, 0.2) !important;
      }
      
      .chatbot-container .MuiTextField-root .MuiOutlinedInput-root:hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
      }
      
      .chatbot-container .MuiTextField-root .MuiOutlinedInput-root.Mui-focused {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
      }
      
      /* OMU Button Styling */
      .chatbot-container .MuiButton-root {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        border-radius: 16px !important;
        text-transform: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(30, 58, 138, 0.3) !important;
        transition: all 0.3s ease !important;
      }
      
      .chatbot-container .MuiButton-root:hover {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(30, 58, 138, 0.4) !important;
      }
      
      .chatbot-container .MuiButton-root:disabled {
        background: linear-gradient(135deg, #94a3b8 0%, #cbd5e1 100%) !important;
        color: #64748b !important;
        transform: none !important;
        box-shadow: none !important;
      }
      
      /* Özel buton stilleri - En popüler soru (Mavi border) */
      .chatbot-container .popular-question-btn {
        background: transparent !important;
        border: 2px solid #1e3a8a !important;
        color: #1e3a8a !important;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.1) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
      }
      
      .chatbot-container .popular-question-btn:hover {
        background: rgba(30, 58, 138, 0.05) !important;
        border-color: #1e3a8a !important;
        color: #1e3a8a !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2) !important;
        transform: translateY(-1px) !important;
      }
      
      .chatbot-container .popular-question-btn:disabled {
        background: transparent !important;
        border: 2px solid #e2e8f0 !important;
        color: #94a3b8 !important;
        box-shadow: none !important;
        transform: none !important;
      }
      
      /* Chat temizle butonu (Kırmızı border) */
      .chatbot-container .clear-chat-btn {
        background: transparent !important;
        border: 2px solid #dc2626 !important;
        color: #dc2626 !important;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.1) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
      }
      
      .chatbot-container .clear-chat-btn:hover {
        background: rgba(239, 68, 68, 0.05) !important;
        border-color: #dc2626 !important;
        color: #dc2626 !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2) !important;
        transform: translateY(-1px) !important;
      }
      
      /* Admin Paneli butonu (Beyaz border - header'da) */
      .chatbot-container .admin-panel-btn {
        background: transparent !important;
        border: 2px solid rgba(255, 255, 255, 0.8) !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        text-transform: none !important;
      }
      
      .chatbot-container .admin-panel-btn:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: #ffffff !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-1px) !important;
      }
      
      /* OMU Typography */
      .chatbot-container .MuiTypography-h6 {
        color: white !important;
        font-weight: 700 !important;
      }
    `;
    
    // Style'ı head'in en başına ekle (öncelik için)
    const existingStyle = document.getElementById('chatbot-theme-fix');
    if (existingStyle) {
      document.head.removeChild(existingStyle);
    }
    document.head.insertBefore(style, document.head.firstChild);
    
    return () => {
      const styleToRemove = document.getElementById('chatbot-theme-fix');
      if (styleToRemove) {
        document.head.removeChild(styleToRemove);
      }
    };
  }, []);

  // Hoş geldin mesajı
  useEffect(() => {
    const welcomeMessage: Message = {
      id: '1',
      text: 'Merhaba! 👋 Ben Ondokuz Mayıs Üniversitesi bilgi asistanınızım. Üniversite yönetmelikleri, kuralları ve prosedürleri hakkında sorularınızı yanıtlamaya hazırım. Size nasıl yardımcı olabilirim?',
      isBot: true,
      timestamp: new Date(),
      type: 'greeting',
      quality_level: 'Otomatik Yanıt',
      confidence: 1.0
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    // En çok sorulan soruyu backend'den çek
    fetch("/api/admin/stats", { cache: "no-store" })
      .then((res) => res.json())
      .then((data) => {
        if (data.topQuestions && data.topQuestions.length > 0) {
          setTopQuestion(data.topQuestions[0].question);
        }
      });

    // Kullanıcı session'ını başlat
    axios.post('/api/user/session', { user_id: userId })
      .catch(error => console.log('Session başlatma hatası:', error));
  }, [userId]);

  // Fetch document data for filename mapping
  useEffect(() => {
    const fetchDocumentData = async () => {
      try {
        const response = await fetch('/enhanced_document_data.json');
        const data = await response.json();
        setDocumentData(data);
      } catch (error) {
        console.error('Error fetching document data:', error);
      }
    };

    fetchDocumentData();
  }, []);

  const clearChat = async () => {
    try {
      // Backend'de sohbet geçmişini temizle
      await axios.post('/api/conversation/clear', { user_id: userId });
      
      const welcomeMessage: Message = {
        id: Date.now().toString(),
        text: 'Chat geçmişi temizlendi. Yeni bir soru sorabilirsiniz! 🚀',
        isBot: true,
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
      setConversationHistory([]);
      showNotification('Chat geçmişi temizlendi', 'success');
    } catch (error) {
      showNotification('Chat geçmişi temizlenirken hata oluştu', 'error');
    }
  };

  const copyMessage = (text: string) => {
    navigator.clipboard.writeText(text);
    showNotification('Metin kopyalandı', 'success');
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Background'u korumak için ekstra önlem
    document.body.style.setProperty('background', 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 100%)', 'important');
    document.documentElement.style.setProperty('background', 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 100%)', 'important');

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      isBot: false,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    
    // Background'u koruyarak loading state'i değiştir
    document.body.style.setProperty('background', 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 100%)', 'important');
    setIsLoading(true);
    setIsTyping(true);

    // Yeni AbortController oluştur
    const controller = new AbortController();
    setCurrentRequestController(controller);

    try {
      const response = await axios.post('/api/chat', {
        message: currentInput,
        user_id: userId,
      }, {
        signal: controller.signal
      });
      
      // Hata kontrolü
      if (response.data.error) {
        throw new Error(response.data.error);
      }
      
      // Sohbet geçmişini güncelle
      if (response.data.conversation_history) {
        setConversationHistory(response.data.conversation_history);
      }
      
      // Typing efekti için kısa bekleme
      setTimeout(() => {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          isBot: true,
          timestamp: new Date(),
          sources: response.data.sources,
          isTyping: true,
          type: response.data.type,
          category: response.data.category,
          confidence: response.data.confidence,
          quality_level: response.data.quality_level,
        };

        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
        
        // Yanıt tamamlandıktan sonra input'a scroll ve focus
        setTimeout(() => {
          scrollToInput();
          focusInput();
        }, 2000); // Typing effect için ekstra bekle
      }, 800);
    } catch (error: any) {
      // İptal edilmişse sadece kullanıcıya bilgi ver, backend'e hiçbir şey gönderme
      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        const cancelMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: '⏹️ Yanıt üretimi durduruldu. Yeni bir soru sorabilirsiniz.',
          isBot: true,
          timestamp: new Date(),
          type: 'cancelled',
          quality_level: 'İptal Edildi'
        };
        setMessages(prev => [...prev, cancelMessage]);
        
        // İptal durumunda da input'a odaklan
        setTimeout(() => {
          scrollToInput();
          focusInput();
        }, 500);
      } else {
        setTimeout(() => {
          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: '⚠️ Üzgünüm, bir hata oluştu. ' + (error?.message || 'Lütfen tekrar deneyin veya sunucunun çalıştığından emin olun.'),
            isBot: true,
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMessage]);
          
          // Hata durumunda da input'a odaklan
          setTimeout(() => {
            scrollToInput();
            focusInput();
          }, 500);
        }, 1000);
      }
      setIsTyping(false);
    } finally {
      // Background'u koruyarak loading state'i kapat
      document.body.style.setProperty('background', 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 100%)', 'important');
      setIsLoading(false);
      setCurrentRequestController(null);
    }
  };

  const handleStop = () => {
    if (currentRequestController) {
      currentRequestController.abort();
      setCurrentRequestController(null);
      // Background'u koruyarak loading state'i kapat
      document.body.style.setProperty('background', 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 100%)', 'important');
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Function to get filename for a source keyword
  const getFilenameForSource = (source: string): string => {
    // Return the actual filename instead of mapped keywords
    return source;
  };

  // Link dönüştürme fonksiyonu
  const renderTextWithLinks = (text: string) => {
    // https ile başlayan linkleri bul ve tıklanabilir hale getir
    const linkRegex = /(https:\/\/[^\s]+)/g;
    const parts = text.split(linkRegex);
    
    return (
      <>
        {parts.map((part, index) => {
          if (part.match(linkRegex)) {
            return (
              <a 
                key={index}
                href={part}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: '#3b82f6',
                  textDecoration: 'none',
                  fontWeight: 600,
                  borderRadius: '4px',
                  padding: '2px 4px',
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.2)',
                  transition: 'all 0.2s ease',
                  display: 'inline-block',
                  margin: '0 2px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.2)';
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.boxShadow = '0 2px 4px rgba(59, 130, 246, 0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {part}
              </a>
            );
          }
          return part;
        })}
      </>
    );
  };

  return (
    <>
      {/* Sabit arka plan katmanı */}
      <Box
        sx={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 100%)',
          zIndex: -1000,
          pointerEvents: 'none',
        }}
      />
      
      <Box 
        className="chatbot-container"
        sx={{ 
          height: '100vh', 
          display: 'flex', 
          flexDirection: 'column',
          background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 100%) !important',
          minHeight: '100vh',
          overflow: 'auto',
          position: 'relative',
          zIndex: 1,
        }}
      >
      {/* Header */}
      <AppBar
        className="chatbot-header"
        position="static"
        elevation={0}
        sx={{
          background: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #1e40af 100%) !important',
          backdropFilter: 'blur(10px)',
          borderBottom: `1px solid rgba(59, 130, 246, 0.2)`,
          boxShadow: '0 4px 20px rgba(30, 58, 138, 0.15)',
        }}
      >
        <Toolbar sx={{ minHeight: '70px !important', px: 3 }}>
          <Avatar
            src={NewOMULogo}
            alt="OMÜ Logo"
            sx={{
              mr: 3,
              background: '#ffffff',
              color: '#1e3a8a',
              width: 50,
              height: 50,
              border: '3px solid rgba(255, 255, 255, 0.8)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            }}
          />
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h5" component="div" sx={{
              fontWeight: 700,
              color: '#ffffff',
              textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
            }}>
              OMÜ Yapay Zeka Asistan
            </Typography>
            
          </Box>
          {/* Admin Paneli Butonu */}
          <Button
            className="admin-panel-btn"
            color="inherit"
            variant="outlined"
            onClick={() => navigate('/admin')}
            sx={{ 
              ml: 2, 
              fontWeight: 600,
              borderRadius: 3,
              textTransform: 'none',
              fontSize: '0.9rem',
              borderColor: 'rgba(255, 255, 255, 0.8)',
              color: '#ffffff',
              border: '2px solid rgba(255, 255, 255, 0.8)',
              boxShadow: '0 2px 8px rgba(255, 255, 255, 0.1)',
              transition: 'all 0.2s ease',
              '&:hover': {
                borderColor: '#ffffff',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                boxShadow: '0 4px 12px rgba(255, 255, 255, 0.2)',
                transform: 'translateY(-1px)',
              }
            }}
          >
            Admin Paneli
          </Button>
        </Toolbar>
      </AppBar>

      {/* Chat Area */}
      <Container maxWidth="lg" sx={{ flex: 1, display: 'flex', flexDirection: 'column', py: 3 }}>
        <Card
          elevation={0}
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
            borderRadius: 4,
            border: `1px solid rgba(30, 58, 138, 0.1)`,
            boxShadow: '0 8px 32px rgba(30, 58, 138, 0.08)',
            overflow: 'hidden',
          }}
        >
          {/* Messages */}
          <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
            <List sx={{ p: 0 }}>
              {messages.map((message, index) => (
                <Zoom in={true} key={message.id} timeout={300 + index * 100}>
                  <ListItem
                    sx={{
                      display: 'flex',
                      flexDirection: message.isBot ? 'row' : 'row-reverse',
                      alignItems: 'flex-start',
                      gap: 2,
                      mb: 3,
                      px: 0,
                    }}
                  >
                    <Avatar
                      sx={{
                        background: message.isBot 
                          ? 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)' 
                          : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                        color: message.isBot ? '#ffffff' : '#1e3a8a',
                        width: 40,
                        height: 40,
                        border: message.isBot 
                          ? '2px solid rgba(59, 130, 246, 0.5)' 
                          : '2px solid rgba(30, 58, 138, 0.4)',
                        boxShadow: message.isBot 
                          ? '0 4px 12px rgba(30, 58, 138, 0.2)' 
                          : '0 4px 12px rgba(0, 0, 0, 0.1)',
                      }}
                    >
                      {message.isBot ? <BotIcon /> : <PersonIcon />}
                    </Avatar>

                    <Card
                      sx={{
                        maxWidth: { xs: '90%', sm: '75%' },
                        background: message.isBot
                          ? 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)'
                          : 'linear-gradient(135deg, rgba(30, 58, 138, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%)',
                        border: `2px solid ${message.isBot
                          ? 'rgba(30, 58, 138, 0.35)'
                          : 'rgba(30, 58, 138, 0.4)'}`,
                        borderRadius: 4,
                        position: 'relative',
                        boxShadow: message.isBot 
                          ? '0 8px 32px rgba(30, 58, 138, 0.12)' 
                          : '0 8px 32px rgba(30, 58, 138, 0.15)',
                        '&:hover .message-actions': {
                          opacity: 1,
                        },
                      }}
                    >
                      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
                        {message.isBot && message.isTyping ? (
                          <TypingEffect text={message.text} speed={8} />
                        ) : (                        <Typography
                          variant="body1"
                          sx={{
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.7,
                            fontSize: '0.95rem',
                            color: '#1e3a8a',
                            fontFamily: '"Segoe UI", Tahoma, Geneva, Verdana, sans-serif',
                            fontWeight: message.isBot ? 500 : 500,
                          }}
                        >
                            {renderTextWithLinks(message.text)}
                          </Typography>
                        )}

                        {/* Kalite ve kategori bilgileri (bot mesajları için) - GİZLENDİ */}
                        {/* {message.isBot && (message.type || message.category || message.confidence !== undefined) && (
                          <Box sx={{ mt: 2, mb: 1 }}>
                            <Stack direction="row" spacing={1} flexWrap="wrap">
                              {message.type && (
                                <Chip
                                  label={message.type === 'greeting' ? 'Selamlama' : 
                                        message.type === 'goodbye' ? 'Veda' :
                                        message.type === 'no_answer' ? 'Cevap Yok' : 
                                        message.type === 'knowledge_answer' ? 'Bilgi' : message.type}
                                  size="small"
                                  sx={{
                                    bgcolor: message.type === 'greeting' || message.type === 'goodbye' ? 
                                           'rgba(76, 175, 80, 0.2)' : 
                                           message.type === 'no_answer' ? 'rgba(244, 67, 54, 0.2)' :
                                           'rgba(33, 150, 243, 0.2)',
                                    color: 'white',
                                    fontSize: '0.7rem',
                                  }}
                                />
                              )}
                              {message.category && (
                                <Chip
                                  label={message.category}
                                  size="small"
                                  sx={{
                                    bgcolor: 'rgba(156, 39, 176, 0.2)',
                                    color: 'white',
                                    fontSize: '0.7rem',
                                  }}
                                />
                              )}
                              {message.confidence !== undefined && (
                                <Chip
                                  label={`Güven: ${(message.confidence * 100).toFixed(0)}%`}
                                  size="small"
                                  sx={{
                                    bgcolor: message.confidence >= 0.7 ? 'rgba(76, 175, 80, 0.2)' :
                                             message.confidence >= 0.4 ? 'rgba(255, 193, 7, 0.2)' :
                                             'rgba(244, 67, 54, 0.2)',
                                    color: 'white',
                                    fontSize: '0.7rem',
                                  }}
                                />
                              )}
                              {message.quality_level && (
                                <Chip
                                  label={message.quality_level}
                                  size="small"
                                  sx={{
                                    bgcolor: 'rgba(103, 58, 183, 0.2)',
                                    color: 'white',
                                    fontSize: '0.7rem',
                                  }}
                                />
                              )}
                            </Stack>
                          </Box>
                        )} */}

                        {/* Kaynaklar */}
                        {message.sources && message.sources.length > 0 && (
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="caption" sx={{ color: '#1e3a8a', fontWeight: 600 }}>
                              Kaynaklar:
                            </Typography>
                            <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 1 }}>
                              {message.sources.filter((source, idx, arr) => arr.indexOf(source) === idx).map((source, idx) => (
                                <Chip
                                  key={idx}
                                  label={getFilenameForSource(source)}
                                  size="small"
                                  sx={{
                                    bgcolor: '#1e3a8a',
                                    color: 'white',
                                    fontSize: '0.75rem',
                                    fontWeight: 500,
                                    '&:hover': {
                                      bgcolor: '#1e40af',
                                    }
                                  }}
                                />
                              ))}
                            </Stack>
                          </Box>
                        )}

                        <Box sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          mt: 2,
                        }}>
                          <Typography
                            variant="caption"
                            sx={{
                              opacity: 0.6,
                              fontSize: '0.75rem',
                              color: '#64748b',
                            }}
                          >
                            {message.timestamp.toLocaleTimeString('tr-TR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </Typography>

                          {/* Message Actions */}
                          <Stack
                            direction="row"
                            spacing={0.5}
                            className="message-actions"
                            sx={{
                              opacity: 0,
                              transition: 'opacity 0.2s ease',
                            }}
                          >
                            <Tooltip title="Kopyala">
                              <IconButton
                                size="small"
                                onClick={() => copyMessage(message.text)}
                                sx={{
                                  color: 'rgba(30, 58, 138, 0.5)',
                                  '&:hover': {
                                    color: '#1e3a8a',
                                    background: 'rgba(30, 58, 138, 0.08)',
                                  },
                                }}
                              >
                                <CopyIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>

                          </Stack>
                        </Box>
                      </CardContent>
                    </Card>
                  </ListItem>
                </Zoom>
              ))}

              {isTyping && (
                <Fade in={true} timeout={300}>
                  <ListItem sx={{ display: 'flex', gap: 2, mb: 3, px: 0 }}>
                    <Avatar sx={{
                      background: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
                      color: '#ffffff',
                      width: 40,
                      height: 40,
                      border: '2px solid rgba(59, 130, 246, 0.3)',
                      boxShadow: '0 4px 12px rgba(30, 58, 138, 0.15)',
                    }}>
                      <BotIcon />
                    </Avatar>
                    <Card sx={{
                      background: 'linear-gradient(135deg, rgba(248, 250, 252, 0.95) 0%, rgba(255, 255, 255, 0.95) 100%)',
                      border: `1px solid rgba(30, 58, 138, 0.1)`,
                      borderRadius: 3,
                      boxShadow: '0 4px 20px rgba(30, 58, 138, 0.08)',
                    }}>
                      <CardContent sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
                        <CircularProgress size={20} sx={{ color: '#1e3a8a' }} />
                        <Typography variant="body1" sx={{ opacity: 0.7, color: '#64748b' }}>
                          Düşünüyorum... 🤔
                        </Typography>
                      </CardContent>
                    </Card>
                  </ListItem>
                </Fade>
              )}
            </List>
            <div ref={messagesEndRef} />
          </Box>

          {/* Input Area */}
          <Box sx={{
            p: 3,
            background: 'linear-gradient(135deg, rgba(248, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.95) 100%)',
            backdropFilter: 'blur(15px)',
            borderTop: `1px solid rgba(30, 58, 138, 0.1)`,
            boxShadow: '0 -4px 20px rgba(30, 58, 138, 0.05)',
          }}>
            {/* Quick Actions */}
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={1}
              sx={{ mb: 2 }}
            >
              <Button
                className="popular-question-btn"
                size="small"
                variant="outlined"
                onClick={() => {
                  if (topQuestion) {
                    const cleanedQuestion = cleanTopicFromQuestion(topQuestion);
                    setInput(cleanedQuestion.charAt(0).toUpperCase() + cleanedQuestion.slice(1).replace(/\?*$/, '') + '?');
                  }
                }}
                sx={{
                  borderRadius: 3,
                  textTransform: 'none',
                  fontSize: '0.8rem',
                  borderColor: 'rgba(30, 58, 138, 0.25)',
                  color: '#1e3a8a',
                  fontWeight: 600,
                  boxShadow: '0 2px 8px rgba(30, 58, 138, 0.1)',
                  '&:hover': {
                    borderColor: '#1e3a8a',
                    background: 'rgba(30, 58, 138, 0.05)',
                    boxShadow: '0 4px 12px rgba(30, 58, 138, 0.2)',
                    transform: 'translateY(-1px)',
                  },
                  transition: 'all 0.2s ease',
                }}
                disabled={!topQuestion}
              >
                {topQuestion ? ` ${(() => {
                  const cleanedQuestion = cleanTopicFromQuestion(topQuestion);
                  return cleanedQuestion.charAt(0).toUpperCase() + cleanedQuestion.slice(1).replace(/\?*$/, '') + '?';
                })()}` : 'Yükleniyor...'}
              </Button>
              <Button
                className="clear-chat-btn"
                size="small"
                variant="outlined"
                onClick={clearChat}
                sx={{
                  borderRadius: 3,
                  textTransform: 'none',
                  fontSize: '0.8rem',
                  borderColor: 'rgba(239, 68, 68, 0.3)',
                  color: '#dc2626',
                  fontWeight: 600,
                  boxShadow: '0 2px 8px rgba(239, 68, 68, 0.1)',
                  '&:hover': {
                    borderColor: '#dc2626',
                    background: 'rgba(239, 68, 68, 0.05)',
                    boxShadow: '0 4px 12px rgba(239, 68, 68, 0.2)',
                    transform: 'translateY(-1px)',
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                🗑️ Chat'i Temizle
              </Button>
            </Stack>

            {/* Loading Progress */}
            {isLoading && (
              <LinearProgress
                sx={{
                  mb: 2,
                  borderRadius: 1,
                  backgroundColor: 'rgba(30, 58, 138, 0.08)',
                  background: 'transparent',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%)',
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'transparent',
                    zIndex: -1,
                  }
                }}
              />
            )}

            {/* Input Field */}
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
              <TextField
                fullWidth
                multiline
                maxRows={4}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Sorunuzu buraya yazın..."
                disabled={isLoading}
                variant="outlined"
                inputRef={inputRef}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%)',
                    borderRadius: 3,
                    fontSize: '1rem',
                    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif',
                    color: '#1e3a8a',
                    fontWeight: 500,
                    lineHeight: 1.6,
                    '& fieldset': {
                      borderColor: 'rgba(30, 58, 138, 0.2)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(30, 58, 138, 0.4)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1e3a8a',
                      borderWidth: 2,
                    },
                  },
                  '& .MuiOutlinedInput-input': {
                    color: '#1e3a8a',
                    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif',
                    fontWeight: 500,
                    fontSize: '1rem',
                    lineHeight: 1.6,
                    '&::placeholder': {
                      color: 'rgba(30, 58, 138, 0.5)',
                      fontWeight: 400,
                    },
                  },
                }}
              />
              <IconButton
                onClick={isLoading ? handleStop : handleSend}
                disabled={!isLoading && !input.trim()}
                sx={{
                  background: isLoading 
                    ? 'linear-gradient(135deg, #dc2626 0%, #ef4444 100%)' 
                    : 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
                  color: 'white',
                  width: 52,
                  height: 52,
                  borderRadius: 3,
                  boxShadow: '0 4px 12px rgba(30, 58, 138, 0.3)',
                  '&:hover': {
                    background: isLoading 
                      ? 'linear-gradient(135deg, #b91c1c 0%, #dc2626 100%)' 
                      : 'linear-gradient(135deg, #1e40af 0%, #2563eb 100%)',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 6px 16px rgba(30, 58, 138, 0.4)',
                  },
                  '&:disabled': {
                    background: 'rgba(148, 163, 184, 0.3)',
                    color: 'rgba(148, 163, 184, 0.6)',
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                {isLoading ? <StopIcon /> : <SendIcon />}
              </IconButton>
            </Box>

            {/* Status Info */}
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                textAlign: 'center',
                mt: 2,
                opacity: 0.6,
                fontSize: '0.75rem',
                color: '#64748b',
              }}
            >
              {/* Yanıt hazırlama mesajı kaldırıldı */}
            </Typography>
          </Box>
        </Card>
      </Container>
    </Box>
    </>
  );
};

export default ChatBot;
