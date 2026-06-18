// ── Core DB-matching types ────────────────────────────────────────────────────

export type AlertLevel = 'out_of_stock' | 'critical' | 'warning' | 'excess' | 'ok';
export type Urgency    = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
export type OrderStatus = 'pending_approval' | 'approved' | 'sent_whatsapp' | 'rejected';
export type OrderCycle  = 'daily' | 'weekly' | 'monthly' | 'emergency';
export type BatchStatus = 'active' | 'expiring_soon' | 'depleted' | 'expired';

// ── Product ───────────────────────────────────────────────────────────────────

export interface Product {
  product_id:           number;
  name:                 string;
  sku:                  string;
  category:             string;
  brand:                string | null;
  unit:                 string;
  unit_size:            number;
  selling_price:        number;
  cost_price:           number;
  order_cycle:          OrderCycle;
  order_day:            string | null;
  reorder_point_days:   number;
  lead_time_days:       number;
  shelf_life_days:      number;
  min_threshold:        number;
  demand_events:        string;
  avg_daily_demand:     number;
}

// ── Inventory ─────────────────────────────────────────────────────────────────

export interface ExpiryAlert {
  batch_number:   string;
  days_to_expiry: number;
  quantity:       number;
  severity:       'expired' | 'critical_expiry' | 'expiring_soon';
}

export interface InventoryBatch {
  id:                number;
  batch_number:      string;
  quantity:          number;
  unit:              string;
  purchase_price:    number;
  manufactured_date: string | null;
  expiry_date:       string | null;
  days_to_expiry:    number | null;
  status:            BatchStatus;
  created_at:        string;
}

export interface InventoryItem {
  product_id:          number;
  name:                string;
  sku:                 string;
  category:            string;
  brand:               string | null;
  unit:                string;
  selling_price:       number;
  cost_price:          number;
  avg_daily_demand:    number;
  min_threshold:       number;
  reorder_point_days:  number;
  lead_time_days:      number;
  order_cycle:         OrderCycle;
  order_day:           string | null;
  current_stock:       number;
  days_remaining:      number;
  stock_status:        AlertLevel;
  expiry_alerts:       ExpiryAlert[];
  batches:             InventoryBatch[];
}

// ── Supplier ──────────────────────────────────────────────────────────────────

export interface SupplierRanking {
  supplier_id:           number;
  name:                  string;
  contact_name:          string;
  whatsapp_number:       string;
  region:                string;
  price_per_unit:        number;
  on_time_rate_pct:      number;
  avg_rating:            number;
  total_deliveries_90d:  number;
  region_risk:           boolean;
  price_score:           number;
  reliability_score:     number;
  regional_score:        number;
  composite_score:       number;
  saving_vs_costliest:   number;
  notes:                 string;
}

export interface Supplier {
  id:                    number;
  name:                  string;
  contact_name:          string;
  whatsapp_number:       string;
  email:                 string;
  region:                string;
  supply_categories:     string[];
  notes:                 string;
  is_active:             boolean;
  on_time_rate_pct:      number;
  avg_rating:            number;
  total_deliveries_90d:  number;
  delivery_history?:     DeliveryRecord[];
  prices?:               SupplierPrice[];
}

export interface DeliveryRecord {
  id:                     number;
  product_id:             number;
  order_date:             string;
  expected_delivery_date: string;
  actual_delivery_date:   string | null;
  on_time:                boolean;
  quantity_ordered:       number;
  quantity_received:      number;
  complaint:              string | null;
  rating:                 number | null;
}

export interface SupplierPrice {
  product_id:          number;
  price_per_unit:      number;
  min_order_qty:       number | null;
  bulk_discount_qty:   number | null;
  bulk_discount_price: number | null;
  recorded_date:       string;
}

// ── Orders ────────────────────────────────────────────────────────────────────

export interface Order {
  id:                   number;
  product_id:           number;
  product_name:         string;
  product_sku:          string;
  category:             string;
  supplier_id:          number;
  supplier_name:        string;
  supplier_contact:     string;
  supplier_whatsapp:    string;
  order_cycle:          OrderCycle;
  ai_recommended_qty:   number;
  final_qty:            number;
  owner_modified:       boolean;
  owner_note:           string | null;
  unit:                 string;
  price_per_unit:       number;
  total_cost:           number;
  status:               OrderStatus;
  ai_reasoning:         string;
  whatsapp_message:     string;
  created_at:           string;
  approved_at:          string | null;
}

