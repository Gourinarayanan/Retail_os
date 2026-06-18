import React from 'react';

// Login.tsx
// ─────────────────────────────────────────────────────────────────────────────
// NOTE: The backend has no /api/auth/login endpoint in any router.
// The app runs in single-owner demo mode (no auth).
// This page immediately redirects to the dashboard.
//
// If you want to add authentication, create:
//   backend/routers/auth.py  with POST /api/auth/login → { access_token, token_type }
// and update frontend/src/api/client.ts to read the JWT from memory.
// ─────────────────────────────────────────────────────────────────────────────

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const navigate = useNavigate();

  useEffect(() => {
    // No auth backend — go straight to dashboard
    navigate('/', { replace: true });
  }, [navigate]);

  return (
    <div className="flex h-screen items-center justify-center" style={{ background: 'var(--bg-base)' }}>
      <div className="flex items-center gap-3">
        <div className="h-5 w-5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
        <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Redirecting…</span>
      </div>
    </div>
  );
}
