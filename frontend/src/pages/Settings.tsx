import React, { useState, useEffect, useCallback } from 'react';
import { Settings2, CheckCircle2, XCircle, Save, Loader2, Info } from 'lucide-react';
import { apiGet, apiPatch } from '../api/client';
import toast from 'react-hot-toast';

// ── Exact backend response shape (from routers/settings.py SettingsOut) ───────

interface SettingsData {
  business_name:      string;
  business_location:  string;
  weather_city:       string;
  morning_brief_time: string;
  gemini_configured:  boolean;
  twilio_configured:  boolean;
  newsapi_configured: boolean;
  weather_configured: boolean;
}

// ── API status check pill ─────────────────────────────────────────────────────

function ApiStatus({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center justify-between px-4 py-3 rounded-lg"
      style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}>
      <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{label}</span>
      <div className="flex items-center gap-1.5">
        {ok
          ? <><CheckCircle2 size={13} style={{ color: '#34d399' }} /><span className="text-xs" style={{ color: '#34d399' }}>Configured</span></>
          : <><XCircle size={13} style={{ color: '#f43f5e' }} /><span className="text-xs" style={{ color: '#f43f5e' }}>Not set</span></>
        }
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function SettingsPage() {
  const [data,    setData]    = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving,  setSaving]  = useState(false);
  const [form,    setForm]    = useState<Partial<SettingsData>>({});

  // GET /api/settings
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const s = await apiGet<SettingsData>('/settings');
      setData(s);
      setForm({
        business_name:      s.business_name,
        business_location:  s.business_location,
        weather_city:       s.weather_city,
        morning_brief_time: s.morning_brief_time,
      });
    } catch { /* toast by interceptor */ } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  // PATCH /api/settings
  const save = async () => {
    setSaving(true);
    try {
      const updated = await apiPatch<SettingsData>('/settings', form);
      setData(updated);
      toast.success('Settings saved!');
    } catch { /* toast by interceptor */ } finally { setSaving(false); }
  };

  const field = (key: keyof typeof form, label: string, placeholder?: string, hint?: string) => (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-semibold" style={{ color: 'var(--text-muted)' }}>{label}</label>
      <input
        type="text"
        className="input"
        value={form[key] as string ?? ''}
        placeholder={placeholder}
        onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
      />
      {hint && <p className="text-[10px]" style={{ color: 'var(--text-muted)' }}>{hint}</p>}
    </div>
  );

  if (loading) {
    return (
      <div className="flex flex-col gap-4 max-w-xl">
        {[0,1,2,3].map(i => <div key={i} className="skeleton h-16 rounded-xl" />)}
      </div>
    );
  }

  return (
    <div className="page-enter flex flex-col gap-6 max-w-xl">
      <div>
        <h1 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Settings</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
          Runtime config · changes take effect immediately, but restart to persist across server reboots
        </p>
      </div>

      {/* ── Business info ──────────────────────────────────────────── */}
      <div className="card flex flex-col gap-4">
        <div className="flex items-center gap-2">
          <Settings2 size={14} style={{ color: '#60a5fa' }} />
          <h2 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>Business Info</h2>
        </div>
        {field('business_name',      'Business Name',   'Noofa General Stores',    'Appears in WhatsApp order messages and morning briefings')}
        {field('business_location',  'Location',        'Palakkad, Kerala',        'City / area shown in supplier messages')}
        {field('weather_city',       'Weather City',    'Palakkad',                'City name for Open-Meteo weather data')}
        {field('morning_brief_time', 'Brief Time (24h)','07:00',                   'Daily briefing cron — Asia/Kolkata timezone. Restart server to update scheduler.')}
      </div>

      {/* ── API key status ──────────────────────────────────────────── */}
      {data && (
        <div className="card flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Info size={14} style={{ color: '#60a5fa' }} />
            <h2 className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>API Key Status</h2>
          </div>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            Configure keys in <code className="mono px-1 py-0.5 rounded" style={{ background: 'var(--border)', color: '#93c5fd' }}>backend/.env</code>
          </p>
          <ApiStatus label="Gemini (LLM + embeddings)" ok={data.gemini_configured} />
          <ApiStatus label="Twilio (WhatsApp orders)"  ok={data.twilio_configured} />
          <ApiStatus label="NewsAPI (hartal detection)" ok={data.newsapi_configured} />
          <ApiStatus label="Open-Meteo (weather)"      ok={data.weather_configured} />
        </div>
      )}

      {/* ── Save button ─────────────────────────────────────────────── */}
      <button
        id="btn-save-settings"
        onClick={save}
        disabled={saving}
        className="btn-success self-start disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {saving
          ? <><Loader2 size={14} className="animate-spin" /> Saving…</>
          : <><Save size={14} /> Save Settings</>
        }
      </button>

      {/* ── .env reminder ──────────────────────────────────────────── */}
      <div className="rounded-xl px-4 py-3 flex items-start gap-2"
        style={{ background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.2)' }}>
        <Info size={13} style={{ color: '#fbbf24', flexShrink: 0, marginTop: 2 }} />
        <p className="text-xs" style={{ color: '#fde68a' }}>
          These changes are in-process only. To make them permanent, also update <code className="mono">backend/.env</code> and restart the server.
        </p>
      </div>
    </div>
  );
}
