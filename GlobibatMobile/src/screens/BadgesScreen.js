import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  RefreshControl,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  Card,
  Button,
  TextInput,
  List,
  Divider,
  Chip,
  FAB,
  Surface,
  ActivityIndicator,
  SegmentedButtons,
  IconButton,
  Badge,
} from 'react-native-paper';
import * as Location from 'expo-location';
import { useSocket } from '../contexts/SocketContext';
import { apiService } from '../services/api';
import config from '../config';
import moment from 'moment';
import 'moment/locale/fr';

moment.locale('fr');

export default function BadgesScreen() {
  const [matricule, setMatricule] = useState('');
  const [badgeType, setBadgeType] = useState('ENTREE');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [todayBadges, setTodayBadges] = useState([]);
  const [location, setLocation] = useState(null);
  const [employeeInfo, setEmployeeInfo] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  
  const { connected, badgeUpdates, sendBadge } = useSocket();

  useEffect(() => {
    loadTodayBadges();
    requestLocationPermission();
    loadAnomalies();
  }, []);

  useEffect(() => {
    // Ajouter les nouveaux badges depuis WebSocket
    if (badgeUpdates.length > 0) {
      const latestBadge = badgeUpdates[0];
      setTodayBadges(prev => [latestBadge, ...prev]);
    }
  }, [badgeUpdates]);

  const requestLocationPermission = async () => {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        const currentLocation = await Location.getCurrentPositionAsync({});
        setLocation({
          latitude: currentLocation.coords.latitude,
          longitude: currentLocation.coords.longitude,
        });
      }
    } catch (error) {
      console.log('Erreur localisation:', error);
    }
  };

  const loadTodayBadges = async () => {
    try {
      const response = await apiService.badges.getToday();
      setTodayBadges(response.data);
    } catch (error) {
      console.error('Erreur chargement badges:', error);
    }
  };

  const loadAnomalies = async () => {
    try {
      const response = await apiService.badges.getAnomalies();
      setAnomalies(response.data);
    } catch (error) {
      console.error('Erreur chargement anomalies:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await Promise.all([
      loadTodayBadges(),
      loadAnomalies(),
      requestLocationPermission(),
    ]);
    setRefreshing(false);
  };

  const validateMatricule = async () => {
    if (!matricule) {
      Alert.alert('Erreur', 'Veuillez saisir un matricule');
      return;
    }

    setLoading(true);
    try {
      // Vérifier que le matricule existe
      const response = await apiService.employees.getByMatricule(matricule);
      setEmployeeInfo(response.data);
      return true;
    } catch (error) {
      Alert.alert('Erreur', 'Matricule invalide ou employé non trouvé');
      setEmployeeInfo(null);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const submitBadge = async () => {
    // Valider le matricule d'abord
    const isValid = await validateMatricule();
    if (!isValid) return;

    setLoading(true);
    try {
      // Envoyer le badge
      const response = await apiService.badges.submitBadge(
        matricule,
        config.BADGE_TYPES[badgeType],
        location
      );

      // Envoyer via WebSocket pour temps réel
      if (connected) {
        sendBadge({
          matricule,
          employe: employeeInfo?.nom_complet || matricule,
          type: config.BADGE_TYPES[badgeType],
          chantier_name: 'Bureau', // À adapter selon le contexte
          location,
        });
      }

      // Succès
      Alert.alert(
        'Badge enregistré',
        `${config.BADGE_TYPES[badgeType]} enregistrée pour ${employeeInfo?.nom_complet || matricule}`,
        [
          {
            text: 'OK',
            onPress: () => {
              // Réinitialiser
              setMatricule('');
              setEmployeeInfo(null);
              loadTodayBadges();
            },
          },
        ]
      );
    } catch (error) {
      Alert.alert('Erreur', 'Impossible d\'enregistrer le badge');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (dateString) => {
    return moment(dateString).format('HH:mm');
  };

  const formatDuration = (start, end) => {
    if (!end) return 'En cours...';
    const duration = moment.duration(moment(end).diff(moment(start)));
    return `${Math.floor(duration.asHours())}h${duration.minutes()}m`;
  };

  const getBadgeColor = (type) => {
    switch (type) {
      case 'Entrée':
        return config.colors.success;
      case 'Sortie':
        return config.colors.danger;
      case 'Pause':
        return config.colors.warning;
      case 'Reprise':
        return config.colors.info;
      default:
        return config.colors.dark;
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        keyboardShouldPersistTaps="handled"
      >
        {/* Carte de saisie du matricule */}
        <Card style={styles.badgeCard}>
          <Card.Title
            title="Badgeage par Matricule"
            subtitle={connected ? 'Connecté' : 'Hors ligne'}
            left={(props) => (
              <View>
                <IconButton {...props} icon="badge-account" />
                {connected && (
                  <Badge style={styles.connectedBadge} size={10} />
                )}
              </View>
            )}
          />
          <Card.Content>
            <TextInput
              label="Matricule employé"
              value={matricule}
              onChangeText={setMatricule}
              mode="outlined"
              keyboardType="default"
              autoCapitalize="characters"
              placeholder="Ex: EMP001"
              left={<TextInput.Icon icon="card-account-details" />}
              style={styles.matriculeInput}
              disabled={loading}
            />

            {employeeInfo && (
              <Surface style={styles.employeeInfo}>
                <Text style={styles.employeeName}>
                  {employeeInfo.nom_complet}
                </Text>
                <Text style={styles.employeeDetails}>
                  {employeeInfo.poste} - {employeeInfo.departement}
                </Text>
              </Surface>
            )}

            <Text style={styles.label}>Type de badge</Text>
            <SegmentedButtons
              value={badgeType}
              onValueChange={setBadgeType}
              buttons={[
                {
                  value: 'ENTREE',
                  label: 'Entrée',
                  icon: 'login',
                },
                {
                  value: 'SORTIE',
                  label: 'Sortie',
                  icon: 'logout',
                },
                {
                  value: 'PAUSE',
                  label: 'Pause',
                  icon: 'pause',
                },
                {
                  value: 'REPRISE',
                  label: 'Reprise',
                  icon: 'play',
                },
              ]}
              style={styles.segmentedButtons}
            />

            {location && (
              <Chip icon="map-marker" style={styles.locationChip}>
                Position GPS capturée
              </Chip>
            )}
          </Card.Content>
          <Card.Actions>
            <Button
              mode="contained"
              onPress={submitBadge}
              loading={loading}
              disabled={loading || !matricule}
              icon="check-circle"
              style={styles.submitButton}
            >
              Valider le badge
            </Button>
          </Card.Actions>
        </Card>

        {/* Anomalies */}
        {anomalies.length > 0 && (
          <Card style={styles.anomaliesCard}>
            <Card.Title
              title="Anomalies détectées"
              subtitle={`${anomalies.length} anomalie(s)`}
              left={(props) => <IconButton {...props} icon="alert" color={config.colors.danger} />}
            />
            <Card.Content>
              {anomalies.slice(0, 3).map((anomalie, index) => (
                <View key={index} style={styles.anomalieItem}>
                  <Text style={styles.anomalieText}>
                    {anomalie.employe} - {anomalie.description}
                  </Text>
                </View>
              ))}
            </Card.Content>
          </Card>
        )}

        {/* Badges du jour */}
        <Card style={styles.todayCard}>
          <Card.Title
            title="Badges d'aujourd'hui"
            subtitle={`${todayBadges.length} badge(s)`}
            left={(props) => <IconButton {...props} icon="clock-outline" />}
          />
          <Card.Content>
            {todayBadges.length === 0 ? (
              <Text style={styles.emptyText}>Aucun badge aujourd'hui</Text>
            ) : (
              <List.Section>
                {todayBadges.map((badge, index) => (
                  <View key={badge.id || index}>
                    <List.Item
                      title={badge.employe}
                      description={`${badge.type} - ${badge.chantier || 'Bureau'}`}
                      left={(props) => (
                        <View style={[styles.badgeIcon, { backgroundColor: getBadgeColor(badge.type) }]}>
                          <Text style={styles.badgeIconText}>
                            {badge.type?.charAt(0).toUpperCase()}
                          </Text>
                        </View>
                      )}
                      right={(props) => (
                        <Text style={styles.timeText}>
                          {formatTime(badge.time)}
                        </Text>
                      )}
                    />
                    {index < todayBadges.length - 1 && <Divider />}
                  </View>
                ))}
              </List.Section>
            )}
          </Card.Content>
        </Card>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: config.colors.light,
  },
  badgeCard: {
    margin: 16,
    elevation: 2,
  },
  matriculeInput: {
    marginBottom: 16,
    fontSize: 18,
  },
  employeeInfo: {
    padding: 12,
    marginBottom: 16,
    borderRadius: 8,
    backgroundColor: config.colors.light,
  },
  employeeName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: config.colors.dark,
  },
  employeeDetails: {
    fontSize: 14,
    color: config.colors.dark,
    opacity: 0.7,
    marginTop: 4,
  },
  label: {
    fontSize: 14,
    color: config.colors.dark,
    marginBottom: 8,
    fontWeight: '500',
  },
  segmentedButtons: {
    marginBottom: 16,
  },
  locationChip: {
    alignSelf: 'flex-start',
    marginBottom: 8,
  },
  submitButton: {
    flex: 1,
  },
  anomaliesCard: {
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
    borderLeftWidth: 4,
    borderLeftColor: config.colors.danger,
  },
  anomalieItem: {
    paddingVertical: 8,
  },
  anomalieText: {
    fontSize: 14,
    color: config.colors.danger,
  },
  todayCard: {
    margin: 16,
    elevation: 2,
  },
  emptyText: {
    textAlign: 'center',
    color: config.colors.dark,
    opacity: 0.5,
    paddingVertical: 20,
  },
  badgeIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeIconText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 18,
  },
  timeText: {
    fontSize: 14,
    color: config.colors.dark,
    opacity: 0.7,
  },
  connectedBadge: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: config.colors.success,
  },
});