/**
 * Single source for backend URL resolution (Vercel + CRA).
 * Avoids `undefined/api/...` when REACT_APP_BACKEND_URL is missing.
 * Empty origin → `/api` for local CRA proxy.
 */
export const BACKEND_ORIGIN = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/+$/, '');

export const API = BACKEND_ORIGIN ? `${BACKEND_ORIGIN}/api` : '/api';
