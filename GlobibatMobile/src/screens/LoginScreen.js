import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import {
  TextInput,
  Button,
  ActivityIndicator,
  Surface,
  Title,
  Paragraph,
} from 'react-native-paper';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { signIn } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    setLoading(true);
    const result = await signIn(email, password);
    setLoading(false);

    if (!result.success) {
      Alert.alert('Erreur de connexion', result.error);
    }
  };

  // Pour les tests, connexion rapide
  const quickLogin = () => {
    setEmail('admin@globibat.ch');
    setPassword('admin123');
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContainer}
        keyboardShouldPersistTaps="handled"
      >
        <Surface style={styles.surface}>
          <View style={styles.logoContainer}>
            <View style={styles.logo}>
              <Text style={styles.logoText}>G</Text>
            </View>
            <Title style={styles.title}>{config.APP_NAME}</Title>
            <Paragraph style={styles.subtitle}>
              Connectez-vous pour accéder à votre espace
            </Paragraph>
          </View>

          <View style={styles.form}>
            <TextInput
              label="Email"
              value={email}
              onChangeText={setEmail}
              mode="outlined"
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              left={<TextInput.Icon icon="email" />}
              style={styles.input}
              disabled={loading}
            />

            <TextInput
              label="Mot de passe"
              value={password}
              onChangeText={setPassword}
              mode="outlined"
              secureTextEntry={!showPassword}
              left={<TextInput.Icon icon="lock" />}
              right={
                <TextInput.Icon
                  icon={showPassword ? 'eye-off' : 'eye'}
                  onPress={() => setShowPassword(!showPassword)}
                />
              }
              style={styles.input}
              disabled={loading}
              onSubmitEditing={handleLogin}
            />

            <Button
              mode="contained"
              onPress={handleLogin}
              loading={loading}
              disabled={loading}
              style={styles.button}
              contentStyle={styles.buttonContent}
            >
              {loading ? 'Connexion...' : 'Se connecter'}
            </Button>

            {__DEV__ && (
              <Button
                mode="text"
                onPress={quickLogin}
                style={styles.devButton}
              >
                Connexion rapide (Dev)
              </Button>
            )}
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>
              © 2025 {config.COMPANY_NAME}
            </Text>
            <Text style={styles.version}>Version 1.0.0</Text>
          </View>
        </Surface>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: config.colors.light,
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  surface: {
    padding: 30,
    borderRadius: 12,
    elevation: 4,
    backgroundColor: 'white',
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: config.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  logoText: {
    color: 'white',
    fontSize: 36,
    fontWeight: 'bold',
  },
  title: {
    fontSize: 24,
    color: config.colors.primary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: config.colors.dark,
    opacity: 0.7,
    textAlign: 'center',
  },
  form: {
    marginBottom: 30,
  },
  input: {
    marginBottom: 16,
  },
  button: {
    marginTop: 8,
    borderRadius: 8,
  },
  buttonContent: {
    paddingVertical: 8,
  },
  devButton: {
    marginTop: 10,
  },
  footer: {
    alignItems: 'center',
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: config.colors.light,
  },
  footerText: {
    fontSize: 12,
    color: config.colors.dark,
    opacity: 0.6,
  },
  version: {
    fontSize: 10,
    color: config.colors.dark,
    opacity: 0.4,
    marginTop: 4,
  },
});