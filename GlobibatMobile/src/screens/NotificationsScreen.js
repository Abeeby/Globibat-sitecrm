import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
} from 'react-native';
import {
  List,
  IconButton,
  Chip,
  Surface,
  Button,
  FAB,
} from 'react-native-paper';
import { useSocket } from '../contexts/SocketContext';
import { useNotifications } from '../contexts/NotificationContext';
import config from '../config';
import moment from 'moment';
import 'moment/locale/fr';

moment.locale('fr');

export default function NotificationsScreen() {
  const [refreshing, setRefreshing] = useState(false);
  const { notifications, removeNotification, clearNotifications } = useSocket();
  const { clearAllNotifications } = useNotifications();

  const onRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  const handleClearAll = async () => {
    clearNotifications();
    await clearAllNotifications();
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'badge': return 'badge-account';
      case 'message': return 'message';
      case 'alert': return 'alert';
      case 'info': return 'information';
      case 'success': return 'check-circle';
      case 'warning': return 'alert-circle';
      case 'danger': return 'close-circle';
      default: return 'bell';
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'success': return config.colors.success;
      case 'warning': return config.colors.warning;
      case 'danger': return config.colors.danger;
      case 'info': return config.colors.info;
      default: return config.colors.primary;
    }
  };

  const renderNotification = ({ item }) => (
    <Surface style={styles.notificationCard}>
      <View style={styles.notificationContent}>
        <View style={[styles.iconContainer, { backgroundColor: getNotificationColor(item.type) + '20' }]}>
          <IconButton
            icon={getNotificationIcon(item.type)}
            size={24}
            iconColor={getNotificationColor(item.type)}
          />
        </View>
        <View style={styles.textContainer}>
          <Text style={styles.title}>{item.title}</Text>
          <Text style={styles.message}>{item.message}</Text>
          <Text style={styles.time}>
            {moment(item.time).fromNow()}
          </Text>
        </View>
        <IconButton
          icon="close"
          size={20}
          onPress={() => removeNotification(item.id)}
          style={styles.closeButton}
        />
      </View>
    </Surface>
  );

  const EmptyComponent = () => (
    <View style={styles.emptyContainer}>
      <IconButton
        icon="bell-off"
        size={64}
        iconColor={config.colors.dark}
        style={{ opacity: 0.3 }}
      />
      <Text style={styles.emptyText}>Aucune notification</Text>
      <Text style={styles.emptySubtext}>
        Vous recevrez ici les alertes et messages importants
      </Text>
    </View>
  );

  return (
    <View style={styles.container}>
      {notifications.length > 0 && (
        <View style={styles.header}>
          <Text style={styles.count}>
            {notifications.length} notification{notifications.length > 1 ? 's' : ''}
          </Text>
          <Button
            mode="text"
            onPress={handleClearAll}
            textColor={config.colors.danger}
          >
            Tout effacer
          </Button>
        </View>
      )}

      <FlatList
        data={notifications}
        renderItem={renderNotification}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={EmptyComponent}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: config.colors.light,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: 'white',
    elevation: 2,
  },
  count: {
    fontSize: 14,
    fontWeight: '500',
    color: config.colors.dark,
  },
  list: {
    paddingVertical: 8,
  },
  notificationCard: {
    marginHorizontal: 16,
    marginVertical: 4,
    padding: 12,
    borderRadius: 8,
    elevation: 2,
    backgroundColor: 'white',
  },
  notificationContent: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  textContainer: {
    flex: 1,
  },
  title: {
    fontSize: 14,
    fontWeight: 'bold',
    color: config.colors.dark,
    marginBottom: 4,
  },
  message: {
    fontSize: 13,
    color: config.colors.dark,
    opacity: 0.8,
    marginBottom: 6,
  },
  time: {
    fontSize: 11,
    color: config.colors.dark,
    opacity: 0.5,
  },
  closeButton: {
    margin: -8,
  },
  separator: {
    height: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 100,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: config.colors.dark,
    opacity: 0.5,
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: config.colors.dark,
    opacity: 0.3,
    marginTop: 8,
    textAlign: 'center',
    paddingHorizontal: 40,
  },
});