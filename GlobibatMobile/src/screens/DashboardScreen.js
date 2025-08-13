import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Dimensions,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  List,
  Divider,
  IconButton,
  Surface,
  Chip,
  ActivityIndicator,
  FAB,
} from 'react-native-paper';
import { LineChart, BarChart } from 'react-native-chart-kit';
import { useNavigation } from '@react-navigation/native';
import { useSocket } from '../contexts/SocketContext';
import { apiService } from '../services/api';
import config from '../config';
import moment from 'moment';
import 'moment/locale/fr';

moment.locale('fr');
const { width } = Dimensions.get('window');

export default function DashboardScreen() {
  const navigation = useNavigation();
  const { connected, notifications, badgeUpdates } = useSocket();
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    employees_actifs: 0,
    employees_presents: 0,
    chantiers_actifs: 0,
    factures_impayees: 0,
    ca_mois: 0,
    badges_jour: 0,
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [statsResponse, activityResponse] = await Promise.all([
        apiService.dashboard.getStats(),
        apiService.dashboard.getRecentActivity(),
      ]);

      setStats(statsResponse.data);
      setRecentActivity(activityResponse.data || []);
      
      // Préparer les données pour le graphique
      prepareChartData(statsResponse.data);
    } catch (error) {
      console.error('Erreur chargement dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const prepareChartData = (data) => {
    // Données simulées pour le graphique
    setChartData({
      labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
      datasets: [
        {
          data: [20, 45, 28, 80, 99, 43, 50],
          color: (opacity = 1) => `rgba(0, 91, 187, ${opacity})`,
        },
      ],
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CH', {
      style: 'currency',
      currency: 'CHF',
    }).format(amount);
  };

  const KPICard = ({ title, value, subtitle, icon, color = config.colors.primary }) => (
    <Card style={styles.kpiCard}>
      <Card.Content>
        <View style={styles.kpiHeader}>
          <View style={[styles.kpiIcon, { backgroundColor: color + '20' }]}>
            <IconButton icon={icon} size={24} iconColor={color} />
          </View>
        </View>
        <Title style={styles.kpiValue}>{value}</Title>
        <Paragraph style={styles.kpiTitle}>{title}</Paragraph>
        {subtitle && (
          <Text style={styles.kpiSubtitle}>{subtitle}</Text>
        )}
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={config.colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Statut de connexion */}
        <Surface style={styles.statusBar}>
          <View style={styles.statusContent}>
            <Chip
              icon="wifi"
              style={[
                styles.statusChip,
                { backgroundColor: connected ? config.colors.success : config.colors.danger }
              ]}
              textStyle={{ color: 'white' }}
            >
              {connected ? 'Connecté' : 'Hors ligne'}
            </Chip>
            <Text style={styles.dateText}>
              {moment().format('dddd D MMMM YYYY')}
            </Text>
          </View>
        </Surface>

        {/* KPI Cards */}
        <View style={styles.kpiContainer}>
          <View style={styles.kpiRow}>
            <KPICard
              title="Employés actifs"
              value={stats.employees_actifs}
              icon="account-group"
              color={config.colors.primary}
            />
            <KPICard
              title="Présents"
              value={stats.employees_presents}
              subtitle={`sur ${stats.employees_actifs}`}
              icon="account-check"
              color={config.colors.success}
            />
          </View>
          <View style={styles.kpiRow}>
            <KPICard
              title="Chantiers actifs"
              value={stats.chantiers_actifs}
              icon="hammer"
              color={config.colors.warning}
            />
            <KPICard
              title="Factures impayées"
              value={stats.factures_impayees}
              icon="file-document"
              color={config.colors.danger}
            />
          </View>
        </View>

        {/* CA du mois */}
        <Card style={styles.caCard}>
          <Card.Title
            title="Chiffre d'affaires du mois"
            left={(props) => <IconButton {...props} icon="cash" />}
          />
          <Card.Content>
            <Title style={styles.caAmount}>
              {formatCurrency(stats.ca_mois)}
            </Title>
            {chartData && (
              <LineChart
                data={chartData}
                width={width - 64}
                height={180}
                chartConfig={{
                  backgroundColor: 'white',
                  backgroundGradientFrom: 'white',
                  backgroundGradientTo: 'white',
                  decimalPlaces: 0,
                  color: (opacity = 1) => `rgba(0, 91, 187, ${opacity})`,
                  labelColor: (opacity = 1) => `rgba(44, 62, 80, ${opacity})`,
                  style: {
                    borderRadius: 8,
                  },
                  propsForDots: {
                    r: '4',
                    strokeWidth: '2',
                    stroke: config.colors.primary,
                  },
                }}
                bezier
                style={styles.chart}
              />
            )}
          </Card.Content>
        </Card>

        {/* Activité récente */}
        <Card style={styles.activityCard}>
          <Card.Title
            title="Activité récente"
            subtitle={`${recentActivity.length} événements`}
            left={(props) => <IconButton {...props} icon="history" />}
            right={(props) => (
              <IconButton
                {...props}
                icon="refresh"
                onPress={loadDashboardData}
              />
            )}
          />
          <Card.Content>
            {recentActivity.length === 0 ? (
              <Text style={styles.emptyText}>Aucune activité récente</Text>
            ) : (
              <List.Section>
                {recentActivity.slice(0, 5).map((activity, index) => (
                  <View key={index}>
                    <List.Item
                      title={activity.title}
                      description={activity.description}
                      left={(props) => (
                        <List.Icon
                          {...props}
                          icon={activity.icon || 'information'}
                          color={activity.color || config.colors.primary}
                        />
                      )}
                      right={(props) => (
                        <Text style={styles.timeText}>
                          {moment(activity.time).fromNow()}
                        </Text>
                      )}
                    />
                    {index < recentActivity.length - 1 && <Divider />}
                  </View>
                ))}
              </List.Section>
            )}
          </Card.Content>
        </Card>

        {/* Badges en temps réel */}
        {badgeUpdates.length > 0 && (
          <Card style={styles.badgeCard}>
            <Card.Title
              title="Derniers badges"
              left={(props) => <IconButton {...props} icon="badge-account" />}
            />
            <Card.Content>
              {badgeUpdates.slice(0, 3).map((badge, index) => (
                <Chip
                  key={index}
                  icon="account"
                  style={styles.badgeChip}
                  mode="outlined"
                >
                  {badge.employe} - {badge.type}
                </Chip>
              ))}
            </Card.Content>
          </Card>
        )}
      </ScrollView>

      {/* FAB pour badge rapide */}
      <FAB
        style={styles.fab}
        icon="badge-account"
        onPress={() => navigation.navigate('Badges')}
        label="Badge"
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
  statusBar: {
    margin: 16,
    padding: 12,
    borderRadius: 8,
    elevation: 2,
  },
  statusContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusChip: {
    borderRadius: 16,
  },
  dateText: {
    fontSize: 14,
    color: config.colors.dark,
    opacity: 0.7,
  },
  kpiContainer: {
    paddingHorizontal: 16,
  },
  kpiRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  kpiCard: {
    flex: 1,
    marginHorizontal: 4,
    elevation: 2,
  },
  kpiHeader: {
    marginBottom: 8,
  },
  kpiIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  kpiValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: config.colors.dark,
  },
  kpiTitle: {
    fontSize: 14,
    color: config.colors.dark,
    opacity: 0.7,
    marginTop: 4,
  },
  kpiSubtitle: {
    fontSize: 12,
    color: config.colors.dark,
    opacity: 0.5,
    marginTop: 2,
  },
  caCard: {
    margin: 16,
    elevation: 2,
  },
  caAmount: {
    fontSize: 28,
    color: config.colors.primary,
    marginBottom: 16,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 8,
  },
  activityCard: {
    margin: 16,
    elevation: 2,
  },
  emptyText: {
    textAlign: 'center',
    color: config.colors.dark,
    opacity: 0.5,
    paddingVertical: 20,
  },
  timeText: {
    fontSize: 12,
    color: config.colors.dark,
    opacity: 0.5,
  },
  badgeCard: {
    margin: 16,
    marginBottom: 80,
    elevation: 2,
  },
  badgeChip: {
    marginVertical: 4,
    alignSelf: 'flex-start',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: config.colors.primary,
  },
});