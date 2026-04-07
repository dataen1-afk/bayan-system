/**
 * Normalize FastAPI / Axios error payloads for user-visible messages.
 * Handles string detail, validation error arrays, and plain objects.
 */
export function formatApiErrorDetail(detail, fallback = 'Something went wrong') {
  if (detail == null || detail === '') return fallback;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    const parts = detail.map((e) => {
      if (!e || typeof e !== 'object') return JSON.stringify(e);
      const msg = e.msg != null ? String(e.msg) : '';
      const loc = Array.isArray(e.loc)
        ? e.loc.filter((x) => x !== 'body' && x != null).join('.')
        : '';
      if (loc && msg) return `${loc}: ${msg}`;
      return msg || JSON.stringify(e);
    });
    return parts.filter(Boolean).join('; ') || fallback;
  }
  if (typeof detail === 'object') return JSON.stringify(detail);
  return String(detail);
}
