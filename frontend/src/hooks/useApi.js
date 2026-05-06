import { useState, useCallback } from 'react';

/**
 * Generic hook for async API calls.
 * Returns { data, loading, error, execute }.
 * Call execute(fn) with any async function — it handles loading/error state.
 */
export default function useApi() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const execute = useCallback(async (apiFn) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFn();
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
  }, []);

  return { data, loading, error, execute, reset };
}
