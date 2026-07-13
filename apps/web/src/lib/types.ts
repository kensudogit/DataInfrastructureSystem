export type MediaCode =
  | "google"
  | "yahoo"
  | "meta"
  | "x"
  | "line"
  | "tiktok"
  | string;

export interface MetricTotals {
  impressions?: number;
  clicks?: number;
  conversions?: number;
  spend?: number;
  conversion_value?: number;
  ctr?: number | null;
  cpc?: number | null;
  cpm?: number | null;
  cpa?: number | null;
  roas?: number | null;
}

export interface DailyMediaRow {
  report_date: string;
  media: MediaCode;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  conversion_value: number;
  ctr?: number | null;
  cpc?: number | null;
  cpm?: number | null;
  cpa?: number | null;
  roas?: number | null;
}

export interface CampaignRow {
  report_date: string;
  media: MediaCode;
  account_id: string;
  campaign_id: string;
  campaign_name?: string | null;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  conversion_value: number;
  ctr?: number | null;
  cpc?: number | null;
  cpm?: number | null;
  cpa?: number | null;
  roas?: number | null;
}

export interface MetricsResponse {
  start_date: string;
  end_date: string;
  source: string;
  rows: DailyMediaRow[];
  totals: MetricTotals;
}

export interface CampaignsResponse {
  start_date: string;
  end_date: string;
  source: string;
  rows: CampaignRow[];
}

export interface MediaMasterRow {
  media_code: string;
  media_name: string;
  is_active: boolean;
}

export interface OptimizeAllocation {
  media: string;
  campaign_id?: string | null;
  campaign_name?: string | null;
  current_spend: number;
  current_roas: number;
  recommended_budget: number;
  rationale: string;
}

export interface OptimizeResponse {
  start_date: string;
  end_date: string;
  total_budget: number;
  provider: string;
  summary: string;
  allocations: OptimizeAllocation[];
  llm_commentary?: string;
  data_source?: string;
}
