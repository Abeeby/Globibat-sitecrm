import React, { createContext, useContext, useEffect, useState } from 'react';
import io from 'socket.io-client';
import { useAuth } from './AuthContext';
import config from '../config';

const SocketContext = createContext({});

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [badgeUpdates, setBadgeUpdates] = useState([]);
  const [typingUsers, setTypingUsers] = useState({});
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      connectSocket();
    }
    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [user]);

  const connectSocket = () => {
    const newSocket = io(config.SOCKET_URL, {
      transports: ['websocket', 'polling'],
      query: {
        userId: user?.id,
        username: user?.name
      }
    });

    newSocket.on('connect', () => {
      console.log('✅ WebSocket connecté');
      setConnected(true);
      
      // S'enregistrer
      newSocket.emit('register_user', {
        username: user?.name,
        user_id: user?.id
      });

      // S'abonner aux notifications
      newSocket.emit('subscribe_notifications', {
        user_id: user?.id
      });

      // S'abonner aux badges
      newSocket.emit('subscribe_badges', {});
    });

    newSocket.on('disconnect', () => {
      console.log('❌ WebSocket déconnecté');
      setConnected(false);
    });

    // Événements de chat
    newSocket.on('new_message', (message) => {
      setMessages(prev => ({
        ...prev,
        [message.room]: [...(prev[message.room] || []), message]
      }));
    });

    newSocket.on('chat_history', (history) => {
      const room = history[0]?.room || 'general';
      setMessages(prev => ({
        ...prev,
        [room]: history
      }));
    });

    newSocket.on('user_typing', (data) => {
      setTypingUsers(prev => ({
        ...prev,
        [data.room]: data.typing ? data.user : null
      }));
    });

    // Événements de notifications
    newSocket.on('notification', (notification) => {
      setNotifications(prev => [notification, ...prev]);
    });

    newSocket.on('pending_notifications', (notifications) => {
      setNotifications(prev => [...notifications, ...prev]);
    });

    // Événements de badges
    newSocket.on('badge_update', (badge) => {
      setBadgeUpdates(prev => [badge, ...prev].slice(0, 50));
    });

    // Événements d'alertes
    newSocket.on('alert_broadcast', (alert) => {
      setNotifications(prev => [{
        id: `alert_${Date.now()}`,
        title: alert.title,
        message: alert.message,
        type: alert.type,
        time: alert.time
      }, ...prev]);
    });

    setSocket(newSocket);
  };

  const joinChat = (roomId) => {
    if (socket && connected) {
      socket.emit('join_chat', {
        chantier_id: roomId,
        username: user?.name
      });
    }
  };

  const leaveChat = (roomId) => {
    if (socket && connected) {
      socket.emit('leave_chat', {
        chantier_id: roomId,
        username: user?.name
      });
    }
  };

  const sendMessage = (roomId, message) => {
    if (socket && connected) {
      socket.emit('send_message', {
        chantier_id: roomId,
        message,
        username: user?.name,
        user_id: user?.id
      });
    }
  };

  const sendTyping = (roomId, typing) => {
    if (socket && connected) {
      socket.emit('typing', {
        chantier_id: roomId,
        username: user?.name,
        typing
      });
    }
  };

  const sendBadge = (badgeData) => {
    if (socket && connected) {
      socket.emit('new_badge', {
        ...badgeData,
        employe: user?.name,
        time: new Date().toISOString()
      });
    }
  };

  const updatePresence = (status, location = null) => {
    if (socket && connected) {
      socket.emit('update_presence', {
        employe_id: user?.id,
        employe_name: user?.name,
        status,
        location
      });
    }
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  return (
    <SocketContext.Provider value={{
      socket,
      connected,
      messages,
      notifications,
      badgeUpdates,
      typingUsers,
      joinChat,
      leaveChat,
      sendMessage,
      sendTyping,
      sendBadge,
      updatePresence,
      clearNotifications,
      removeNotification
    }}>
      {children}
    </SocketContext.Provider>
  );
};

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within SocketProvider');
  }
  return context;
};