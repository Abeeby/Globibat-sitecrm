import React, { createContext, useContext, useEffect, useRef } from 'react';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { useAuth } from './AuthContext';
import api from '../services/api';

const NotificationContext = createContext({});

// Configuration des notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export const NotificationProvider = ({ children }) => {
  const { user } = useAuth();
  const notificationListener = useRef();
  const responseListener = useRef();

  useEffect(() => {
    if (user) {
      registerForPushNotifications();
      setupNotificationListeners();
    }

    return () => {
      if (notificationListener.current) {
        Notifications.removeNotificationSubscription(notificationListener.current);
      }
      if (responseListener.current) {
        Notifications.removeNotificationSubscription(responseListener.current);
      }
    };
  }, [user]);

  const registerForPushNotifications = async () => {
    if (!Device.isDevice) {
      console.log('Les notifications ne fonctionnent que sur un appareil physique');
      return;
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.log('Permission pour les notifications refusée');
      return;
    }

    try {
      const token = await Notifications.getExpoPushTokenAsync();
      console.log('Push token:', token.data);
      
      // Envoyer le token au serveur
      await api.post('/api/notifications/register', {
        token: token.data,
        userId: user?.id,
        platform: Platform.OS
      });
    } catch (error) {
      console.error('Erreur obtention token push:', error);
    }

    if (Platform.OS === 'android') {
      Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }
  };

  const setupNotificationListeners = () => {
    // Listener pour les notifications reçues quand l'app est ouverte
    notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
      console.log('Notification reçue:', notification);
    });

    // Listener pour les interactions avec les notifications
    responseListener.current = Notifications.addNotificationResponseReceivedListener(response => {
      const data = response.notification.request.content.data;
      handleNotificationResponse(data);
    });
  };

  const handleNotificationResponse = (data) => {
    // Gérer la navigation selon le type de notification
    if (data.type === 'badge') {
      // Navigation vers l'écran des badges
    } else if (data.type === 'message') {
      // Navigation vers le chat
    } else if (data.type === 'alert') {
      // Afficher l'alerte
    }
  };

  const sendLocalNotification = async (title, body, data = {}) => {
    await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body,
        data,
        sound: true,
      },
      trigger: null, // Immédiat
    });
  };

  const clearAllNotifications = async () => {
    await Notifications.dismissAllNotificationsAsync();
  };

  const setBadgeCount = async (count) => {
    if (Platform.OS === 'ios') {
      await Notifications.setBadgeCountAsync(count);
    }
  };

  return (
    <NotificationContext.Provider value={{
      sendLocalNotification,
      clearAllNotifications,
      setBadgeCount,
    }}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};