import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from './AuthContext';
import toast from 'react-hot-toast';

interface SocketContextType {
  socket: Socket | null;
  connected: boolean;
  lastCommand: any | null;
  securityAlerts: any[];
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

interface SocketProviderProps {
  children: ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastCommand, setLastCommand] = useState<any>(null);
  const [securityAlerts, setSecurityAlerts] = useState<any[]>([]);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      const token = localStorage.getItem('access_token');
      const newSocket = io(process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000', {
        auth: {
          token,
        },
        transports: ['websocket', 'polling'],
      });

      newSocket.on('connect', () => {
        console.log('Connected to WebSocket');
        setConnected(true);
      });

      newSocket.on('disconnect', () => {
        console.log('Disconnected from WebSocket');
        setConnected(false);
      });

      newSocket.on('command_processed', (data) => {
        setLastCommand(data);
        console.log('Command processed:', data);
      });

      newSocket.on('security_alert', (data) => {
        setSecurityAlerts(prev => [data, ...prev.slice(0, 9)]); // Keep last 10 alerts
        toast.error(`Security Alert: ${data.type}`, {
          duration: 6000,
        });
        console.log('Security alert:', data);
      });

      newSocket.on('connect_error', (error) => {
        console.error('Socket connection error:', error);
        toast.error('Connection error. Some features may not work properly.');
      });

      setSocket(newSocket);

      return () => {
        newSocket.close();
      };
    }
  }, [user]);

  const value: SocketContextType = {
    socket,
    connected,
    lastCommand,
    securityAlerts,
  };

  return <SocketContext.Provider value={value}>{children}</SocketContext.Provider>;
};

export const useSocket = (): SocketContextType => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};