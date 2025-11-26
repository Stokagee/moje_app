/**
 * Page3 - Sprava objednavek
 * Food Delivery System - Phase 1
 *
 * Read-only seznam vsech objednavek s barevnymi statusy a statistikami
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import Container from '../layout/Container';
import StatusBadge from '../common/StatusBadge';
import PriorityBadge from '../common/PriorityBadge';
import LoadingScreen from '../common/LoadingScreen';
import EmptyState from '../common/EmptyState';
import useApi from '../hooks/useApi';
import { API_ENDPOINTS } from '../../utils/apiConfig';
import { ORDER_STATUS_CONFIG, ORDER_STATUSES } from '../../utils/constants';

/**
 * Hlavni komponenta Page3 - Sprava objednavek
 */
export default function Page3({ navigation }) {
  const [orders, setOrders] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const { get, loading } = useApi();

  // Nacteni objednavek z API
  const fetchOrders = useCallback(async () => {
    try {
      const data = await get(API_ENDPOINTS.ORDERS);
      setOrders(data || []);
    } catch (err) {
      console.error('Chyba pri nacitani objednavek:', err);
    }
  }, [get]);

  // Prvotni nacteni pri mount
  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  // Pull-to-refresh handler
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchOrders();
    setRefreshing(false);
  }, [fetchOrders]);

  // Vypocet statistik
  const stats = {
    total: orders.length,
    pending: orders.filter(
      (o) =>
        o.status === ORDER_STATUSES.CREATED ||
        o.status === ORDER_STATUSES.SEARCHING
    ).length,
    active: orders.filter(
      (o) =>
        o.status === ORDER_STATUSES.ASSIGNED ||
        o.status === ORDER_STATUSES.PICKED
    ).length,
    completed: orders.filter((o) => o.status === ORDER_STATUSES.DELIVERED)
      .length,
  };

  // Loading state - prvni nacteni
  if (loading && orders.length === 0) {
    return (
      <Container>
        <LoadingScreen
          visible={true}
          message="Nacitam objednavky..."
          testID="orders-loading"
        />
      </Container>
    );
  }

  // Empty state - zadne objednavky
  if (!loading && orders.length === 0) {
    return (
      <Container>
        <View style={styles.header}>
          <Text style={styles.title} testID="page3-title">
            Sprava objednavek
          </Text>
        </View>
        <EmptyState
          icon="receipt"
          title="Zadne objednavky"
          message="Zatim nebyla vytvorena zadna objednavka."
          action={{
            label: 'Obnovit',
            onPress: fetchOrders,
          }}
          testID="orders-empty-state"
        />
      </Container>
    );
  }

  return (
    <Container>
      {/* Header s nazvem a tlacitkem refresh */}
      <View style={styles.header}>
        <Text
          style={styles.title}
          testID="page3-title"
          nativeID="page3-title"
          data-class="page-title"
        >
          Sprava objednavek
        </Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={onRefresh}
          testID="orders-refresh-button"
          nativeID="orders-refresh-button"
          accessibilityLabel="Obnovit seznam"
          accessibilityRole="button"
          data-class="btn refresh-btn"
        >
          <MaterialIcons name="refresh" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      {/* Statistiky */}
      <View
        style={styles.statsRow}
        testID="orders-stats-panel"
        data-class="stats-panel"
      >
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>{stats.total}</Text>
          <Text style={styles.statLabel}>Celkem</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statNumber, { color: '#fd7e14' }]}>
            {stats.pending}
          </Text>
          <Text style={styles.statLabel}>Cekajici</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statNumber, { color: '#007bff' }]}>
            {stats.active}
          </Text>
          <Text style={styles.statLabel}>Aktivni</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={[styles.statNumber, { color: '#28a745' }]}>
            {stats.completed}
          </Text>
          <Text style={styles.statLabel}>Dokonceno</Text>
        </View>
      </View>

      {/* Seznam objednavek */}
      <ScrollView
        style={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        testID="orders-list"
        nativeID="orders-list"
        data-class="orders-list"
      >
        {orders.map((order) => (
          <View
            key={order.id}
            style={styles.orderCard}
            testID={`order-card-${order.id}`}
            nativeID={`order-card-${order.id}`}
            accessibilityRole="listitem"
            data-class="order-card"
            data-order-id={order.id}
          >
            {/* Horni radek: ID, Status, Priority */}
            <View style={styles.cardHeader}>
              <Text style={styles.orderId}>#{order.id}</Text>
              <View style={styles.badges}>
                <PriorityBadge
                  isVip={order.is_vip}
                  testID={`order-card-${order.id}-priority`}
                />
                <StatusBadge
                  status={order.status}
                  statusConfig={ORDER_STATUS_CONFIG}
                  size="small"
                  testID={`order-card-${order.id}-status`}
                />
              </View>
            </View>

            {/* Info o zakaznikovi */}
            <View style={styles.cardBody}>
              <View style={styles.infoRow}>
                <MaterialIcons name="person" size={16} color="#666" />
                <Text
                  style={styles.infoText}
                  testID={`order-card-${order.id}-customer`}
                  numberOfLines={1}
                >
                  {order.customer_name}
                </Text>
              </View>
              <View style={styles.infoRow}>
                <MaterialIcons name="location-on" size={16} color="#666" />
                <Text
                  style={styles.infoText}
                  testID={`order-card-${order.id}-address`}
                  numberOfLines={1}
                >
                  {order.delivery_address}
                </Text>
              </View>
            </View>

            {/* Cas vytvoreni */}
            <View style={styles.cardFooter}>
              <Text style={styles.timestamp}>
                {new Date(order.created_at).toLocaleString('cs-CZ')}
              </Text>
            </View>
          </View>
        ))}
      </ScrollView>
    </Container>
  );
}

const styles = StyleSheet.create({
  // Header sekce
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  refreshButton: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: '#f0f7ff',
  },

  // Statistiky
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    marginVertical: 12,
  },
  statBox: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },

  // Seznam
  listContainer: {
    flex: 1,
  },

  // Order karta
  orderCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e9ecef',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  orderId: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  badges: {
    flexDirection: 'row',
    gap: 8,
  },
  cardBody: {
    gap: 6,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#555',
  },
  cardFooter: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  timestamp: {
    fontSize: 12,
    color: '#999',
  },
});
