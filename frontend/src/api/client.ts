/**
 * API client with fetch helpers, retry, and abort support
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

export interface FetchOptions extends RequestInit {
  retries?: number;
  timeout?: number;
}

/**
 * Fetch with retry logic and timeout
 */
export async function fetchJSON<T>(
  url: string,
  options: FetchOptions = {}
): Promise<T> {
  const { retries = 3, timeout = 30000, ...fetchOptions } = options;
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        ...fetchOptions,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new APIError(
          response.status,
          `API error: ${response.status} ${response.statusText}`
        );
      }
      
      return await response.json();
    } catch (error) {
      lastError = error as Error;
      
      // Don't retry on abort or 4xx errors
      if (
        error instanceof DOMException && error.name === 'AbortError' ||
        error instanceof APIError && error.status >= 400 && error.status < 500
      ) {
        break;
      }
      
      // Wait before retry (exponential backoff)
      if (attempt < retries - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt)));
      }
    }
  }
  
  clearTimeout(timeoutId);
  throw lastError || new Error('Unknown error');
}

/**
 * GET request helper
 */
export function get<T>(url: string, options?: FetchOptions): Promise<T> {
  return fetchJSON<T>(url, { ...options, method: 'GET' });
}

/**
 * POST request helper
 */
export function post<T>(
  url: string,
  body: any,
  options?: FetchOptions
): Promise<T> {
  return fetchJSON<T>(url, {
    ...options,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    body: JSON.stringify(body),
  });
}
