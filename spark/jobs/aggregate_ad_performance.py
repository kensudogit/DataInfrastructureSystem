"""
Spark job: aggregate landing JSONL into curated parquet.

Usage:
  spark-submit spark/jobs/aggregate_ad_performance.py --date 2026-07-13 --landing ./data/landing --curated ./data/curated
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--landing", default="./data/landing")
    parser.add_argument("--curated", default="./data/curated")
    args = parser.parse_args()

    try:
        from pyspark.sql import SparkSession
        from pyspark.sql import functions as F
    except ImportError as exc:
        raise SystemExit(
            "pyspark is not installed. pip install pyspark or use Pandas pipeline instead."
        ) from exc

    spark = (
        SparkSession.builder.appName("ad-infra-aggregate")
        .master("local[*]")
        .getOrCreate()
    )

    landing = Path(args.landing)
    paths = [str(p) for p in landing.glob(f"*/{args.date}/performance.jsonl")]
    if not paths:
        raise SystemExit(f"No landing files for {args.date}")

    df = spark.read.json(paths)
    daily = (
        df.groupBy("report_date", "media")
        .agg(
            F.sum("impressions").alias("impressions"),
            F.sum("clicks").alias("clicks"),
            F.sum("conversions").alias("conversions"),
            F.sum("spend").alias("spend"),
            F.sum("conversion_value").alias("conversion_value"),
        )
        .withColumn("ctr", F.col("clicks") / F.col("impressions"))
        .withColumn("cpc", F.col("spend") / F.col("clicks"))
        .withColumn("cpm", F.col("spend") / F.col("impressions") * F.lit(1000))
        .withColumn("cpa", F.col("spend") / F.col("conversions"))
        .withColumn("roas", F.col("conversion_value") / F.col("spend"))
    )

    out = Path(args.curated) / args.date / "spark_daily_media_summary"
    out.parent.mkdir(parents=True, exist_ok=True)
    daily.write.mode("overwrite").parquet(str(out))
    print(f"wrote {out}")
    spark.stop()


if __name__ == "__main__":
    main()
