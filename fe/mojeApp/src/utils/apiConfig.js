/**
 * Centralizovana konfigurace API URL a endpointu
 * Food Delivery System - Phase 1
 */

import { Platform } from 'react-native';

/**
 * Dynamicka konfigurace API URL podle platformy
 * @returns {string} Base URL pro API
 */
export const getApiUrl = () => {
  // Pro web prohlizec (Docker backend)
  if (Platform.OS === 'web') {
    return 'http://localhost:20300';
  }
  // Pro React Native (Android emulator - Docker backend on port 20300)
  return 'http://10.0.2.2:20300';
};

/**
 * Definice API endpointu pro Food Delivery system
 */
export const API_ENDPOINTS = {
  // Orders - objednavky
  ORDERS: '/api/v1/orders/',
  ORDERS_PENDING: '/api/v1/orders/pending',
  ORDERS_BY_STATUS: (status) => `/api/v1/orders/by-status/${status}`,
  ORDER_BY_ID: (id) => `/api/v1/orders/${id}`,
  ORDER_STATUS: (id) => `/api/v1/orders/${id}/status`,
  ORDER_PICKUP: (id) => `/api/v1/orders/${id}/pickup`,
  ORDER_DELIVER: (id) => `/api/v1/orders/${id}/deliver`,
  ORDER_CANCEL: (id) => `/api/v1/orders/${id}/cancel`,

  // Couriers - kuryri
  COURIERS: '/api/v1/couriers/',
  COURIERS_AVAILABLE: '/api/v1/couriers/available',
  COURIER_BY_ID: (id) => `/api/v1/couriers/${id}`,
  COURIER_LOCATION: (id) => `/api/v1/couriers/${id}/location`,
  COURIER_STATUS: (id) => `/api/v1/couriers/${id}/status`,

  // Dispatch - prirazovani
  DISPATCH_AUTO: (orderId) => `/api/v1/dispatch/auto/${orderId}`,
  DISPATCH_MANUAL: '/api/v1/dispatch/manual',
  DISPATCH_AVAILABLE: (orderId) => `/api/v1/dispatch/available-couriers/${orderId}`,
  DISPATCH_LOGS_ORDER: (orderId) => `/api/v1/dispatch/logs/order/${orderId}`,
  DISPATCH_LOGS_COURIER: (courierId) => `/api/v1/dispatch/logs/courier/${courierId}`,

  // Form - puvodni formular (zachovano pro kompatibilitu)
  FORM: '/api/v1/form/',
  FORM_BY_ID: (id) => `/api/v1/form/${id}`,
};

/**
 * Helper pro sestaveni plne URL
 * @param {string} endpoint - Endpoint z API_ENDPOINTS
 * @returns {string} Plna URL
 */
export const buildApiUrl = (endpoint) => {
  return `${getApiUrl()}${endpoint}`;
};

export default { getApiUrl, API_ENDPOINTS, buildApiUrl };
