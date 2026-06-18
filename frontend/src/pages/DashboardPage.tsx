import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertTriangle, IndianRupee, PackageCheck, ShoppingCart, Sparkles } from 'lucide-react';
import { apiGet } from '../api/client';
import type { Briefing } from '../types';
import AgentFlowVisualiser from '../components/dashboard/AgentFlowVisualiser';
import ContextCards from '../components/dashboard/ContextCards';
import MorningBriefCard from '../components/dashboard/MorningBriefCard';

function MetricTile({
  label,
  value,
  tone,
  icon,
}: {
  label: string;
  value: string | number;
  tone: 'green' | 'amber' | 'red' | 'blue';
  icon: React.ReactNode;
}) {
  const color = {
    green: 'var(--accent-emerald)',
    amber: 'var(--accent-amber)',
    red: 'var(--accent-rose)',
    blue: 'var(--accent-blue)',
  }[tone];

  return (
    <div className="metric-tile">
      <div className="metric-icon" style={{ color }}>
        {icon}
      </div>
      <div>
        <p>{label}</p>
        <strong style={{ color }}>{value}</strong>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBriefing = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiGet<Briefing>('/briefing/today');
      setBriefing(data);
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setBriefing(null);
      } else {
        setError('Could not load today workspace. Check that the backend is running.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBriefing();
  }, [fetchBriefing]);

  const handlePipelineComplete = useCallback(() => {
    window.setTimeout(fetchBriefing, 500);
  }, [fetchBriefing]);

  const metrics = useMemo(() => {
    const alerts = briefing?.inventory_alerts ?? [];
    const orders = briefing?.orders ?? [];
    const opportunities = briefing?.opportunities ?? [];
    const critical = alerts.filter((item) => item.stock_status === 'critical' || item.stock_status === 'out_of_stock').length;
    const pending = orders.filter((order) => order.status === 'pending_approval').length;
    const orderValue = orders.reduce((sum, order) => sum + (order.total_cost || 0), 0);
    const profit = opportunities.reduce((sum, opp) => sum + (opp.extra_profit_est || 0), 0);

    return { critical, pending, orderValue, profit };
  }, [briefing]);

  return (
    <div className="page-enter flex flex-col gap-6">
      <section className="dashboard-hero">
        <div className="hero-copy">
          <span className="hero-kicker">
            <Sparkles size={14} />
            Retail operations cockpit
          </span>
          <h2>Know what to stock, order, and watch today.</h2>
          <p>
            Built for a small store owner: context signals, AI order reasoning, supplier actions,
            and forecast-backed decisions in one workspace.
          </p>
        </div>

        <div className="hero-metrics">
          <MetricTile label="Critical alerts" value={loading ? '--' : metrics.critical} tone={metrics.critical > 0 ? 'red' : 'green'} icon={<AlertTriangle size={18} />} />
          <MetricTile label="Pending orders" value={loading ? '--' : metrics.pending} tone="amber" icon={<ShoppingCart size={18} />} />
          <MetricTile label="Order value" value={loading ? '--' : `Rs ${Math.round(metrics.orderValue).toLocaleString('en-IN')}`} tone="green" icon={<PackageCheck size={18} />} />
          <MetricTile label="Profit upside" value={loading ? '--' : `Rs ${Math.round(metrics.profit).toLocaleString('en-IN')}`} tone="blue" icon={<IndianRupee size={18} />} />
        </div>
      </section>

      {error && !loading && (
        <div className="rounded-lg px-4 py-3 text-sm font-semibold" style={{ background: '#fff1f2', border: '1px solid #fecdd3', color: 'var(--accent-rose)' }}>
          {error}
        </div>
      )}

      <div className="dashboard-grid">
        <div className="dashboard-main">
          <AgentFlowVisualiser onComplete={handlePipelineComplete} />
          <MorningBriefCard briefing={briefing} loading={loading} onRefresh={fetchBriefing} />
        </div>

        <aside className="dashboard-side">
          <ContextCards context={briefing?.context ?? null} scenarios={briefing?.scenarios ?? []} loading={loading} />
        </aside>
      </div>
    </div>
  );
}
