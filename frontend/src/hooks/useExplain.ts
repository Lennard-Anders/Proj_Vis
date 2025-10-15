/**
 * Custom hook for explanation data
 */
import { useState } from 'react';
import { get } from '../api/client';
import type { ExplainResponse } from '../api/types';

export function useExplain() {
  const [data, setData] = useState<ExplainResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const fetchExplanation = async (lat: number, lon: number, date: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await get<ExplainResponse>(
        `/explain?lat=${lat}&lon=${lon}&date=${date}`
      );
      setData(response);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };
  
  return { data, loading, error, fetchExplanation };
}
