import React, { useState, useEffect, useCallback } from 'react';
import { Settings2, CheckCircle2, XCircle, Save, Loader2, Info, Building2, MapPin, Clock, BrainCircuit, Bell, Globe, Cloud } from 'lucide-react';
import { apiGet, apiPatch } from '../api/client';
import toast from 'react-hot-toast';

interface SettingsData {
  business_name:      string;
  business_location:  string;
  weather_city:       string;
  morning_brief_time: string;
  gemini_configured:  boolean;
  twilio_configured:  boolean;
  newsapi_configured: boolean;
  weather_configured: boolean;
  owner_whatsapp_number?: string;
  twilio_account_sid?: string;
  twilio_auth_token?: string;
}

function ApiStatus({ label, ok, icon: Icon }: { label: string; ok: boolean; icon: React.ElementType }) {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl bg-surface-container-low border border-border-glass">
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${
          ok ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600' : 'bg-surface-container border-border-glass text-on-surface-variant'
        }`}>
          <Icon className="w-4 h-4" />
        </div>
        <span className="font-semibold text-sm text-on-surface">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        {ok ? (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-600 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span className="font-label-xs text-[10px] uppercase tracking-wider font-bold">Active</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-error/10 text-error border border-error/20">
            <XCircle className="w-3.5 h-3.5" />
            <span className="font-label-xs text-[10px] uppercase tracking-wider font-bold">Missing</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const [data,    setData]    = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving,  setSaving]  = useState(false);
  const [form,    setForm]    = useState<Partial<SettingsData>>({});

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
        owner_whatsapp_number: s.owner_whatsapp_number || '',
        twilio_account_sid: s.twilio_account_sid || '',
        twilio_auth_token:  s.twilio_auth_token || '',
      });
    } catch { } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const save = async () => {
    setSaving(true);
    try {
      const updated = await apiPatch<SettingsData>('/settings', form);
      setData(updated);
      toast.success('Settings saved successfully', {
        style: { background: '#10b981', color: 'white', border: 'none', borderRadius: '12px' },
        icon: '💾',
      });
    } catch { } finally { setSaving(false); }
  };

  const field = (key: keyof typeof form, label: string, placeholder: string, hint: string, icon: React.ReactNode, type = 'text') => (
    <div className="flex flex-col gap-2">
      <label className="font-label-xs text-[10px] uppercase tracking-wider text-on-surface-variant font-bold flex items-center gap-1.5">
        {icon} {label}
      </label>
      <input
        type={type}
        className="nexus-input w-full px-4 py-3 rounded-xl text-sm"
        value={form[key] as string ?? ''}
        placeholder={placeholder}
        onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
      />
      <p className="text-[11px] text-on-surface-variant/80 ml-1">{hint}</p>
    </div>
  );

  if (loading) {
    return (
      <div className="space-y-6 max-w-2xl animate-fade-in">
        <div className="skeleton h-24 rounded-2xl" />
        <div className="skeleton h-[400px] rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl animate-fade-in pb-10">
      <div>
        <h1 className="font-headline-lg text-xl font-bold text-on-surface">System Preferences</h1>
        <p className="font-body-md text-on-surface-variant mt-1">
          Runtime configuration · Changes apply instantly to active flows
        </p>
      </div>



      <div className="glass-panel p-6 rounded-2xl border border-border-glass space-y-8">
        <div className="flex items-center gap-3 border-b border-border-glass pb-4">
          <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
            <Building2 className="w-5 h-5" />
          </div>
          <h2 className="font-headline-sm text-lg font-bold text-on-surface">Business Identity</h2>
        </div>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {field('business_name', 'Store Name', 'Noofa General Stores', 'Appears in WhatsApp msgs', <Building2 className="w-3 h-3" />)}
            {field('business_location', 'Location', 'Palakkad, Kerala', 'Regional context for agents', <MapPin className="w-3 h-3" />)}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {field('weather_city', 'Weather Target', 'Palakkad', 'City for Open-Meteo forecasts', <Cloud className="w-3 h-3" />)}
            {field('morning_brief_time', 'Brief Schedule (24h)', '07:00', 'Cron schedule (Requires restart)', <Clock className="w-3 h-3" />)}
          </div>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-border-glass space-y-8 mt-6">
        <div className="flex flex-col gap-1 border-b border-border-glass pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600">
              <Bell className="w-5 h-5" />
            </div>
            <h2 className="font-headline-sm text-lg font-bold text-on-surface">WhatsApp & Twilio</h2>
          </div>
          <p className="text-xs text-on-surface-variant ml-14">
            Twilio Sandbox requires orders to be sent <strong>from their official number</strong>. You can configure your own number below to <strong>receive</strong> the Morning Briefs.
          </p>
        </div>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {field('owner_whatsapp_number', 'Owner WhatsApp Number', 'whatsapp:+919876543210', 'Number to receive morning briefs (Format: whatsapp:+YOUR_NUMBER)', <Bell className="w-3 h-3" />)}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {field('twilio_account_sid', 'Twilio Account SID', 'AC123...', 'Find this in your Twilio Sandbox console', <Cloud className="w-3 h-3" />, 'password')}
            {field('twilio_auth_token', 'Twilio Auth Token', '••••••••', 'Find this in your Twilio Sandbox console', <Cloud className="w-3 h-3" />, 'password')}
          </div>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-border-glass space-y-6">
        <div className="flex items-center gap-3 border-b border-border-glass pb-4">
          <div className="w-10 h-10 rounded-xl bg-surface-container-high border border-border-glass flex items-center justify-center text-on-surface">
            <Settings2 className="w-5 h-5" />
          </div>
          <h2 className="font-headline-sm text-lg font-bold text-on-surface">Integration Status</h2>
        </div>

        {data && (
          <div className="space-y-3">
            <ApiStatus label="Google Gemini API" ok={data.gemini_configured} icon={BrainCircuit} />
            <ApiStatus label="Twilio Messaging" ok={data.twilio_configured} icon={Bell} />
            <ApiStatus label="NewsAPI Service" ok={data.newsapi_configured} icon={Globe} />
            <ApiStatus label="Open-Meteo Data" ok={data.weather_configured} icon={Cloud} />
          </div>
        )}
      </div>

      <button
        onClick={save}
        disabled={saving}
        className="w-full sm:w-auto px-8 py-3 rounded-xl bg-primary hover:bg-primary-fixed text-on-primary font-bold text-sm tracking-wide uppercase transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
        {saving ? 'Applying...' : 'Save Preferences'}
      </button>
    </div>
  );
}
