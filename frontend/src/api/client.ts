import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

// ── Base client ───────────────────────────────────────────────────────────────

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 60_000,   // 60s — Holt-Winters pipeline can be slow on first run
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// ── Request interceptor: JWT ──────────────────────────────────────────────────

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('rw_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ── Response interceptor: error handling ──────────────────────────────────────

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<{ detail: string | { msg: string }[] }>) => {
    if (!error.response) {
      // Network error — backend unreachable
      toast.error('Cannot reach RetailWise server. Is the backend running?', { id: 'net-error' });
      return Promise.reject(error);
    }

    const { status, data } = error.response;

    // 401 — clear token and reload to show login
    if (status === 401) {
      localStorage.removeItem('rw_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // 404 — caller handles (do NOT toast 404s globally)
    if (status === 404) {
      return Promise.reject(error);
    }

    // 422 — validation: extract message from FastAPI format
    if (status === 422) {
      let msg = 'Validation error.';
      if (Array.isArray(data?.detail)) {
        msg = data.detail.map((e) => (typeof e === 'object' ? e.msg : e)).join(', ');
      } else if (typeof data?.detail === 'string') {
        msg = data.detail;
      }
      toast.error(msg, { id: `422-${msg.slice(0, 20)}` });
      return Promise.reject(error);
    }

    // 503 — AI service unavailable
    if (status === 503) {
      toast.error('AI service temporarily unavailable. Please try again.', { id: '503' });
      return Promise.reject(error);
    }

    // Everything else (500, etc.)
    const detail = typeof data?.detail === 'string' ? data.detail : 'An unexpected error occurred.';
    toast.error(detail, { id: `err-${status}` });
    return Promise.reject(error);
  },
);

// ── Typed API helpers ─────────────────────────────────────────────────────────

export const apiGet  = <T>(url: string, params?: object) =>
  api.get<T>(url, { params }).then((r) => r.data);

export const apiPost = <T>(url: string, body?: unknown) =>
  api.post<T>(url, body).then((r) => r.data);

export const apiPatch = <T>(url: string, body?: unknown) =>
  api.patch<T>(url, body).then((r) => r.data);

export const apiDelete = <T>(url: string) =>
  api.delete<T>(url).then((r) => r.data);

// ── SSE helper — wraps the browser EventSource for the briefing stream ─────────
/**
 * Opens a POST-based SSE connection to /api/run-briefing.
 * Uses fetch + ReadableStream (browser native) because EventSource only supports GET.
 *
 * onEntry   — called for each `agent_update` event
 * onComplete — called when the `complete` event fires
 * onError    — called on stream failure
 */
export async function streamBriefing(
  onEntry:    (entry: object) => void,
  onComplete: (summary: object) => void,
  onError:    (err: Error) => void,
): Promise<void> {
  const baseUrl = import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000';
  const token = localStorage.getItem('rw_token');

  try {
    const response = await fetch(`${baseUrl}/api/run-briefing`, {
      method: 'POST',
      headers: {
        Accept: 'text/event-stream',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP ${response.status} — pipeline failed to start.`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split(/\r?\n\r?\n/);
      buffer = parts.pop() ?? '';

      for (const chunk of parts) {
        const lines = chunk.split(/\r?\n/);
        let eventType = 'agent_update';
        let dataLine  = '';

        for (const line of lines) {
          if (line.startsWith('event:')) eventType = line.slice(6).trim();
          if (line.startsWith('data:'))  dataLine  = line.slice(5).trim();
        }

        if (!dataLine) continue;
        try {
          const parsed = JSON.parse(dataLine);
          if (eventType === 'complete') {
            onComplete(parsed);
          } else {
            onEntry(parsed);
          }
        } catch {
          // skip malformed chunks
        }
      }
    }
  } catch (err) {
    onError(err instanceof Error ? err : new Error(String(err)));
  }
}

export default api;
