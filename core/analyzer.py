"""DataPulse | core/analyzer.py — Statistical analysis engine."""
import csv, json, math
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ColumnStats:
    name:       str
    col_type:   str          # numeric | categorical | date | mixed
    count:      int
    nulls:      int
    unique:     int
    # numeric
    mean:       Optional[float] = None
    median:     Optional[float] = None
    std:        Optional[float] = None
    min_val:    Optional[float] = None
    max_val:    Optional[float] = None
    # categorical
    top_values: list = field(default_factory=list)   # [(val, count), ...]

@dataclass
class DatasetProfile:
    filename:    str
    rows:        int
    cols:        int
    columns:     list[ColumnStats] = field(default_factory=list)
    insights:    list[str]         = field(default_factory=list)
    warnings:    list[str]         = field(default_factory=list)

def _try_float(v):
    try:    return float(str(v).replace(",","").strip())
    except: return None

def _mean(vals):   return sum(vals)/len(vals) if vals else 0
def _std(vals):
    if len(vals)<2: return 0
    m=_mean(vals); return math.sqrt(sum((x-m)**2 for x in vals)/len(vals))
def _median(vals):
    s=sorted(vals); n=len(s)
    return (s[n//2-1]+s[n//2])/2 if n%2==0 else s[n//2]

def analyze_csv(filepath: str) -> DatasetProfile:
    with open(filepath, encoding="utf-8", errors="replace") as f:
        reader  = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows    = list(reader)

    profile = DatasetProfile(filename=filepath, rows=len(rows), cols=len(headers))

    for col in headers:
        raw_vals   = [r.get(col,"") for r in rows]
        non_null   = [v for v in raw_vals if v.strip()]
        nulls      = len(raw_vals) - len(non_null)
        unique     = len(set(non_null))
        numeric    = [_try_float(v) for v in non_null]
        numeric    = [x for x in numeric if x is not None]

        if len(numeric) >= len(non_null) * 0.7:
            col_type = "numeric"
            cs = ColumnStats(name=col, col_type=col_type,
                count=len(non_null), nulls=nulls, unique=unique,
                mean=round(_mean(numeric),2), median=round(_median(numeric),2),
                std=round(_std(numeric),2),
                min_val=round(min(numeric),2), max_val=round(max(numeric),2))
        else:
            col_type = "categorical"
            top = Counter(non_null).most_common(8)
            cs = ColumnStats(name=col, col_type=col_type,
                count=len(non_null), nulls=nulls, unique=unique,
                top_values=top)
        profile.columns.append(cs)

    # Auto insights
    for cs in profile.columns:
        if cs.col_type=="numeric":
            if cs.std and cs.mean and cs.std > cs.mean * 0.5:
                profile.insights.append(f"'{cs.name}' has high variance (std={cs.std}) — data is widely spread.")
            if cs.max_val and cs.min_val is not None and cs.max_val > (cs.min_val + cs.std*3 if cs.std else cs.min_val):
                profile.insights.append(f"'{cs.name}' may contain outliers (max={cs.max_val}, mean={cs.mean}).")
        if cs.nulls > 0:
            pct = round(cs.nulls/profile.rows*100,1)
            if pct > 10:
                profile.warnings.append(f"'{cs.name}' has {pct}% missing values ({cs.nulls} rows).")
        if cs.col_type=="categorical" and cs.top_values:
            top_val, top_cnt = cs.top_values[0]
            pct = round(top_cnt/profile.rows*100,1)
            if pct > 60:
                profile.insights.append(f"'{cs.name}' is dominated by '{top_val}' ({pct}% of rows).")

    if not profile.insights:
        profile.insights.append("Dataset looks clean with no major anomalies detected.")

    return profile
