import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import {
  Avatar,
  Card,
  List,
  Button,
  Divider,
  Switch,
  Surface,
} from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';

export default function ProfileScreen() {
  const { user, signOut } = useAuth();
  const [notifications, setNotifications] = React.useState(true);
  const [darkMode, setDarkMode] = React.useState(false);

  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        { 
          text: 'Déconnexion', 
          onPress: signOut,
          style: 'destructive'
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* Profil Header */}
      <Surface style={styles.header}>
        <Avatar.Text
          size={80}
          label={user?.name?.substring(0, 2).toUpperCase() || 'U'}
          style={styles.avatar}
        />
        <Text style={styles.name}>{user?.name || 'Utilisateur'}</Text>
        <Text style={styles.email}>{user?.email || 'email@example.com'}</Text>
        <Text style={styles.role}>{user?.role || 'Employé'}</Text>
      </Surface>

      {/* Informations */}
      <Card style={styles.card}>
        <Card.Title title="Informations" />
        <Card.Content>
          <List.Item
            title="Matricule"
            description={user?.matricule || 'EMP001'}
            left={(props) => <List.Icon {...props} icon="badge-account" />}
          />
          <Divider />
          <List.Item
            title="Département"
            description={user?.department || 'Construction'}
            left={(props) => <List.Icon {...props} icon="domain" />}
          />
          <Divider />
          <List.Item
            title="Téléphone"
            description={user?.phone || '+41 79 123 45 67'}
            left={(props) => <List.Icon {...props} icon="phone" />}
          />
        </Card.Content>
      </Card>

      {/* Paramètres */}
      <Card style={styles.card}>
        <Card.Title title="Paramètres" />
        <Card.Content>
          <List.Item
            title="Notifications"
            description="Recevoir les notifications push"
            left={(props) => <List.Icon {...props} icon="bell" />}
            right={() => (
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                color={config.colors.primary}
              />
            )}
          />
          <Divider />
          <List.Item
            title="Mode sombre"
            description="Activer le thème sombre"
            left={(props) => <List.Icon {...props} icon="theme-light-dark" />}
            right={() => (
              <Switch
                value={darkMode}
                onValueChange={setDarkMode}
                color={config.colors.primary}
              />
            )}
          />
        </Card.Content>
      </Card>

      {/* Actions */}
      <Card style={styles.card}>
        <Card.Title title="Actions" />
        <Card.Content>
          <List.Item
            title="Modifier le profil"
            left={(props) => <List.Icon {...props} icon="account-edit" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => Alert.alert('Info', 'Modifier le profil')}
          />
          <Divider />
          <List.Item
            title="Changer le mot de passe"
            left={(props) => <List.Icon {...props} icon="lock-reset" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => Alert.alert('Info', 'Changer le mot de passe')}
          />
          <Divider />
          <List.Item
            title="Aide et support"
            left={(props) => <List.Icon {...props} icon="help-circle" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => Alert.alert('Support', 'support@globibat.ch')}
          />
        </Card.Content>
      </Card>

      {/* Bouton déconnexion */}
      <Button
        mode="contained"
        onPress={handleLogout}
        style={styles.logoutButton}
        buttonColor={config.colors.danger}
        icon="logout"
      >
        Déconnexion
      </Button>

      {/* Version */}
      <Text style={styles.version}>
        Version 1.0.0 - © 2025 Globibat SA
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: config.colors.light,
  },
  header: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: 'white',
    elevation: 2,
    marginBottom: 16,
  },
  avatar: {
    backgroundColor: config.colors.primary,
    marginBottom: 12,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: config.colors.dark,
    marginBottom: 4,
  },
  email: {
    fontSize: 14,
    color: config.colors.dark,
    opacity: 0.7,
    marginBottom: 4,
  },
  role: {
    fontSize: 12,
    color: config.colors.primary,
    fontWeight: '500',
  },
  card: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
  },
  logoutButton: {
    margin: 16,
    marginTop: 8,
  },
  version: {
    textAlign: 'center',
    fontSize: 12,
    color: config.colors.dark,
    opacity: 0.5,
    marginBottom: 24,
  },
});