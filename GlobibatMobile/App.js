import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StatusBar } from 'expo-status-bar';
import { View, ActivityIndicator } from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Import des écrans
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import EmployeesScreen from './src/screens/EmployeesScreen';
import ClientsScreen from './src/screens/ClientsScreen';
import BadgesScreen from './src/screens/BadgesScreen';
import ChatsScreen from './src/screens/ChatsScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';

// Import des contextes et services
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { SocketProvider } from './src/contexts/SocketContext';
import { NotificationProvider } from './src/contexts/NotificationContext';

// Configuration du thème
const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#005BBB',
    accent: '#FF7A00',
    background: '#F4F6F8',
    surface: '#FFFFFF',
    text: '#2C3E50',
    success: '#27AE60',
    warning: '#FF7A00',
    error: '#DC3545',
  },
  roundness: 8,
};

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Navigation principale avec tabs
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Dashboard') {
            iconName = 'view-dashboard';
          } else if (route.name === 'Employés') {
            iconName = 'account-group';
          } else if (route.name === 'Clients') {
            iconName = 'domain';
          } else if (route.name === 'Badges') {
            iconName = 'badge-account';
          } else if (route.name === 'Chat') {
            iconName = 'message-text';
          } else if (route.name === 'Profil') {
            iconName = 'account';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: '#95A5A6',
        tabBarStyle: {
          height: 60,
          paddingBottom: 5,
          paddingTop: 5,
        },
        headerStyle: {
          backgroundColor: theme.colors.primary,
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: 'Tableau de bord' }}
      />
      <Tab.Screen 
        name="Employés" 
        component={EmployeesScreen}
        options={{ title: 'Employés' }}
      />
      <Tab.Screen 
        name="Clients" 
        component={ClientsScreen}
        options={{ title: 'Clients' }}
      />
      <Tab.Screen 
        name="Badges" 
        component={BadgesScreen}
        options={{ title: 'Badges' }}
      />
      <Tab.Screen 
        name="Chat" 
        component={ChatsScreen}
        options={{ title: 'Messages' }}
      />
      <Tab.Screen 
        name="Profil" 
        component={ProfileScreen}
        options={{ title: 'Profil' }}
      />
    </Tab.Navigator>
  );
}

// Navigation racine avec authentification
function RootNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {user ? (
        <>
          <Stack.Screen name="Main" component={MainTabs} />
          <Stack.Screen 
            name="Notifications" 
            component={NotificationsScreen}
            options={{
              headerShown: true,
              headerTitle: 'Notifications',
              headerStyle: {
                backgroundColor: theme.colors.primary,
              },
              headerTintColor: '#fff',
            }}
          />
        </>
      ) : (
        <Stack.Screen name="Login" component={LoginScreen} />
      )}
    </Stack.Navigator>
  );
}

// Application principale
export default function App() {
  return (
    <PaperProvider theme={theme}>
      <AuthProvider>
        <SocketProvider>
          <NotificationProvider>
            <NavigationContainer>
              <StatusBar style="light" backgroundColor={theme.colors.primary} />
              <RootNavigator />
            </NavigationContainer>
          </NotificationProvider>
        </SocketProvider>
      </AuthProvider>
    </PaperProvider>
  );
}
