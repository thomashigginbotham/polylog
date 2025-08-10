import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';

interface Message {
  id: string;
  userId: string | null;
  userName: string;
  content: string;
  isAiMessage: boolean;
  timestamp: string;
}

interface WebSocketContextType {
  messages: Message[];
  sendMessage: (message: string) => void;
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  isConnected: boolean;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  
  // Use refs to prevent duplicate connections
  const isConnecting = useRef(false);
  const connectionId = useRef<string | null>(null);

  const connectWebSocket = useCallback(() => {
    // Prevent multiple simultaneous connections
    if (socket?.readyState === WebSocket.OPEN || isConnecting.current) {
      console.log('🔒 WebSocket connection prevented: already connected or connecting');
      return;
    }

    // Generate unique connection ID
    const newConnectionId = Date.now().toString();
    connectionId.current = newConnectionId;
    isConnecting.current = true;

    console.log('🔌 Attempting WebSocket connection with ID:', newConnectionId);
    setConnectionStatus('connecting');

    // Switch back to full WebSocket endpoint with AI responses
    const ws = new WebSocket('ws://localhost:8000/ws/test');

    ws.onopen = (event) => {
      // Check if this is still the active connection attempt
      if (connectionId.current !== newConnectionId) {
        console.log('🚫 Ignoring connection from outdated attempt:', newConnectionId);
        ws.close();
        return;
      }

      console.log('✅ WebSocket connected successfully with ID:', newConnectionId);
      setConnectionStatus('connected');
      setSocket(ws);
      isConnecting.current = false;
    };

    ws.onmessage = (event) => {
      // Check if this is still the active connection
      if (connectionId.current !== newConnectionId) {
        console.log('🚫 Ignoring message from outdated connection:', newConnectionId);
        return;
      }

      try {
        console.log('📨 WebSocket message received:', event.data);
        const message = JSON.parse(event.data);
        
        // Message already in correct format from full endpoint
        // Prevent duplicate welcome messages by checking content and recent timestamp
        setMessages((prevMessages) => {
          const now = Date.now();
          const recentWelcome = prevMessages.find(msg => 
            msg.userName === 'System' && 
            msg.content.includes('Connected to conversation') &&
            (now - new Date(msg.timestamp).getTime()) < 2000 // Within 2 seconds
          );
          
          if (message.userName === 'System' && 
              message.content.includes('Connected to conversation') && 
              recentWelcome) {
            console.log('🚫 Preventing duplicate welcome message');
            return prevMessages;
          }
          
          return [...prevMessages, message];
        });
      } catch (error) {
        console.error('❌ Failed to parse WebSocket message:', error, event.data);
      }
    };

    ws.onclose = (event) => {
      console.log('🔌 WebSocket disconnected with ID:', newConnectionId, { code: event.code, reason: event.reason });
      
      // Only update state if this is the active connection
      if (connectionId.current === newConnectionId) {
        setConnectionStatus('disconnected');
        setSocket(null);
        isConnecting.current = false;
        
        // Auto-reconnect after 3 seconds if not intentionally closed
        if (event.code !== 1000) {
          setTimeout(() => {
            console.log('🔄 Attempting to reconnect WebSocket...');
            connectWebSocket();
          }, 3000);
        }
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error with ID:', newConnectionId, error);
      if (connectionId.current === newConnectionId) {
        setConnectionStatus('error');
        isConnecting.current = false;
      }
    };

    // Store reference for cleanup
    setSocket(ws);
  }, []); // Empty dependency array to prevent recreations

  useEffect(() => {
    // Debounce connection attempt to prevent React Strict Mode duplicates
    const timer = setTimeout(() => {
      connectWebSocket();
    }, 100);

    // Cleanup on component unmount
    return () => {
      clearTimeout(timer);
      if (socket) {
        console.log('🧹 Cleaning up WebSocket connection');
        socket.close(1000, 'Component unmounting');
      }
      isConnecting.current = false;
      connectionId.current = null;
    };
  }, []); // Empty dependency array - only run once

  const sendMessage = useCallback((message: string) => {
    if (!socket) {
      console.warn('⚠️ Cannot send message: WebSocket not initialized');
      return;
    }

    if (socket.readyState === WebSocket.CONNECTING) {
      console.warn('⚠️ Cannot send message: WebSocket still connecting');
      return;
    }

    if (socket.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ Cannot send message: WebSocket not connected', {
        readyState: socket.readyState,
        status: connectionStatus
      });
      return;
    }

    try {
      console.log('📤 Sending message:', message);
      socket.send(message);
    } catch (error) {
      console.error('❌ Failed to send message:', error);
    }
  }, [socket, connectionStatus]);

  const isConnected = connectionStatus === 'connected' && socket?.readyState === WebSocket.OPEN;

  const contextValue = {
    messages,
    sendMessage,
    connectionStatus,
    isConnected
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocket() {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}