"use client";

import { useEffect, useMemo, useState, useTransition } from "react";
import { fetchCampaigns, fetchMediaList, fetchMetrics, optimizeBudget } from "@/lib/api";
import { daysAgoIso, formatCurrency, formatNumber, formatPercent, formatRoas } from "@/lib/format";
import type {
  CampaignRow,
  DailyMediaRow,
  MediaMasterRow,
  MetricTotals,
  OptimizeResponse,
} from "@/lib/types";

const MEDIA_COLORS: Record<string, string> = {
  google: "#1a7a5c",
  yahoo: "#c45c26",
  meta: "#2f6fed",
  x: "#1c1c1c",
  line: "#06c755",
  tiktok: "#111111",
};

export default function Dashboard() {
  const [startDate, setStartDate] = useState("2026-07-13");
  const [endDate, setEndDate] = useState("2026-07-13");
  const [media, setMedia] = useState("");
  const [mediaList, setMediaList] = useState<MediaMasterRow[]>([]);
  const [rows, setRows] = useState<DailyMediaRow[]>([]);
  const [campaigns, setCampaigns] = useState<CampaignRow[]>([]);
  const [totals, setTotals] = useState<MetricTotals>({});
  const [source, setSource] = useState("-");
  const [error, setError] = useState<string | null>(null);
  const [budget, setBudget] = useState(1_000_000);
  const [opt, setOpt] = useState<OptimizeResponse | null>(null);
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    fetchMediaList()
      .then(setMediaList)
      .catch(() =>
        setMediaList([
          { media_code: "google", media_name: "Google Ads", is_active: true },
          { media_code: "yahoo", media_name: "Yahoo! Ads", is_active: true },
          { media_code: "meta", media_name: "Meta Ads", is_active: true },
          { media_code: "x", media_name: "X Ads", is_active: true },
          { media_code: "line", media_name: "LINE Ads", is_active: true },
          { media_code: "tiktok", media_name: "TikTok Ads", is_active: true },
        ]),
      );
  }, []);

  const load = () => {
    startTransition(async () => {
      setError(null);
      try {
        const [metrics, camp] = await Promise.all([
          fetchMetrics({
            startDate,
            endDate,
            media: media || undefined,
          }),
          fetchCampaigns({
            startDate,
            endDate,
            media: media || undefined,
          }),
        ]);
        setRows(metrics.rows);
        setTotals(metrics.totals);
        setSource(metrics.source);
        setCampaigns(camp.rows);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load metrics");
      }
    });
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const mediaAgg = useMemo(() => {
    const map = new Map<string, number>();
    for (const row of rows) {
      map.set(row.media, (map.get(row.media) || 0) + Number(row.spend || 0));
    }
    const list = [...map.entries()].sort((a, b) => b[1] - a[1]);
    const max = list[0]?.[1] || 1;
    return list.map(([name, spend]) => ({
      name,
      spend,
      pct: (spend / max) * 100,
    }));
  }, [rows]);

  const runOptimize = () => {
    startTransition(async () => {
      setError(null);
      try {
        const result = await optimizeBudget({
          start_date: startDate,
          end_date: endDate,
          total_budget: budget,
          media: media || undefined,
        });
        setOpt(result);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Optimize failed");
      }
    });
  };

  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <p className="brand">AdInfra</p>
          <h1>広告配信実績コンソール</h1>
          <p className="lede">
            Google / Yahoo! / Meta / X / LINE / TikTok を PostgreSQL に統合し、指標と AI 配分提案を確認します。
          </p>
        </div>
        <div className="source-pill">
          Data source: <strong>{source}</strong>
        </div>
      </header>

      <section className="filters">
        <label>
          開始日
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </label>
        <label>
          終了日
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </label>
        <label>
          媒体
          <select value={media} onChange={(e) => setMedia(e.target.value)}>
            <option value="">すべて</option>
            {mediaList.map((m) => (
              <option key={m.media_code} value={m.media_code}>
                {m.media_name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="btn primary" onClick={load} disabled={pending}>
          {pending ? "更新中…" : "更新"}
        </button>
        <button
          type="button"
          className="btn ghost"
          onClick={() => {
            setStartDate(daysAgoIso(7));
            setEndDate("2026-07-13");
          }}
        >
          直近7日に設定
        </button>
      </section>

      {error ? <p className="error">{error}</p> : null}

      <section className="kpi-grid">
        <Kpi label="広告費" value={formatCurrency(totals.spend)} />
        <Kpi label="インプレッション" value={formatNumber(totals.impressions)} />
        <Kpi label="クリック" value={formatNumber(totals.clicks)} />
        <Kpi label="コンバージョン" value={formatNumber(totals.conversions, 1)} />
        <Kpi label="CTR" value={formatPercent(totals.ctr)} />
        <Kpi label="CPC" value={formatCurrency(totals.cpc)} />
        <Kpi label="CPA" value={formatCurrency(totals.cpa)} />
        <Kpi label="ROAS" value={formatRoas(totals.roas)} />
      </section>

      <div className="split">
        <section className="panel">
          <div className="panel-head">
            <h2>媒体別広告費</h2>
            <p>PostgreSQL mart / parquet の日次サマリを集計</p>
          </div>
          <ul className="bars">
            {mediaAgg.length === 0 ? (
              <li className="empty">データがありません。API と DB を起動し、パイプラインを実行してください。</li>
            ) : (
              mediaAgg.map((item) => (
                <li key={item.name}>
                  <div className="bar-meta">
                    <span>{item.name}</span>
                    <span>{formatCurrency(item.spend)}</span>
                  </div>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{
                        width: `${item.pct}%`,
                        background: MEDIA_COLORS[item.name] || "#0f766e",
                      }}
                    />
                  </div>
                </li>
              ))
            )}
          </ul>
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>AI 予算最適化</h2>
            <p>ROAS 加重で推奨配分を算出（OpenAI 連携可）</p>
          </div>
          <div className="optimize-form">
            <label>
              総予算 (JPY)
              <input
                type="number"
                min={1}
                step={10000}
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
              />
            </label>
            <button type="button" className="btn primary" onClick={runOptimize} disabled={pending}>
              提案を生成
            </button>
          </div>
          {opt ? (
            <div className="optimize-result">
              <p className="summary">{opt.summary}</p>
              <ul>
                {opt.allocations.slice(0, 8).map((a) => (
                  <li key={`${a.media}-${a.campaign_id}`}>
                    <strong>
                      {a.media} / {a.campaign_name || a.campaign_id}
                    </strong>
                    <span>
                      {formatCurrency(a.recommended_budget)} · ROAS{" "}
                      {formatRoas(a.current_roas)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>
      </div>

      <section className="panel table-panel">
        <div className="panel-head">
          <h2>キャンペーン実績</h2>
          <p>{campaigns.length} campaigns</p>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>日付</th>
                <th>媒体</th>
                <th>キャンペーン</th>
                <th>Spend</th>
                <th>Imp</th>
                <th>Click</th>
                <th>CV</th>
                <th>CTR</th>
                <th>CPA</th>
                <th>ROAS</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.slice(0, 50).map((c) => (
                <tr key={`${c.report_date}-${c.media}-${c.campaign_id}`}>
                  <td>{c.report_date}</td>
                  <td>{c.media}</td>
                  <td>{c.campaign_name || c.campaign_id}</td>
                  <td>{formatCurrency(c.spend)}</td>
                  <td>{formatNumber(c.impressions)}</td>
                  <td>{formatNumber(c.clicks)}</td>
                  <td>{formatNumber(c.conversions, 1)}</td>
                  <td>{formatPercent(c.ctr)}</td>
                  <td>{formatCurrency(c.cpa)}</td>
                  <td>{formatRoas(c.roas)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function Kpi({ label, value }: { label: string; value: string }) {
  return (
    <article className="kpi">
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}
