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
        <View
          style={styles.header}
          // === EMPTY STATE HEADER LOKÁTORY ===
          testID="page3-empty-header"
          nativeID="page3-empty-header"
          id="empty-header"
          data-component="page-header"
          data-page="page3"
          data-state="empty"
          data-class="page-header header-section"
          accessibilityRole="banner"
          aria-label="Hlavička stránky"
          className="page-header header-section"
        >
          <Text
            style={styles.title}
            // === EMPTY STATE TITLE LOKÁTORY ===
            testID="page3-title"
            nativeID="page3-title-empty"
            id="page3-title-empty"
            data-component="page-title"
            data-page="page3"
            data-state="empty"
            data-class="page-title heading"
            accessibilityRole="header"
            aria-label="Správa objednávek"
            aria-level="1"
            className="page-title heading"
          >
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
      <View
        style={styles.header}
        // === HEADER SECTION LOKÁTORY ===
        testID="page3-header"
        nativeID="page3-header"
        id="page3-header"
        data-component="page-header"
        data-page="page3"
        data-section="header"
        data-class="page-header header-section"
        accessibilityRole="banner"
        aria-label="Hlavička stránky objednávek"
        className="page-header header-section"
      >
        <Text
          style={styles.title}
          // === PAGE TITLE LOKÁTORY ===
          testID="page3-title"
          nativeID="page3-title"
          id="page3-heading"
          data-component="page-title"
          data-page="page3"
          data-class="page-title heading main-title"
          accessibilityRole="header"
          accessibilityLabel="Správa objednávek"
          aria-label="Správa objednávek"
          aria-level="1"
          className="page-title heading main-title"
        >
          Sprava objednavek
        </Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={onRefresh}
          // === REFRESH BUTTON LOKÁTORY ===
          testID="orders-refresh-button"
          nativeID="orders-refresh-button"
          id="refresh-btn"
          name="refresh"
          data-testid="orders-refresh-button"
          data-component="refresh-button"
          data-action="refresh-orders"
          data-class="btn btn-icon refresh-btn"
          accessibilityLabel="Obnovit seznam objednávek"
          accessibilityRole="button"
          accessibilityHint="Klikněte pro obnovení seznamu"
          aria-label="Obnovit seznam objednávek"
          className="btn btn-icon refresh-btn"
        >
          <MaterialIcons
            name="refresh"
            size={24}
            color="#007AFF"
            // === REFRESH ICON LOKÁTORY ===
            testID="refresh-icon"
            nativeID="refresh-icon"
            data-component="icon"
            data-icon="refresh"
            accessibilityLabel="Ikona obnovení"
          />
        </TouchableOpacity>
      </View>

      {/* Statistiky */}
      <View
        style={styles.statsRow}
        // === STATS PANEL LOKÁTORY ===
        testID="orders-stats-panel"
        nativeID="orders-stats-panel"
        id="stats-section"
        data-component="stats-panel"
        data-page="page3"
        data-section="statistics"
        data-class="stats-panel stats-row"
        accessibilityRole="region"
        accessibilityLabel="Statistiky objednávek"
        aria-label="Statistiky objednávek"
        className="stats-panel stats-row"
      >
        <View
          style={styles.statBox}
          // === STAT BOX - TOTAL LOKÁTORY ===
          testID="stat-box-total"
          nativeID="stat-total"
          id="stat-total"
          data-component="stat-box"
          data-stat="total"
          data-value={stats.total}
          data-class="stat-box stat-item"
          accessibilityRole="text"
          accessibilityLabel={`Celkem: ${stats.total}`}
          aria-label={`Celkem: ${stats.total}`}
          className="stat-box stat-item"
        >
          <Text
            style={styles.statNumber}
            // === STAT NUMBER - TOTAL LOKÁTORY ===
            testID="stat-number-total"
            nativeID="stat-value-total"
            data-component="stat-number"
            data-stat="total"
            data-class="stat-number"
            className="stat-number"
          >{stats.total}</Text>
          <Text
            style={styles.statLabel}
            // === STAT LABEL - TOTAL LOKÁTORY ===
            testID="stat-label-total"
            nativeID="stat-label-total"
            data-component="stat-label"
            data-class="stat-label"
            className="stat-label"
          >Celkem</Text>
        </View>
        <View
          style={styles.statBox}
          // === STAT BOX - PENDING LOKÁTORY ===
          testID="stat-box-pending"
          nativeID="stat-pending"
          id="stat-pending"
          data-component="stat-box"
          data-stat="pending"
          data-value={stats.pending}
          data-class="stat-box stat-item"
          accessibilityRole="text"
          accessibilityLabel={`Čekající: ${stats.pending}`}
          aria-label={`Čekající: ${stats.pending}`}
          className="stat-box stat-item"
        >
          <Text
            style={[styles.statNumber, { color: '#fd7e14' }]}
            // === STAT NUMBER - PENDING LOKÁTORY ===
            testID="stat-number-pending"
            nativeID="stat-value-pending"
            data-component="stat-number"
            data-stat="pending"
            data-class="stat-number stat-warning"
            className="stat-number stat-warning"
          >
            {stats.pending}
          </Text>
          <Text
            style={styles.statLabel}
            // === STAT LABEL - PENDING LOKÁTORY ===
            testID="stat-label-pending"
            nativeID="stat-label-pending"
            data-component="stat-label"
            data-class="stat-label"
            className="stat-label"
          >Cekajici</Text>
        </View>
        <View
          style={styles.statBox}
          // === STAT BOX - ACTIVE LOKÁTORY ===
          testID="stat-box-active"
          nativeID="stat-active"
          id="stat-active"
          data-component="stat-box"
          data-stat="active"
          data-value={stats.active}
          data-class="stat-box stat-item"
          accessibilityRole="text"
          accessibilityLabel={`Aktivní: ${stats.active}`}
          aria-label={`Aktivní: ${stats.active}`}
          className="stat-box stat-item"
        >
          <Text
            style={[styles.statNumber, { color: '#007bff' }]}
            // === STAT NUMBER - ACTIVE LOKÁTORY ===
            testID="stat-number-active"
            nativeID="stat-value-active"
            data-component="stat-number"
            data-stat="active"
            data-class="stat-number stat-info"
            className="stat-number stat-info"
          >
            {stats.active}
          </Text>
          <Text
            style={styles.statLabel}
            // === STAT LABEL - ACTIVE LOKÁTORY ===
            testID="stat-label-active"
            nativeID="stat-label-active"
            data-component="stat-label"
            data-class="stat-label"
            className="stat-label"
          >Aktivni</Text>
        </View>
        <View
          style={styles.statBox}
          // === STAT BOX - COMPLETED LOKÁTORY ===
          testID="stat-box-completed"
          nativeID="stat-completed"
          id="stat-completed"
          data-component="stat-box"
          data-stat="completed"
          data-value={stats.completed}
          data-class="stat-box stat-item"
          accessibilityRole="text"
          accessibilityLabel={`Dokončeno: ${stats.completed}`}
          aria-label={`Dokončeno: ${stats.completed}`}
          className="stat-box stat-item"
        >
          <Text
            style={[styles.statNumber, { color: '#28a745' }]}
            // === STAT NUMBER - COMPLETED LOKÁTORY ===
            testID="stat-number-completed"
            nativeID="stat-value-completed"
            data-component="stat-number"
            data-stat="completed"
            data-class="stat-number stat-success"
            className="stat-number stat-success"
          >
            {stats.completed}
          </Text>
          <Text
            style={styles.statLabel}
            // === STAT LABEL - COMPLETED LOKÁTORY ===
            testID="stat-label-completed"
            nativeID="stat-label-completed"
            data-component="stat-label"
            data-class="stat-label"
            className="stat-label"
          >Dokonceno</Text>
        </View>
      </View>

      {/* Seznam objednavek */}
      <ScrollView
        style={styles.listContainer}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        // === ORDERS LIST LOKÁTORY ===
        testID="orders-list"
        nativeID="orders-list"
        id="orders-scroll"
        data-component="orders-list"
        data-page="page3"
        data-count={orders.length}
        data-class="orders-list scroll-container"
        accessibilityRole="list"
        accessibilityLabel="Seznam objednávek"
        aria-label="Seznam objednávek"
        className="orders-list scroll-container"
      >
        {orders.map((order, index) => (
          <View
            key={order.id}
            style={styles.orderCard}
            // === ORDER CARD LOKÁTORY ===
            testID={`order-card-${order.id}`}
            nativeID={`order-card-${order.id}`}
            id={`order-${order.id}`}
            data-testid={`order-card-${order.id}`}
            data-component="order-card"
            data-order-id={order.id}
            data-order-status={order.status}
            data-order-vip={order.is_vip ? 'true' : 'false'}
            data-index={index}
            data-class="order-card card list-item"
            accessibilityRole="listitem"
            accessibilityLabel={`Objednávka ${order.id} - ${order.customer_name}`}
            aria-label={`Objednávka ${order.id}`}
            className="order-card card list-item"
          >
            {/* Horni radek: ID, Status, Priority */}
            <View
              style={styles.cardHeader}
              // === CARD HEADER LOKÁTORY ===
              testID={`order-card-${order.id}-header`}
              nativeID={`order-header-${order.id}`}
              data-component="card-header"
              data-class="card-header order-header"
              className="card-header order-header"
            >
              <Text
                style={styles.orderId}
                // === ORDER ID TEXT LOKÁTORY ===
                testID={`order-card-${order.id}-id`}
                nativeID={`order-id-${order.id}`}
                data-component="order-id"
                data-order-id={order.id}
                data-class="order-id"
                accessibilityRole="text"
                className="order-id"
              >#{order.id}</Text>
              <View
                style={styles.badges}
                // === BADGES CONTAINER LOKÁTORY ===
                testID={`order-card-${order.id}-badges`}
                nativeID={`order-badges-${order.id}`}
                data-component="badges-container"
                data-class="badges badge-group"
                className="badges badge-group"
              >
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
            <View
              style={styles.cardBody}
              // === CARD BODY LOKÁTORY ===
              testID={`order-card-${order.id}-body`}
              nativeID={`order-body-${order.id}`}
              data-component="card-body"
              data-class="card-body order-info"
              className="card-body order-info"
            >
              <View
                style={styles.infoRow}
                // === CUSTOMER ROW LOKÁTORY ===
                testID={`order-card-${order.id}-customer-row`}
                nativeID={`order-customer-row-${order.id}`}
                data-component="info-row"
                data-info="customer"
                data-class="info-row customer-row"
                className="info-row customer-row"
              >
                <MaterialIcons
                  name="person"
                  size={16}
                  color="#666"
                  // === CUSTOMER ICON LOKÁTORY ===
                  testID={`order-card-${order.id}-customer-icon`}
                  nativeID={`customer-icon-${order.id}`}
                  data-component="icon"
                  data-icon="person"
                  accessibilityLabel="Zákazník"
                />
                <Text
                  style={styles.infoText}
                  // === CUSTOMER TEXT LOKÁTORY ===
                  testID={`order-card-${order.id}-customer`}
                  nativeID={`order-customer-${order.id}`}
                  id={`customer-name-${order.id}`}
                  data-component="customer-name"
                  data-customer={order.customer_name}
                  data-class="info-text customer-name"
                  accessibilityRole="text"
                  accessibilityLabel={`Zákazník: ${order.customer_name}`}
                  className="info-text customer-name"
                  numberOfLines={1}
                >
                  {order.customer_name}
                </Text>
              </View>
              <View
                style={styles.infoRow}
                // === ADDRESS ROW LOKÁTORY ===
                testID={`order-card-${order.id}-address-row`}
                nativeID={`order-address-row-${order.id}`}
                data-component="info-row"
                data-info="address"
                data-class="info-row address-row"
                className="info-row address-row"
              >
                <MaterialIcons
                  name="location-on"
                  size={16}
                  color="#666"
                  // === ADDRESS ICON LOKÁTORY ===
                  testID={`order-card-${order.id}-address-icon`}
                  nativeID={`address-icon-${order.id}`}
                  data-component="icon"
                  data-icon="location-on"
                  accessibilityLabel="Adresa"
                />
                <Text
                  style={styles.infoText}
                  // === ADDRESS TEXT LOKÁTORY ===
                  testID={`order-card-${order.id}-address`}
                  nativeID={`order-address-${order.id}`}
                  id={`delivery-address-${order.id}`}
                  data-component="delivery-address"
                  data-address={order.delivery_address}
                  data-class="info-text delivery-address"
                  accessibilityRole="text"
                  accessibilityLabel={`Adresa: ${order.delivery_address}`}
                  className="info-text delivery-address"
                  numberOfLines={1}
                >
                  {order.delivery_address}
                </Text>
              </View>
            </View>

            {/* Cas vytvoreni */}
            <View
              style={styles.cardFooter}
              // === CARD FOOTER LOKÁTORY ===
              testID={`order-card-${order.id}-footer`}
              nativeID={`order-footer-${order.id}`}
              data-component="card-footer"
              data-class="card-footer order-footer"
              className="card-footer order-footer"
            >
              <Text
                style={styles.timestamp}
                // === TIMESTAMP LOKÁTORY ===
                testID={`order-card-${order.id}-timestamp`}
                nativeID={`order-timestamp-${order.id}`}
                data-component="timestamp"
                data-created={order.created_at}
                data-class="timestamp order-time"
                accessibilityRole="text"
                accessibilityLabel={`Vytvořeno: ${new Date(order.created_at).toLocaleString('cs-CZ')}`}
                className="timestamp order-time"
              >
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
