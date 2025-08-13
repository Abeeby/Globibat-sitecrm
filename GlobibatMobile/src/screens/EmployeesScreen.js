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

export default function EmployeesScreen() {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadEmployees();
  }, []);

  useEffect(() => {
    filterEmployees();
  }, [searchQuery, employees]);

  const loadEmployees = async () => {
    try {
      const response = await apiService.employees.getAll();
      setEmployees(response.data || []);
    } catch (error) {
      console.error('Erreur chargement employés:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterEmployees = () => {
    if (!searchQuery) {
      setFilteredEmployees(employees);
    } else {
      const filtered = employees.filter(emp =>
        emp.nom?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        emp.prenom?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        emp.matricule?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredEmployees(filtered);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadEmployees();
    setRefreshing(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Actif': return config.colors.success;
      case 'En congé': return config.colors.warning;
      case 'Maladie': return config.colors.danger;
      default: return config.colors.dark;
    }
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
        placeholder="Rechercher par nom ou matricule..."
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
                <Text style={styles.statValue}>{employees.length}</Text>
                <Text style={styles.statLabel}>Total</Text>
              </View>
              <View style={styles.stat}>
                <Text style={styles.statValue}>
                  {employees.filter(e => e.statut === 'Actif').length}
                </Text>
                <Text style={styles.statLabel}>Actifs</Text>
              </View>
              <View style={styles.stat}>
                <Text style={styles.statValue}>
                  {employees.filter(e => e.statut === 'En congé').length}
                </Text>
                <Text style={styles.statLabel}>En congé</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        <List.Section>
          {filteredEmployees.map((employee, index) => (
            <View key={employee.id || index}>
              <List.Item
                title={`${employee.prenom} ${employee.nom}`}
                description={`${employee.matricule} - ${employee.poste || 'N/A'}`}
                left={(props) => (
                  <Avatar.Text
                    {...props}
                    label={`${employee.prenom?.[0]}${employee.nom?.[0]}`}
                    size={40}
                  />
                )}
                right={(props) => (
                  <Chip
                    style={{ backgroundColor: getStatusColor(employee.statut) }}
                    textStyle={{ color: 'white' }}
                  >
                    {employee.statut}
                  </Chip>
                )}
                onPress={() => Alert.alert('Employé', `${employee.prenom} ${employee.nom}`)}
              />
              {index < filteredEmployees.length - 1 && <Divider />}
            </View>
          ))}
        </List.Section>
      </ScrollView>

      <FAB
        style={styles.fab}
        icon="plus"
        onPress={() => Alert.alert('Info', 'Ajouter un employé')}
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
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: config.colors.primary,
  },
});