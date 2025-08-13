import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
} from 'react-native';
import {
  Card,
  List,
  Searchbar,
  FAB,
  Chip,
  Avatar,
  Divider,
  ActivityIndicator,
} from 'react-native-paper';
import { apiService } from '../services/api';
import config from '../config';

export default function ClientsScreen() {
  const [clients, setClients] = useState([]);
  const [filteredClients, setFilteredClients] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadClients();
  }, []);

  useEffect(() => {
    filterClients();
  }, [searchQuery, clients]);

  const loadClients = async () => {
    try {
      const response = await apiService.clients.getAll();
      setClients(response.data || []);
    } catch (error) {
      console.error('Erreur chargement clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterClients = () => {
    if (!searchQuery) {
      setFilteredClients(clients);
    } else {
      const filtered = clients.filter(client =>
        client.nom?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        client.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        client.ville?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredClients(filtered);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadClients();
    setRefreshing(false);
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'Entreprise': return config.colors.primary;
      case 'Particulier': return config.colors.success;
      case 'Public': return config.colors.warning;
      default: return config.colors.dark;
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CH', {
      style: 'currency',
      currency: 'CHF',
    }).format(amount || 0);
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={config.colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Rechercher un client..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />
      
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <Card style={styles.statsCard}>
          <Card.Content>
            <View style={styles.statsRow}>
              <View style={styles.stat}>
                <Text style={styles.statValue}>{clients.length}</Text>
                <Text style={styles.statLabel}>Clients</Text>
              </View>
              <View style={styles.stat}>
                <Text style={styles.statValue}>
                  {clients.filter(c => c.projets_actifs > 0).length}
                </Text>
                <Text style={styles.statLabel}>Actifs</Text>
              </View>
              <View style={styles.stat}>
                <Text style={styles.statValue}>
                  {clients.reduce((sum, c) => sum + (c.projets_actifs || 0), 0)}
                </Text>
                <Text style={styles.statLabel}>Projets</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <List.Section>
          {filteredClients.map((client, index) => (
            <View key={client.id || index}>
              <List.Item
                title={client.nom}
                description={`${client.ville || 'N/A'} - ${client.email || ''}`}
                left={(props) => (
                  <Avatar.Text
                    {...props}
                    label={client.nom?.substring(0, 2).toUpperCase()}
                    size={40}
                  />
                )}
                right={(props) => (
                  <View style={styles.rightSection}>
                    <Chip
                      style={{ 
                        backgroundColor: getTypeColor(client.type),
                        marginBottom: 4
                      }}
                      textStyle={{ color: 'white', fontSize: 10 }}
                    >
                      {client.type}
                    </Chip>
                    <Text style={styles.caText}>
                      {formatCurrency(client.ca_total)}
                    </Text>
                  </View>
                )}
                onPress={() => Alert.alert('Client', client.nom)}
              />
              {index < filteredClients.length - 1 && <Divider />}
            </View>
          ))}
        </List.Section>
      </ScrollView>

      <FAB
        style={styles.fab}
        icon="plus"
        onPress={() => Alert.alert('Info', 'Ajouter un client')}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: config.colors.light,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  searchbar: {
    margin: 16,
    elevation: 2,
  },
  statsCard: {
    margin: 16,
    elevation: 2,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: config.colors.primary,
  },
  statLabel: {
    fontSize: 12,
    color: config.colors.dark,
    opacity: 0.7,
    marginTop: 4,
  },
  rightSection: {
    alignItems: 'flex-end',
  },
  caText: {
    fontSize: 12,
    color: config.colors.success,
    fontWeight: 'bold',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: config.colors.primary,
  },
});