/**
 * Konstanty pro Food Delivery System
 * Statusy, barvy, tagy, urgency logika
 */

/**
 * Order status enum - mapuje backend OrderStatus
 */
export const ORDER_STATUSES = {
  CREATED: 'CREATED',
  SEARCHING: 'SEARCHING',
  ASSIGNED: 'ASSIGNED',
  PICKED: 'PICKED',
  DELIVERED: 'DELIVERED',
  CANCELLED: 'CANCELLED',
};

/**
 * Konfigurace pro zobrazeni statusu objednavky
 * Pouziva se v StatusBadge komponente
 */
export const ORDER_STATUS_CONFIG = {
  [ORDER_STATUSES.CREATED]: {
    label: 'Vytvoreno',
    color: '#6c757d',
    backgroundColor: '#f8f9fa',
  },
  [ORDER_STATUSES.SEARCHING]: {
    label: 'Hleda kuryra',
    color: '#fd7e14',
    backgroundColor: '#fff3e0',
  },
  [ORDER_STATUSES.ASSIGNED]: {
    label: 'Prirazeno',
    color: '#007bff',
    backgroundColor: '#e3f2fd',
  },
  [ORDER_STATUSES.PICKED]: {
    label: 'Vyzvednuto',
    color: '#17a2b8',
    backgroundColor: '#e0f7fa',
  },
  [ORDER_STATUSES.DELIVERED]: {
    label: 'Doruceno',
    color: '#28a745',
    backgroundColor: '#e8f5e9',
  },
  [ORDER_STATUSES.CANCELLED]: {
    label: 'Zruseno',
    color: '#dc3545',
    backgroundColor: '#ffebee',
  },
};

/**
 * Order priority enum
 */
export const ORDER_PRIORITIES = {
  normal: 'normal',
  high: 'high',
};

/**
 * Courier status enum - mapuje backend CourierStatus
 */
export const COURIER_STATUSES = {
  available: 'available',
  busy: 'busy',
  offline: 'offline',
};

/**
 * Konfigurace pro zobrazeni statusu kuryra
 */
export const COURIER_STATUS_CONFIG = {
  [COURIER_STATUSES.available]: {
    label: 'Dostupny',
    color: '#28a745',
    backgroundColor: '#e8f5e9',
  },
  [COURIER_STATUSES.busy]: {
    label: 'Zaneprazdnen',
    color: '#fd7e14',
    backgroundColor: '#fff3e0',
  },
  [COURIER_STATUSES.offline]: {
    label: 'Offline',
    color: '#6c757d',
    backgroundColor: '#f8f9fa',
  },
};

/**
 * Courier tagy/schopnosti
 */
export const AVAILABLE_TAGS = ['bike', 'car', 'vip', 'fragile_ok', 'fast'];

/**
 * Popisky pro tagy kuryra (cesky)
 */
export const TAG_LABELS = {
  bike: 'Kolo',
  car: 'Auto',
  vip: 'VIP',
  fragile_ok: 'Krehke',
  fast: 'Rychly',
};

/**
 * Ikony pro tagy (MaterialIcons)
 */
export const TAG_ICONS = {
  bike: 'directions-bike',
  car: 'directions-car',
  vip: 'star',
  fragile_ok: 'local-shipping',
  fast: 'bolt',
};

/**
 * Urgency thresholds (v minutach od vytvoreni)
 */
export const URGENCY_THRESHOLDS = {
  LOW: 5,
  MEDIUM: 15,
  HIGH: 15,
};

/**
 * Vypocet urgency barvy podle casu od vytvoreni
 * @param {string|Date} createdAt - Cas vytvoreni objednavky
 * @returns {object} { color, backgroundColor, label }
 */
export const getUrgencyColor = (createdAt) => {
  const now = new Date();
  const created = new Date(createdAt);
  const diffMinutes = Math.floor((now - created) / (1000 * 60));

  if (diffMinutes < URGENCY_THRESHOLDS.LOW) {
    return {
      color: '#28a745',
      backgroundColor: '#e8f5e9',
      label: 'Nizka',
    };
  } else if (diffMinutes < URGENCY_THRESHOLDS.MEDIUM) {
    return {
      color: '#fd7e14',
      backgroundColor: '#fff3e0',
      label: 'Stredni',
    };
  } else {
    return {
      color: '#dc3545',
      backgroundColor: '#ffebee',
      label: 'Vysoka',
    };
  }
};

/**
 * Formatovani urgency labelu s casem
 * @param {string|Date} createdAt - Cas vytvoreni objednavky
 * @returns {string} Napr. "15 min - Vysoka"
 */
export const getUrgencyLabel = (createdAt) => {
  const now = new Date();
  const created = new Date(createdAt);
  const diffMinutes = Math.floor((now - created) / (1000 * 60));
  const urgency = getUrgencyColor(createdAt);

  return `${diffMinutes} min - ${urgency.label}`;
};

export default {
  ORDER_STATUSES,
  ORDER_STATUS_CONFIG,
  ORDER_PRIORITIES,
  COURIER_STATUSES,
  COURIER_STATUS_CONFIG,
  AVAILABLE_TAGS,
  TAG_LABELS,
  TAG_ICONS,
  URGENCY_THRESHOLDS,
  getUrgencyColor,
  getUrgencyLabel,
};
