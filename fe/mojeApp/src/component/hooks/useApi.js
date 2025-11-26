/**
 * Custom hook pro API volani s loading/error state management
 * Food Delivery System - Phase 1
 */

import { useState, useCallback } from 'react';
import { buildApiUrl } from '../../utils/apiConfig';

/**
 * Custom hook pro API volani
 *
 * @example
 * const { get, post, loading, error } = useApi();
 * const data = await get('/api/v1/orders/');
 *
 * @returns {object} { get, post, put, del, patch, loading, error, clearError }
 */
const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Zakladni fetch wrapper
   * @param {string} endpoint - API endpoint
   * @param {object} options - fetch options
   * @returns {Promise<any>} Response data
   */
  const request = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const url = endpoint.startsWith('http')
        ? endpoint
        : buildApiUrl(endpoint);

      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      // Zkus parsovat JSON, pokud neni prazdna odpoved
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(data?.detail || `HTTP error ${response.status}`);
      }

      return data;
    } catch (err) {
      const errorMessage = err.message || 'Nastala neocekavana chyba';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * GET request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<any>} Response data
   */
  const get = useCallback(
    async (endpoint) => {
      return request(endpoint, { method: 'GET' });
    },
    [request]
  );

  /**
   * POST request
   * @param {string} endpoint - API endpoint
   * @param {object} body - Request body
   * @returns {Promise<any>} Response data
   */
  const post = useCallback(
    async (endpoint, body) => {
      return request(endpoint, {
        method: 'POST',
        body: JSON.stringify(body),
      });
    },
    [request]
  );

  /**
   * PUT request
   * @param {string} endpoint - API endpoint
   * @param {object} body - Request body
   * @returns {Promise<any>} Response data
   */
  const put = useCallback(
    async (endpoint, body) => {
      return request(endpoint, {
        method: 'PUT',
        body: JSON.stringify(body),
      });
    },
    [request]
  );

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint
   * @returns {Promise<any>} Response data
   */
  const del = useCallback(
    async (endpoint) => {
      return request(endpoint, { method: 'DELETE' });
    },
    [request]
  );

  /**
   * PATCH request
   * @param {string} endpoint - API endpoint
   * @param {object} body - Request body
   * @returns {Promise<any>} Response data
   */
  const patch = useCallback(
    async (endpoint, body) => {
      return request(endpoint, {
        method: 'PATCH',
        body: JSON.stringify(body),
      });
    },
    [request]
  );

  /**
   * Reset error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    get,
    post,
    put,
    del,
    patch,
    loading,
    error,
    clearError,
  };
};

export default useApi;
