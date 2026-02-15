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
import logger from '../../utils/lokiLogger';

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
      logger.error('Failed to load dispatch data', {
        error: err.message,
        stack: err.stack,
        endpoints: [API_ENDPOINTS.ORDERS_PENDING, API_ENDPOINTS.COURIERS_AVAILABLE],
      });
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
      // === PENDING ORDERS SECTION LOKÁTORY ===
      testID="pending-orders-section"
      nativeID="pending-orders-section"
      id="pending-orders"
      data-testid="pending-orders-section"
      data-component="orders-section"
      data-section="pending-orders"
      data-count={pendingOrders.length}
      data-class="section pending-orders-section"
      accessibilityRole="none"
      accessibilityLabel="Čekající objednávky"
      aria-label="Čekající objednávky"
      className="section pending-orders-section"
    >
      <Text
        style={styles.sectionTitle}
        // === SECTION TITLE LOKÁTORY ===
        testID="pending-orders-title"
        nativeID="pending-orders-title"
        id="pending-title"
        data-component="section-title"
        data-section="pending-orders"
        data-class="section-title heading"
        accessibilityRole="header"
        aria-level="2"
        className="section-title heading"
      >
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
        <ScrollView
          style={styles.sectionScroll}
          // === PENDING ORDERS SCROLL LOKÁTORY ===
          testID="pending-orders-scroll"
          nativeID="pending-orders-scroll"
          id="pending-scroll"
          data-component="orders-scroll"
          data-section="pending-orders"
          data-class="section-scroll orders-scroll"
          accessibilityRole="none"
          aria-label="Seznam čekajících objednávek"
          className="section-scroll orders-scroll"
        >
          {pendingOrders.map((order, index) => {
            const urgency = getUrgencyColor(order.created_at);
            return (
              <View
                key={order.id}
                style={[styles.card, { borderLeftColor: urgency.color }]}
                // === PENDING ORDER CARD LOKÁTORY ===
                testID={`pending-order-card-${order.id}`}
                nativeID={`pending-order-card-${order.id}`}
                id={`pending-order-${order.id}`}
                data-testid={`pending-order-card-${order.id}`}
                data-component="pending-order-card"
                data-order-id={order.id}
                data-order-vip={order.is_vip ? 'true' : 'false'}
                data-urgency={urgency.label}
                data-index={index}
                data-class="card pending-order-card"
                accessibilityRole="none"
                accessibilityLabel={`Čekající objednávka ${order.id}`}
                aria-label={`Čekající objednávka ${order.id}`}
                className="card pending-order-card"
              >
                {/* Header */}
                <View
                  style={styles.cardHeader}
                  // === CARD HEADER LOKÁTORY ===
                  testID={`pending-order-card-${order.id}-header`}
                  nativeID={`pending-header-${order.id}`}
                  data-component="card-header"
                  data-class="card-header"
                  className="card-header"
                >
                  <Text
                    style={styles.cardId}
                    // === ORDER ID LOKÁTORY ===
                    testID={`pending-order-card-${order.id}-id`}
                    nativeID={`pending-id-${order.id}`}
                    data-component="order-id"
                    data-order-id={order.id}
                    data-class="card-id order-id"
                    accessibilityRole="text"
                    className="card-id order-id"
                  >#{order.id}</Text>
                  <View
                    style={styles.badges}
                    // === BADGES CONTAINER LOKÁTORY ===
                    testID={`pending-order-card-${order.id}-badges`}
                    nativeID={`pending-badges-${order.id}`}
                    data-component="badges"
                    data-class="badges badge-group"
                    className="badges badge-group"
                  >
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
                  // === URGENCY BADGE LOKÁTORY ===
                  testID={`pending-order-card-${order.id}-urgency`}
                  nativeID={`pending-order-card-${order.id}-urgency`}
                  id={`urgency-badge-${order.id}`}
                  data-testid={`pending-order-card-${order.id}-urgency`}
                  data-component="urgency-badge"
                  data-urgency={urgency.label}
                  data-class="urgency-badge badge"
                  accessibilityRole="text"
                  accessibilityLabel={`Naléhavost: ${urgency.label}`}
                  aria-label={`Naléhavost: ${urgency.label}`}
                  className="urgency-badge badge"
                >
                  <MaterialIcons
                    name="access-time"
                    size={14}
                    color={urgency.color}
                    // === URGENCY ICON LOKÁTORY ===
                    testID={`pending-order-card-${order.id}-urgency-icon`}
                    nativeID={`urgency-icon-${order.id}`}
                    data-component="icon"
                    data-icon="access-time"
                    accessibilityLabel="Ikona času"
                  />
                  <Text
                    style={[styles.urgencyText, { color: urgency.color }]}
                    // === URGENCY TEXT LOKÁTORY ===
                    testID={`pending-order-card-${order.id}-urgency-text`}
                    nativeID={`urgency-text-${order.id}`}
                    data-component="urgency-text"
                    data-class="urgency-text"
                    className="urgency-text"
                  >
                    {getUrgencyLabel(order.created_at)}
                  </Text>
                </View>

                {/* Info */}
                <View
                  style={styles.cardInfo}
                  // === CARD INFO LOKÁTORY ===
                  testID={`pending-order-card-${order.id}-info`}
                  nativeID={`pending-info-${order.id}`}
                  data-component="card-info"
                  data-class="card-info order-info"
                  className="card-info order-info"
                >
                  <Text
                    style={styles.infoText}
                    numberOfLines={1}
                    // === CUSTOMER NAME LOKÁTORY ===
                    testID={`pending-order-card-${order.id}-customer`}
                    nativeID={`pending-customer-${order.id}`}
                    data-component="customer-name"
                    data-customer={order.customer_name}
                    data-class="info-text customer-name"
                    accessibilityRole="text"
                    accessibilityLabel={`Zákazník: ${order.customer_name}`}
                    className="info-text customer-name"
                  >
                    {order.customer_name}
                  </Text>
                  <Text
                    style={styles.addressText}
                    numberOfLines={1}
                    // === ADDRESS TEXT LOKÁTORY ===
                    testID={`pending-order-card-${order.id}-address`}
                    nativeID={`pending-address-${order.id}`}
                    data-component="delivery-address"
                    data-address={order.delivery_address}
                    data-class="address-text delivery-address"
                    accessibilityRole="text"
                    accessibilityLabel={`Adresa: ${order.delivery_address}`}
                    className="address-text delivery-address"
                  >
                    {order.delivery_address}
                  </Text>
                </View>

                {/* Required tags */}
                {order.required_tags && order.required_tags.length > 0 && (
                  <View
                    style={styles.tagsRow}
                    // === REQUIRED TAGS LOKÁTORY ===
                    testID={`pending-order-card-${order.id}-tags`}
                    nativeID={`pending-tags-${order.id}`}
                    data-component="required-tags"
                    data-tags={order.required_tags.join(',')}
                    data-class="tags-row required-tags"
                    accessibilityRole="none"
                    accessibilityLabel="Požadované tagy"
                    className="tags-row required-tags"
                  >
                    {order.required_tags.map((tag, tagIndex) => (
                      <View
                        key={tag}
                        style={styles.tagChip}
                        // === TAG CHIP LOKÁTORY ===
                        testID={`pending-order-card-${order.id}-tag-${tag}`}
                        nativeID={`pending-tag-${order.id}-${tag}`}
                        data-component="tag-chip"
                        data-tag={tag}
                        data-index={tagIndex}
                        data-class="tag-chip tag"
                        accessibilityRole="text"
                        accessibilityLabel={TAG_LABELS[tag] || tag}
                        className="tag-chip tag"
                      >
                        <MaterialIcons
                          name={TAG_ICONS[tag] || 'label'}
                          size={12}
                          color="#666"
                          // === TAG ICON LOKÁTORY ===
                          testID={`pending-tag-icon-${order.id}-${tag}`}
                          data-component="tag-icon"
                          data-icon={TAG_ICONS[tag] || 'label'}
                        />
                        <Text
                          style={styles.tagText}
                          // === TAG TEXT LOKÁTORY ===
                          testID={`pending-tag-text-${order.id}-${tag}`}
                          nativeID={`pending-tag-label-${order.id}-${tag}`}
                          data-component="tag-text"
                          data-class="tag-text"
                          className="tag-text"
                        >
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
      // === AVAILABLE COURIERS SECTION LOKÁTORY ===
      testID="available-couriers-section"
      nativeID="available-couriers-section"
      id="available-couriers"
      data-testid="available-couriers-section"
      data-component="couriers-section"
      data-section="available-couriers"
      data-count={availableCouriers.length}
      data-class="section available-couriers-section"
      accessibilityRole="none"
      accessibilityLabel="Dostupní kurýři"
      aria-label="Dostupní kurýři"
      className="section available-couriers-section"
    >
      <Text
        style={styles.sectionTitle}
        // === SECTION TITLE LOKÁTORY ===
        testID="available-couriers-title"
        nativeID="available-couriers-title"
        id="couriers-title"
        data-component="section-title"
        data-section="available-couriers"
        data-class="section-title heading"
        accessibilityRole="header"
        aria-level="2"
        className="section-title heading"
      >
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
        <ScrollView
          style={styles.sectionScroll}
          // === COURIERS SCROLL LOKÁTORY ===
          testID="available-couriers-scroll"
          nativeID="available-couriers-scroll"
          id="couriers-scroll"
          data-component="couriers-scroll"
          data-section="available-couriers"
          data-class="section-scroll couriers-scroll"
          accessibilityRole="none"
          aria-label="Seznam dostupných kurýrů"
          className="section-scroll couriers-scroll"
        >
          {availableCouriers.map((courier, index) => (
            <View
              key={courier.id}
              style={styles.card}
              // === COURIER CARD LOKÁTORY ===
              testID={`courier-card-${courier.id}`}
              nativeID={`courier-card-${courier.id}`}
              id={`courier-${courier.id}`}
              data-testid={`courier-card-${courier.id}`}
              data-component="courier-card"
              data-courier-id={courier.id}
              data-courier-status={courier.status}
              data-index={index}
              data-class="card courier-card"
              accessibilityRole="none"
              accessibilityLabel={`Kurýr ${courier.name}`}
              aria-label={`Kurýr ${courier.name}`}
              className="card courier-card"
            >
              {/* Header */}
              <View
                style={styles.cardHeader}
                // === COURIER HEADER LOKÁTORY ===
                testID={`courier-card-${courier.id}-header`}
                nativeID={`courier-header-${courier.id}`}
                data-component="card-header"
                data-class="card-header courier-header"
                className="card-header courier-header"
              >
                <View
                  style={styles.courierInfo}
                  // === COURIER INFO LOKÁTORY ===
                  testID={`courier-card-${courier.id}-info`}
                  nativeID={`courier-info-${courier.id}`}
                  data-component="courier-info"
                  data-class="courier-info"
                  className="courier-info"
                >
                  <MaterialIcons
                    name="person"
                    size={20}
                    color="#333"
                    // === COURIER ICON LOKÁTORY ===
                    testID={`courier-card-${courier.id}-icon`}
                    nativeID={`courier-icon-${courier.id}`}
                    data-component="icon"
                    data-icon="person"
                    accessibilityLabel="Ikona kurýra"
                  />
                  <Text
                    style={styles.courierName}
                    // === COURIER NAME LOKÁTORY ===
                    testID={`courier-card-${courier.id}-name`}
                    nativeID={`courier-name-${courier.id}`}
                    id={`courier-name-${courier.id}`}
                    data-component="courier-name"
                    data-courier-name={courier.name}
                    data-class="courier-name"
                    accessibilityRole="text"
                    className="courier-name"
                  >{courier.name}</Text>
                </View>
                <StatusBadge
                  status={courier.status}
                  statusConfig={COURIER_STATUS_CONFIG}
                  size="small"
                  testID={`courier-card-${courier.id}-status`}
                />
              </View>

              {/* Phone */}
              <View
                style={styles.phoneRow}
                // === PHONE ROW LOKÁTORY ===
                testID={`courier-card-${courier.id}-phone-row`}
                nativeID={`courier-phone-row-${courier.id}`}
                data-component="phone-row"
                data-class="phone-row contact-info"
                className="phone-row contact-info"
              >
                <MaterialIcons
                  name="phone"
                  size={14}
                  color="#666"
                  // === PHONE ICON LOKÁTORY ===
                  testID={`courier-card-${courier.id}-phone-icon`}
                  nativeID={`phone-icon-${courier.id}`}
                  data-component="icon"
                  data-icon="phone"
                  accessibilityLabel="Telefon"
                />
                <Text
                  style={styles.phoneText}
                  // === PHONE TEXT LOKÁTORY ===
                  testID={`courier-card-${courier.id}-phone`}
                  nativeID={`courier-phone-${courier.id}`}
                  id={`courier-phone-${courier.id}`}
                  data-component="phone-number"
                  data-phone={courier.phone}
                  data-class="phone-text"
                  accessibilityRole="text"
                  accessibilityLabel={`Telefon: ${courier.phone}`}
                  className="phone-text"
                >{courier.phone}</Text>
              </View>

              {/* Tags */}
              {courier.tags && courier.tags.length > 0 && (
                <View
                  style={styles.tagsRow}
                  // === COURIER TAGS LOKÁTORY ===
                  testID={`courier-card-${courier.id}-tags`}
                  nativeID={`courier-card-${courier.id}-tags`}
                  id={`courier-tags-${courier.id}`}
                  data-testid={`courier-card-${courier.id}-tags`}
                  data-component="courier-tags"
                  data-tags={courier.tags.join(',')}
                  data-class="tags-row courier-tags"
                  accessibilityRole="none"
                  accessibilityLabel="Schopnosti kurýra"
                  className="tags-row courier-tags"
                >
                  {courier.tags.map((tag, tagIndex) => (
                    <View
                      key={tag}
                      style={styles.tagChipBlue}
                      // === COURIER TAG CHIP LOKÁTORY ===
                      testID={`courier-card-${courier.id}-tag-${tag}`}
                      nativeID={`courier-tag-${courier.id}-${tag}`}
                      data-component="tag-chip"
                      data-tag={tag}
                      data-index={tagIndex}
                      data-class="tag-chip tag-blue"
                      accessibilityRole="text"
                      accessibilityLabel={TAG_LABELS[tag] || tag}
                      className="tag-chip tag-blue"
                    >
                      <MaterialIcons
                        name={TAG_ICONS[tag] || 'label'}
                        size={12}
                        color="#007AFF"
                        // === TAG ICON LOKÁTORY ===
                        testID={`courier-tag-icon-${courier.id}-${tag}`}
                        data-component="tag-icon"
                        data-icon={TAG_ICONS[tag] || 'label'}
                      />
                      <Text
                        style={[styles.tagText, { color: '#007AFF' }]}
                        // === TAG TEXT LOKÁTORY ===
                        testID={`courier-tag-text-${courier.id}-${tag}`}
                        nativeID={`courier-tag-label-${courier.id}-${tag}`}
                        data-component="tag-text"
                        data-class="tag-text tag-text-blue"
                        className="tag-text tag-text-blue"
                      >
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
      <View
        style={styles.header}
        // === HEADER SECTION LOKÁTORY ===
        testID="page4-header"
        nativeID="page4-header"
        id="page4-header"
        data-component="page-header"
        data-page="page4"
        data-section="header"
        data-class="page-header header-section"
        accessibilityRole="none"
        aria-label="Hlavička Dispatch Dashboard"
        className="page-header header-section"
      >
        <Text
          style={styles.title}
          // === PAGE TITLE LOKÁTORY ===
          testID="page4-title"
          nativeID="page4-title"
          id="page4-heading"
          data-component="page-title"
          data-page="page4"
          data-class="page-title heading main-title"
          accessibilityRole="header"
          accessibilityLabel="Dispatch Dashboard"
          aria-label="Dispatch Dashboard"
          aria-level="1"
          className="page-title heading main-title"
        >
          Dispatch Dashboard
        </Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={onRefresh}
          // === REFRESH BUTTON LOKÁTORY ===
          testID="dispatch-refresh-button"
          nativeID="dispatch-refresh-button"
          id="dispatch-refresh-btn"
          name="dispatch-refresh"
          data-testid="dispatch-refresh-button"
          data-component="refresh-button"
          data-action="refresh-dispatch"
          data-class="btn btn-icon refresh-btn"
          accessibilityLabel="Obnovit dispatch data"
          accessibilityRole="button"
          accessibilityHint="Klikněte pro obnovení dat"
          aria-label="Obnovit dispatch data"
          className="btn btn-icon refresh-btn"
        >
          <MaterialIcons
            name="refresh"
            size={24}
            color="#007AFF"
            // === REFRESH ICON LOKÁTORY ===
            testID="dispatch-refresh-icon"
            nativeID="dispatch-refresh-icon"
            data-component="icon"
            data-icon="refresh"
            accessibilityLabel="Ikona obnovení"
          />
        </TouchableOpacity>
      </View>

      {/* Stats panel */}
      <View
        style={styles.statsPanel}
        // === STATS PANEL LOKÁTORY ===
        testID="dispatch-stats-panel"
        nativeID="dispatch-stats-panel"
        id="dispatch-stats"
        data-component="stats-panel"
        data-page="page4"
        data-section="statistics"
        data-pending={pendingOrders.length}
        data-available={availableCouriers.length}
        data-class="stats-panel dispatch-stats"
        accessibilityRole="none"
        accessibilityLabel="Statistiky dispatch"
        aria-label="Statistiky dispatch"
        className="stats-panel dispatch-stats"
      >
        <View
          style={styles.statItem}
          // === STAT ITEM - PENDING LOKÁTORY ===
          testID="dispatch-stat-pending"
          nativeID="dispatch-stat-pending"
          id="stat-pending-orders"
          data-component="stat-item"
          data-stat="pending"
          data-value={pendingOrders.length}
          data-class="stat-item"
          accessibilityRole="text"
          accessibilityLabel={`Čekající: ${pendingOrders.length}`}
          aria-label={`Čekající: ${pendingOrders.length}`}
          className="stat-item"
        >
          <Text
            style={[styles.statNumber, { color: '#fd7e14' }]}
            // === PENDING COUNT LOKÁTORY ===
            testID="dispatch-pending-count"
            nativeID="dispatch-pending-value"
            data-component="stat-number"
            data-stat="pending"
            data-class="stat-number stat-warning"
            className="stat-number stat-warning"
          >
            {pendingOrders.length}
          </Text>
          <Text
            style={styles.statLabel}
            // === PENDING LABEL LOKÁTORY ===
            testID="dispatch-pending-label"
            nativeID="dispatch-pending-label"
            data-component="stat-label"
            data-class="stat-label"
            className="stat-label"
          >Cekajici</Text>
        </View>
        <View
          style={styles.statDivider}
          // === STAT DIVIDER LOKÁTORY ===
          testID="dispatch-stat-divider"
          nativeID="dispatch-stat-divider"
          data-component="stat-divider"
          data-class="stat-divider divider"
          className="stat-divider divider"
        />
        <View
          style={styles.statItem}
          // === STAT ITEM - AVAILABLE LOKÁTORY ===
          testID="dispatch-stat-available"
          nativeID="dispatch-stat-available"
          id="stat-available-couriers"
          data-component="stat-item"
          data-stat="available"
          data-value={availableCouriers.length}
          data-class="stat-item"
          accessibilityRole="text"
          accessibilityLabel={`Dostupní: ${availableCouriers.length}`}
          aria-label={`Dostupní: ${availableCouriers.length}`}
          className="stat-item"
        >
          <Text
            style={[styles.statNumber, { color: '#28a745' }]}
            // === AVAILABLE COUNT LOKÁTORY ===
            testID="dispatch-available-count"
            nativeID="dispatch-available-value"
            data-component="stat-number"
            data-stat="available"
            data-class="stat-number stat-success"
            className="stat-number stat-success"
          >
            {availableCouriers.length}
          </Text>
          <Text
            style={styles.statLabel}
            // === AVAILABLE LABEL LOKÁTORY ===
            testID="dispatch-available-label"
            nativeID="dispatch-available-label"
            data-component="stat-label"
            data-class="stat-label"
            className="stat-label"
          >Dostupni</Text>
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
        // === MAIN CONTENT SCROLL LOKÁTORY ===
        testID="dispatch-main-content"
        nativeID="dispatch-main-content"
        id="dispatch-content"
        data-component="main-content"
        data-page="page4"
        data-layout={isWideScreen ? 'wide' : 'narrow'}
        data-class="main-content dispatch-content"
        accessibilityRole="none"
        aria-label="Hlavní obsah dispatch"
        className="main-content dispatch-content"
      >
        {isWideScreen ? (
          <View
            style={styles.splitView}
            // === SPLIT VIEW LOKÁTORY ===
            testID="dispatch-split-view"
            nativeID="dispatch-split-view"
            id="split-view"
            data-component="split-view"
            data-layout="wide"
            data-class="split-view responsive-layout"
            className="split-view responsive-layout"
          >
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
