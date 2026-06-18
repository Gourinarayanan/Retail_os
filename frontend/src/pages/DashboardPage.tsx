import React, { useState, useEffect, useCallback } from 'react';
import { apiGet } from '../api/client';
import type { Briefing } from '../types';
import AgentFlowVisualiser from '../components/dashboard/AgentFlowVisualiser';
import ContextCards from '../components/dashboard/ContextCards';
import MorningBriefCard from '../components/dashboard/MorningBriefCard';

export default function DashboardPage() {
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState<string | null>(null);

  // ── Fetch today's briefing ─────────────────────────────────────────────
  const fetchBriefing = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<Briefing>('/briefing/today');
      setBriefing(data);
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setBriefing(null);  // No briefing yet today — not an error
      } else {
        setError('Failed to load briefing. Is the backend running?');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchBriefing(); }, [fetchBriefing]);

  // When pipeline completes, re-fetch the briefing
  const handlePipelineComplete = useCallback(() => {
    setTimeout(fetchBriefing, 500); // small delay so DB write completes
  }, [fetchBriefing]);

  return (
    <div className="page-enter flex flex-col gap-6 max-w-[1400px]">

      {/* ── Agent Pipeline visualiser ─────────────────────────────── */}
      <AgentFlowVisualiser onComplete={handlePipelineComplete} />

      {/* ── Error banner ─────────────────────────────────────────── */}
      {error && !loading && (
        <div
          className="rounded-xl px-4 py-3 text-sm"
          style={{ background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.25)', color: '#fda4af' }}
        >
          {error}
        </div>
      )}

      {/* ── Context cards: Weather / Hartal / Festival ────────────── */}
      <ContextCards
        context={briefing?.context ?? null}
        scenarios={briefing?.scenarios ?? []}
        loading={loading}
      />

      {/* ── Morning brief card ────────────────────────────────────── */}
      <MorningBriefCard
        briefing={briefing}
        loading={loading}
        onRefresh={fetchBriefing}
      />
    </div>
  );
}