// ── Forecast ──────────────────────────────────────────────────────────────────

export interface ForecastDay {
  date:     string;
  baseline: number;
  adjusted: number;
  lower:    number;
  upper:    number;
}

export interface ForecastResult {
  product_id:               number;
  sku:                      string;
  name:                     string;
  recharts_data:            ForecastDay[];
  baseline_daily:           number;
  scenario_adjusted_daily:  number;
  multiplier:               number;
  reasons:                  string[];
  data_source:              string;
}

// ── Briefing / Context ────────────────────────────────────────────────────────

export interface WeatherDay {
  condition:  string;
  temp_max:   number;
  rain_mm:    number;
  rain_heavy: boolean;
}

export interface FestivalEntry {
  festival:      string;
  date:          string;
  days_away:     number;
  duration_days: number;
}

export interface DailyContext {
  weather: {
    today:    WeatherDay;
    tomorrow: WeatherDay;
  };
  hartal_today:       boolean;
  hartal_tomorrow:    boolean;
  hartal_day_after:   boolean;
  hartal_days_away:   number | null;
  hartal_source:      string | null;
  transport_strike:   boolean;
  supply_disruption:  boolean;
  upcoming_festivals: FestivalEntry[];
  sources:            string[];
}

export interface ActiveScenario {
  id:              string;
  name:            string;
  urgency:         Urgency;
  action:          string;
  supply_warning:  string | null;
  category_impacts: Record<string, { multiplier: number; reason: string }>;
}

export interface Briefing {
  id:               number;
  date:             string;
  brief_text:       string;
  context:          DailyContext;
  scenarios:        ActiveScenario[];
  inventory_alerts: InventoryItem[];
  orders:           Order[];
  opportunities:    Opportunity[];
  created_at:       string;
}

// ── Opportunities ─────────────────────────────────────────────────────────────

export interface Opportunity {
  festival:           string;
  days_away:          number;
  duration_days:      number;
  product_id:         number;
  product_sku:        string;
  product_name:       string;
  category:           string;
  demand_uplift_pct:  number;
  extra_units:        number;
  extra_revenue_est:  number;
  extra_profit_est:   number;
  narrative:          string;
  action:             string;
  multiplier:         number;
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export interface SalesTrendPoint {
  date:         string;
  dairy?:       number;
  staples?:     number;
  snacks?:      number;
  beverages?:   number;
  spices?:      number;
  cleaning?:    number;
  personal_care?: number;
  [key: string]: string | number | undefined;
}

export interface TopProduct {
  product_id:     number;
  name:           string;
  sku:            string;
  category:       string;
  total_revenue:  number;
  total_qty_sold: number;
}

export interface SupplierPerformance {
  supplier_id:       number;
  name:              string;
  region:            string;
  total_deliveries:  number;
  on_time_count:     number;
  on_time_rate_pct:  number;
  avg_rating:        number;
  categories:        string[];
}

export interface InventoryHealthItem {
  product_id:    number;
  name:          string;
  sku:           string;
  category:      string;
  current_stock: number;
  days_remaining:number;
  status:        AlertLevel;
  min_threshold: number;
}

// ── Agent / SSE ───────────────────────────────────────────────────────────────

export type AgentName =
  | 'ceo' | 'context' | 'scenario' | 'forecast'
  | 'inventory' | 'supplier' | 'opportunity' | 'briefing';

export type AgentStatus = 'started' | 'complete' | 'error';

export interface AgentLogEntry {
  agent:   AgentName;
  status:  AgentStatus;
  summary: string;
  ts:      number;
}

export interface SSECompleteEvent {
  run_id:              string;
  brief_preview:       string;
  orders_count:        number;
  opportunities_count: number;
  sources:             string[];
}

// ── Chat ──────────────────────────────────────────────────────────────────────

export type ChatRole = 'user' | 'assistant';

export interface ChatMessage {
  id:           number;
  role:         ChatRole;
  content:      string;
  context_used: string | null;
  created_at:   string;
}

// ── API response wrappers ─────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
}

export interface ProfitInsightsResponse {
  opportunities: Opportunity[];
  count:         number;
}

export interface AgentStatusResponse {
  agent_log:  AgentLogEntry[];
  run_id?:    string;
  date?:      string;
  message?:   string;
}
