/**
 * Custom hook for counterfactual analysis
 */
import { useState } from 'react';
import { post } from '../api/client';
import type { CounterfactualRequest, CounterfactualResponse } from '../api/types';

export function useCounterfactual() {
  const [data, setData] = useState<CounterfactualResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const runCounterfactual = async (request: CounterfactualRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await post<CounterfactualResponse>(
        '/risk/counterfactual',
        request
      );
      setData(response);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };
  
  return { data, loading, error, runCounterfactual };
}
