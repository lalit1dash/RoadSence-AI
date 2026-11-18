import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../config/api';

/**
 * useFetch - fetch data on mount and optionally on refetch()
 * @param {string} url - API endpoint
 * @param {object} options - axios config overrides
 */
export function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const optionsRef = useRef(options);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(url, optionsRef.current);
      setData(response.data);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    if (url) {
      fetchData();
    }
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

/**
 * usePost - returns a mutate function to POST data
 */
export function usePost() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const mutate = useCallback(async (url, payload, config = {}) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const response = await api.post(url, payload, config);
      setData(response.data);
      return response.data;
    } catch (err) {
      const message = err?.response?.data?.detail || err.message || 'Request failed';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { mutate, loading, error, data };
}
