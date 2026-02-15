/**
 * Loki Logger for Frontend Error Logging
 * Sends frontend errors, warnings, and info to Loki for centralized monitoring
 */

// Configuration - dynamically set Loki URL based on platform
const getLokiUrl = () => {
  // For web (browser)
  if (typeof window !== 'undefined' && window.location) {
    return 'http://localhost:20300/api/v1/logs/frontend';
  }
  // For React Native (Android emulator)
  return 'http://10.0.2.2:20300/api/v1/logs/frontend';
};

const LOKI_URL = getLokiUrl();
const SERVICE_NAME = 'moje-app-frontend';
const ENVIRONMENT = typeof process !== 'undefined' && process.env ? process.env.NODE_ENV : 'development';

// Batch configuration to reduce API calls
let logBatch = [];
let batchTimeout = null;
const BATCH_SIZE = 10; // Send after 10 logs
const BATCH_INTERVAL = 5000; // Or after 5 seconds

// Retry queue for failed logs
let failedLogsQueue = [];
const MAX_FAILED_QUEUE_SIZE = 100; // Limit memory usage

/**
 * Format log entry for Loki API
 */
function formatLogEntry(level, message, context = {}) {
  return {
    stream: {
      service: SERVICE_NAME,
      environment: ENVIRONMENT,
      level: level,
      // Add additional labels for filtering
      platform: typeof window !== 'undefined' ? 'web' : 'react-native',
    },
    values: [
      [
        (Date.now() * 1000000).toString(), // Nanoseconds since epoch
        JSON.stringify({
          message: message,
          ...context,
          timestamp: new Date().toISOString(),
          userAgent: typeof window !== 'undefined' ? window.navigator.userAgent : 'unknown',
          url: typeof window !== 'undefined' ? window.location.href : 'unknown',
        })
      ]
    ]
  };
}

/**
 * Send logs to Loki with retry logic
 */
async function sendToLoki(logs) {
  if (!logs || logs.length === 0) return;

  try {
    const response = await fetch(LOKI_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ streams: logs }),
    });

    if (!response.ok) {
      // Re-queue all logs for next attempt
      queueFailedLogs(logs);
      console.error(`[Loki] Failed to send logs (will retry): ${response.statusText}`);
      return;
    }

    // Success - log how many were sent
    const retryCount = logs.filter(l => l.isRetry).length;
    console.log(`[Loki] Sent ${logs.length} logs successfully${retryCount > 0 ? ` (${retryCount} from retry queue)` : ''}`);
  } catch (error) {
    // Re-queue all logs for next attempt
    queueFailedLogs(logs);
    console.error('[Loki] Error sending logs (will retry):', error.message);
  }
}

/**
 * Add failed logs to retry queue with size limit
 */
function queueFailedLogs(logs) {
  const spaceAvailable = MAX_FAILED_QUEUE_SIZE - failedLogsQueue.length;
  if (spaceAvailable <= 0) {
    console.warn('[Loki] Retry queue full, dropping failed logs');
    return;
  }

  // Mark as retry and add to queue (drop oldest if necessary)
  const logsToQueue = logs.slice(0, spaceAvailable).map(log => ({
    ...log,
    isRetry: true,
  }));

  if (logs.length > spaceAvailable) {
    console.warn(`[Loki] Dropped ${logs.length - spaceAvailable} failed logs (queue full)`);
  }

  failedLogsQueue.push(...logsToQueue);
}

/**
 * Flush log batch to Loki (includes retry queue)
 */
function flushBatch() {
  if (logBatch.length > 0 || failedLogsQueue.length > 0) {
    // Combine failed logs + new logs
    const logsToSend = [...failedLogsQueue, ...logBatch];
    logBatch = [];
    failedLogsQueue = []; // Clear queue after combining
    sendToLoki(logsToSend);
  }
  if (batchTimeout) {
    clearTimeout(batchTimeout);
    batchTimeout = null;
  }
}

/**
 * Add log to batch and trigger send if needed
 */
function addToBatch(logEntry) {
  logBatch.push(logEntry);

  // Send immediately if batch is full
  if (logBatch.length >= BATCH_SIZE) {
    flushBatch();
    return;
  }

  // Set timeout to send after interval
  if (!batchTimeout) {
    batchTimeout = setTimeout(flushBatch, BATCH_INTERVAL);
  }
}

/**
 * Logger interface
 */
const logger = {
  /**
   * Log error message
   * @param {string} message - Error message
   * @param {object} context - Additional context (error object, stack trace, etc.)
   */
  error: (message, context = {}) => {
    // Always log to console for immediate visibility
    console.error(message, context);

    // Send to Loki
    const entry = formatLogEntry('error', message, context);
    addToBatch(entry);
  },

  /**
   * Log warning message
   * @param {string} message - Warning message
   * @param {object} context - Additional context
   */
  warning: (message, context = {}) => {
    console.warn(message, context);
    const entry = formatLogEntry('warning', message, context);
    addToBatch(entry);
  },

  /**
   * Log info message
   * @param {string} message - Info message
   * @param {object} context - Additional context
   */
  info: (message, context = {}) => {
    console.log(message, context);
    const entry = formatLogEntry('info', message, context);
    addToBatch(entry);
  },

  /**
   * Manually flush pending logs
   * Call this before page unload to ensure logs are sent
   */
  flush: flushBatch,
};

/**
 * Setup global error handlers to catch unhandled errors
 */
function setupGlobalErrorHandlers() {
  // React Native uses ErrorUtils, browser uses window.addEventListener
  const isReactNative = typeof window !== 'undefined' && !window.document;

  if (isReactNative) {
    // React Native error handling
    if (typeof ErrorUtils !== 'undefined') {
      ErrorUtils.setGlobalHandler((error, isFatal) => {
        logger.error(isFatal ? 'Fatal JavaScript error' : 'Unhandled JavaScript error', {
          message: error.message,
          stack: error.stack,
          isFatal,
        });
      });
    }
    return;
  }

  // Browser environment
  if (typeof window === 'undefined') return;

  // Catch unhandled JavaScript errors
  window.addEventListener('error', (event) => {
    logger.error('Unhandled JavaScript error', {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      stack: event.error?.stack,
    });
  });

  // Catch unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    logger.error('Unhandled promise rejection', {
      reason: event.reason,
      promise: String(event.promise),
      stack: event.reason?.stack,
    });
  });

  // Flush logs before page unload
  window.addEventListener('beforeunload', () => {
    logger.flush();

    // Use sendBeacon as fallback for immediate send
    if (logBatch.length > 0) {
      const blob = new Blob([JSON.stringify({ streams: logBatch })], {
        type: 'application/json',
      });
      if (navigator.sendBeacon) {
        navigator.sendBeacon(LOKI_URL, blob);
      }
    }
  });
}

// Initialize error handlers
setupGlobalErrorHandlers();

export default logger;
