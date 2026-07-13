"""AI-assisted budget / bid optimization suggestions."""
from __future__ import annotations

from typing import Any

import pandas as pd

from packages.common.config import Settings, get_settings


def _heuristic_optimize(df: pd.DataFrame, total_budget: float) -> dict[str, Any]:
    if df.empty:
        return {
            "provider": "mock",
            "summary": "No performance data available for optimization.",
            "allocations": [],
        }

    work = df.copy()
    work["roas"] = work["roas"].fillna(0)
    work["spend"] = work["spend"].fillna(0)
    positive = work[work["roas"] > 0]
    if positive.empty:
        positive = work

    weights = positive["roas"].clip(lower=0.01)
    weight_sum = float(weights.sum())
    allocations = []
    for _, row in positive.iterrows():
        share = float(row["roas"]) / weight_sum if weight_sum else 1 / len(positive)
        allocations.append(
            {
                "media": row["media"],
                "campaign_id": row.get("campaign_id"),
                "campaign_name": row.get("campaign_name"),
                "current_spend": float(row.get("spend") or 0),
                "current_roas": float(row.get("roas") or 0),
                "recommended_budget": round(total_budget * share, 2),
                "rationale": "Higher historical ROAS receives larger budget share.",
            }
        )

    allocations.sort(key=lambda x: x["recommended_budget"], reverse=True)
    return {
        "provider": "heuristic",
        "summary": (
            f"Allocated JPY {total_budget:,.0f} across {len(allocations)} campaigns "
            "weighted by ROAS."
        ),
        "allocations": allocations,
    }


def _llm_optimize(df: pd.DataFrame, total_budget: float, settings: Settings) -> dict[str, Any]:
    heuristic = _heuristic_optimize(df, total_budget)
    if settings.ai_provider == "mock" or not settings.openai_api_key:
        heuristic["provider"] = "mock"
        return heuristic

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
    except Exception:
        return heuristic

    sample = df.head(30).to_dict(orient="records")
    llm = ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o-mini", temperature=0.2)
    messages = [
        SystemMessage(
            content=(
                "You are an advertising performance optimizer. "
                "Given campaign KPIs, propose budget reallocation within the total budget. "
                "Respond in concise Japanese."
            )
        ),
        HumanMessage(
            content=(
                f"Total budget: {total_budget}\n"
                f"Campaign sample: {sample}\n"
                f"Heuristic baseline: {heuristic['allocations'][:10]}"
            )
        ),
    ]
    response = llm.invoke(messages)
    heuristic["provider"] = settings.ai_provider
    heuristic["llm_commentary"] = getattr(response, "content", str(response))
    return heuristic


def optimize_budget(
    campaign_df: pd.DataFrame,
    total_budget: float,
    settings: Settings | None = None,
) -> dict[str, Any]:
    cfg = settings or get_settings()
    if cfg.ai_provider in {"openai", "azure_openai"} and (
        cfg.openai_api_key or cfg.azure_openai_api_key
    ):
        return _llm_optimize(campaign_df, total_budget, cfg)
    return _heuristic_optimize(campaign_df, total_budget)
