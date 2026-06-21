import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle, IndianRupee, PackageCheck, ShoppingCart,
  CircleAlert, TrendingUp, DollarSign, Truck, Activity,
} from 'lucide-react';
import { apiGet } from '../api/client';
import type { Briefing, Order } from '../types';
import AgentFlowVisualiser from '../components/dashboard/AgentFlowVisualiser';
import ContextCards from '../components/dashboard/ContextCards';
import MorningBriefCard from '../components/dashboard/MorningBriefCard';

export default function DashboardPage() {
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [liveOrders, setLiveOrders] = useState<Order[]>([]);
  const [liveAlerts, setLiveAlerts] = useState<any[]>([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);

  const fetchBriefing = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [bData, oData, aData] = await Promise.all([
        apiGet<Briefing>('/briefing/today').catch(err => {
          if (err?.response?.status === 404) return null;
          throw err;
        }),
        apiGet<Order[]>('/orders/pending').catch(() => []),
        apiGet<any[]>('/inventory/alerts').catch(() => [])
      ]);
      setBriefing(bData);
      setLiveOrders(oData);
      setLiveAlerts(aData);
    } catch (err: any) {
      setError('Could not load today workspace. Check that the backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchBriefing(); }, [fetchBriefing]);

  const handlePipelineComplete = useCallback(() => {
    window.setTimeout(fetchBriefing, 500);
  }, [fetchBriefing]);

  const metrics = useMemo(() => {
    const alerts = liveAlerts;
    const orders = liveOrders;
    const opps   = briefing?.opportunities ?? [];
    const critical   = alerts.filter(i => i.stock_status === 'critical' || i.stock_status === 'out_of_stock').length;
    const pending    = orders.filter(o => o.status === 'pending_approval').length;
    const orderValue = orders.reduce((s, o) => s + (o.total_cost || 0), 0);
    const profit     = opps.reduce((s, op) => s + (op.extra_profit_est || 0), 0);
    return { critical, pending, orderValue, profit };
  }, [briefing, liveAlerts, liveOrders]);

  const stats = [
    {
      id: 'stat-critical',
      label: 'Critical Alerts',
      value: loading ? '—' : `${metrics.critical} Items`,
      change: 'Items at or below safety limit',
      isPositive: false,
      icon: CircleAlert,
      colorClass: 'text-error',
      glowBg: 'rgba(239,68,68,0.1)',
    },
    {
      id: 'stat-orders',
      label: 'Pending Orders',
      value: loading ? '—' : `${metrics.pending} Orders`,
      change: 'AI-generated restock drafts',
      isPositive: true,
      icon: ShoppingCart,
      colorClass: 'text-secondary',
      glowBg: 'rgba(14,165,233,0.1)',
    },
    {
      id: 'stat-value',
      label: 'Order Value',
      value: loading ? '—' : `₹${Math.round(metrics.orderValue).toLocaleString('en-IN')}`,
      change: 'Pending capital required',
      isPositive: true,
      icon: IndianRupee,
      colorClass: 'text-primary',
      glowBg: 'rgba(79,70,229,0.1)',
    },
    {
      id: 'stat-profit',
      label: 'Profit Upside',
      value: loading ? '—' : `₹${Math.round(metrics.profit).toLocaleString('en-IN')}`,
      change: 'Festival & scenario opportunities',
      isPositive: true,
      icon: TrendingUp,
      colorClass: 'text-tertiary-fixed-dim',
      glowBg: 'rgba(249,115,22,0.1)',
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h3 className="font-headline-lg text-on-surface">Operations Overview</h3>
        <p className="font-body-md text-on-surface-variant max-w-2xl mt-1">
          AI morning briefing, agent pipeline, inventory signals, and context all in one workspace.
        </p>
      </div>

      {/* Error state */}
      {error && !loading && (
        <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm font-semibold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" /> {error}
        </div>
      )}

      {/* Morning Brief Banner */}
      <MorningBriefCard briefing={briefing} liveAlerts={liveAlerts} liveOrders={liveOrders} loading={loading} onRefresh={fetchBriefing} />

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map(stat => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.id}
              className="glass-panel rounded-xl p-6 transition-all duration-300 relative overflow-hidden group hover:translate-y-[-2px] hover:shadow-lg"
            >
              <div
                className="absolute -right-4 -bottom-4 w-28 h-28 rounded-full blur-3xl pointer-events-none transition-all duration-500 group-hover:scale-125"
                style={{ backgroundColor: stat.glowBg }}
              />
              <div className="flex items-start justify-between relative z-10">
                <div className="space-y-3">
                  <span className="font-label-xs text-on-surface-variant uppercase tracking-wider block">
                    {stat.label}
                  </span>
                  <span className="font-headline-lg font-bold block text-on-surface">
                    {stat.value}
                  </span>
                </div>
                <div className="w-10 h-10 rounded-lg bg-surface-container-low border border-border-glass flex items-center justify-center shadow-sm select-none">
                  <Icon className={`w-5 h-5 ${stat.colorClass}`} />
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-border-glass/40 flex items-center justify-between text-xs relative z-10">
                <span className="text-on-surface-variant/80 font-body-md">{stat.change}</span>
                <Activity className="w-3.5 h-3.5 text-primary opacity-30 group-hover:opacity-100 transition-opacity" />
              </div>
            </div>
          );
        })}
      </div>

      {/* Agent Pipeline */}
      <AgentFlowVisualiser onComplete={handlePipelineComplete} />

      {/* Context Cards */}
      <ContextCards
        context={briefing?.context ?? null}
        scenarios={briefing?.scenarios ?? []}
        loading={loading}
      />
    </div>
  );
}
