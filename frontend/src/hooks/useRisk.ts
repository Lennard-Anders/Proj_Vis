/**
 * Custom hook for risk data fetching
 */
import { useState, useEffect } from 'react';
import { get } from '../api/client';
import type { RiskResponse } from '../api/types';

export function useRisk(date: string, bbox: [number, number, number, number]) {
  const [data, setData] = useState<RiskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    const fetchRisk = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const bboxStr = bbox.join(',');
        const response = await get<RiskResponse>(
          `/risk?date=${date}&bbox=${bboxStr}`
        );
        setData(response);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRisk();
  }, [date, bbox.join(',')]);
  
  return { data, loading, error };
}
