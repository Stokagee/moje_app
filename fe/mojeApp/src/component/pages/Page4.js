/**
 * Page4 - Dispatch Dashboard
 * Food Delivery System - Phase 1
 *
 * Cekajici objednavky s urgency + dostupni kuryri v responsive split view
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  useWindowDimensions,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';
import Container from '../layout/Container';
import StatusBadge from '../common/StatusBadge';
import PriorityBadge from '../common/PriorityBadge';
import LoadingScreen from '../common/LoadingScreen';
import EmptyState from '../common/EmptyState';
import useApi from '../hooks/useApi';
import { API_ENDPOINTS } from '../../utils/apiConfig';
import {
  COURIER_STATUS_CONFIG,
  TAG_LABELS,
  TAG_ICONS,
  getUrgencyColor,
  getUrgencyLabel,
} from '../../utils/constants';

/**
 * Hlavni komponenta Page4 - Dispatch Dashboard
 */
export default function Page4({ navigation }) {
  const [pendingOrders, setPendingOrders] = useState([]);
  const [availableCouriers, setAvailableCouriers] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const { get, loading } = useApi();
  const { width } = useWindowDimensions();

  // Responsive breakpoint
  const isWideScreen = width >= 768;

  // Nacteni dat z API
  const fetchData = useCallback(async () => {
    try {
      const [ordersData, couriersData] = await Promise.all([
        get(API_ENDPOINTS.ORDERS_PENDING),
        get(API_ENDPOINTS.COURIERS_AVAILABLE),
      ]);
      setPendingOrders(ordersData || []);
      setAvailableCouriers(couriersData || []);
    } catch (err) {
      console.error('Chyba pri nacitani dispatch dat:', err);
    }
  }, [get]);

  // Prvotni nacteni + auto-refresh
  useEffect(() => {
    fetchData();

    // Auto-refresh kazdych 30 sekund
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Pull-to-refresh handler
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  }, [fetchData]);

  // Loading state - prvni nacteni
  if (
    loading &&
    pendingOrders.length === 0 &&
    availableCouriers.length === 0
  ) {
    return (
      <Container>
        <LoadingScreen
          visible={true}
          message="Nacitam dispatch data..."
          testID="dispatch-loading"
        />
      </Container>
    );
  }

  // Renderovani sekce cekajicich objednavek
  const renderPendingOrders = () => (
    <View
      style={[styles.section, isWideScreen && styles.sectionWide]}
      testID="pending-orders-section"
      nativeID="pending-orders-section"
      data-class="pending-orders-section"
    >
      <Text style={styles.sectionTitle}>
        Cekajici objednavky ({pendingOrders.length})
      </Text>

      {pendingOrders.length === 0 ? (
        <EmptyState
          icon="hourglass-empty"
          title="Zadne cekajici"
          message="Vsechny objednavky jsou prirazeny."
          testID="pending-orders-empty"
        />
      ) : (
        <ScrollView style={styles.sectionScroll}>
          {pendingOrders.map((order) => {
            const urgency = getUrgencyColor(order.created_at);
            return (
              <View
                key={order.id}
                style={[styles.card, { borderLeftColor: urgency.color }]}
                testID={`pending-order-card-${order.id}`}
                nativeID={`pending-order-card-${order.id}`}
                data-class="pending-order-card"
                data-order-id={order.id}
              >
                {/* Header */}
                <View style={styles.cardHeader}>
                  <Text style={styles.cardId}>#{order.id}</Text>
                  <View style={styles.badges}>
                    <PriorityBadge
                      isVip={order.is_vip}
                      testID={`pending-order-card-${order.id}-priority`}
                    />
                  </View>
                </View>

                {/* Urgency badge */}
                <View
                  style={[
                    styles.urgencyBadge,
                    { backgroundColor: urgency.backgroundColor },
                  ]}
                  testID={`pending-order-card-${order.id}-urgency`}
                  nativeID={`pending-order-card-${order.id}-urgency`}
                  data-class="urgency-badge"
                  data-urgency={urgency.label}
                >
                  <MaterialIcons
                    name="access-time"
                    size={14}
                    color={urgency.color}
                  />
                  <Text style={[styles.urgencyText, { color: urgency.color }]}>
                    {getUrgencyLabel(order.created_at)}
                  </Text>
                </View>

                {/* Info */}
                <View style={styles.cardInfo}>
                  <Text style={styles.infoText} numberOfLines={1}>
                    {order.customer_name}
                  </Text>
                  <Text style={styles.addressText} numberOfLines={1}>
                    {order.delivery_address}
                  </Text>
                </View>

                {/* Required tags */}
                {order.required_tags && order.required_tags.length > 0 && (
                  <View style={styles.tagsRow}>
                    {order.required_tags.map((tag) => (
                      <View key={tag} style={styles.tagChip}>
                        <MaterialIcons
                          name={TAG_ICONS[tag] || 'label'}
                          size={12}
                          color="#666"
                        />
                        <Text style={styles.tagText}>
                          {TAG_LABELS[tag] || tag}
                        </Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            );
          })}
        </ScrollView>
      )}
    </View>
  );

  // Renderovani sekce dostupnych kuryru
  const renderAvailableCouriers = () => (
    <View
      style={[styles.section, isWideScreen && styles.sectionWide]}
      testID="available-couriers-section"
      nativeID="available-couriers-section"
      data-class="available-couriers-section"
    >
      <Text style={styles.sectionTitle}>
        Dostupni kuryri ({availableCouriers.length})
      </Text>

      {availableCouriers.length === 0 ? (
        <EmptyState
          icon="delivery-dining"
          title="Zadni dostupni"
          message="Zadny kuryr neni momentalne k dispozici."
          testID="couriers-empty"
        />
      ) : (
        <ScrollView style={styles.sectionScroll}>
          {availableCouriers.map((courier) => (
            <View
              key={courier.id}
              style={styles.card}
              testID={`courier-card-${courier.id}`}
              nativeID={`courier-card-${courier.id}`}
              data-class="courier-card"
              data-courier-id={courier.id}
            >
              {/* Header */}
              <View style={styles.cardHeader}>
                <View style={styles.courierInfo}>
                  <MaterialIcons name="person" size={20} color="#333" />
                  <Text style={styles.courierName}>{courier.name}</Text>
                </View>
                <StatusBadge
                  status={courier.status}
                  statusConfig={COURIER_STATUS_CONFIG}
                  size="small"
                  testID={`courier-card-${courier.id}-status`}
                />
              </View>

              {/* Phone */}
              <View style={styles.phoneRow}>
                <MaterialIcons name="phone" size={14} color="#666" />
                <Text style={styles.phoneText}>{courier.phone}</Text>
              </View>

              {/* Tags */}
              {courier.tags && courier.tags.length > 0 && (
                <View
                  style={styles.tagsRow}
                  testID={`courier-card-${courier.id}-tags`}
                  nativeID={`courier-card-${courier.id}-tags`}
                  data-class="courier-tags"
                >
                  {courier.tags.map((tag) => (
                    <View key={tag} style={styles.tagChipBlue}>
                      <MaterialIcons
                        name={TAG_ICONS[tag] || 'label'}
                        size={12}
                        color="#007AFF"
                      />
                      <Text style={[styles.tagText, { color: '#007AFF' }]}>
                        {TAG_LABELS[tag] || tag}
                      </Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          ))}
        </ScrollView>
      )}
    </View>
  );

  return (
    <Container>
      {/* Header */}
      <View style={styles.header}>
        <Text
          style={styles.title}
          testID="page4-title"
          nativeID="page4-title"
          data-class="page-title"
        >
          Dispatch Dashboard
        </Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={onRefresh}
          testID="dispatch-refresh-button"
          nativeID="dispatch-refresh-button"
          accessibilityLabel="Obnovit data"
          accessibilityRole="button"
          data-class="btn refresh-btn"
        >
          <MaterialIcons name="refresh" size={24} color="#007AFF" />
        </TouchableOpacity>
      </View>

      {/* Stats panel */}
      <View
        style={styles.statsPanel}
        testID="dispatch-stats-panel"
        nativeID="dispatch-stats-panel"
        data-class="dispatch-stats"
      >
        <View style={styles.statItem}>
          <Text
            style={[styles.statNumber, { color: '#fd7e14' }]}
            testID="dispatch-pending-count"
          >
            {pendingOrders.length}
          </Text>
          <Text style={styles.statLabel}>Cekajici</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text
            style={[styles.statNumber, { color: '#28a745' }]}
            testID="dispatch-available-count"
          >
            {availableCouriers.length}
          </Text>
          <Text style={styles.statLabel}>Dostupni</Text>
        </View>
      </View>

      {/* Main content - responsive split view */}
      <ScrollView
        style={styles.mainContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        contentContainerStyle={
          isWideScreen ? styles.wideContentContainer : undefined
        }
      >
        {isWideScreen ? (
          <View style={styles.splitView}>
            {renderPendingOrders()}
            {renderAvailableCouriers()}
          </View>
        ) : (
          <>
            {renderPendingOrders()}
            {renderAvailableCouriers()}
          </>
        )}
      </ScrollView>
    </Container>
  );
}

const styles = StyleSheet.create({
  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingBottom: 12,
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

  // Stats panel
  statsPanel: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    marginVertical: 12,
  },
  statItem: {
    alignItems: 'center',
    paddingHorizontal: 30,
  },
  statNumber: {
    fontSize: 32,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#dee2e6',
  },

  // Main content
  mainContent: {
    flex: 1,
  },
  wideContentContainer: {
    flex: 1,
  },
  splitView: {
    flexDirection: 'row',
    flex: 1,
    gap: 16,
  },

  // Sections
  section: {
    flex: 1,
    marginBottom: 16,
  },
  sectionWide: {
    flex: 1,
    marginBottom: 0,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
    paddingBottom: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  sectionScroll: {
    flex: 1,
  },

  // Cards
  card: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#e9ecef',
    borderLeftWidth: 4,
    borderLeftColor: '#e9ecef',
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
  cardId: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#333',
  },
  badges: {
    flexDirection: 'row',
    gap: 6,
  },

  // Urgency
  urgencyBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
    marginBottom: 8,
  },
  urgencyText: {
    fontSize: 12,
    fontWeight: '600',
  },

  // Card info
  cardInfo: {
    gap: 4,
  },
  infoText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  addressText: {
    fontSize: 13,
    color: '#666',
  },

  // Courier
  courierInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  courierName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
  },
  phoneRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 8,
  },
  phoneText: {
    fontSize: 13,
    color: '#666',
  },

  // Tags
  tagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: 8,
  },
  tagChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
  },
  tagChipBlue: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4,
  },
  tagText: {
    fontSize: 11,
    color: '#666',
  },
});
