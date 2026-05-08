"""DataPulse | core/reporter.py — Self-contained HTML report with inline SVG charts."""
import datetime, json
from pathlib import Path

BAR_COLORS = ["#3b82f6","#8b5cf6","#ec4899","#10b981","#f59e0b","#ef4444","#06b6d4","#84cc16"]

def _bar_chart(labels, values, title, color="#3b82f6", max_bars=10):
    if not values: return ""
    labels, values = labels[:max_bars], values[:max_bars]
    max_v  = max(values) if values else 1
    W, H   = 480, 220
    pad_l, pad_b, pad_t, pad_r = 60, 40, 30, 20
    chart_w = W - pad_l - pad_r
    chart_h = H - pad_b - pad_t
    bw      = max(8, chart_w // len(labels) - 6)
    bars    = ""
    for i,(lbl,val) in enumerate(zip(labels,values)):
        bh  = int(val/max_v*chart_h) if max_v else 0
        x   = pad_l + i*(chart_w//len(labels)) + (chart_w//len(labels)-bw)//2
        y   = pad_t + chart_h - bh
        sl  = str(lbl)[:10]
        bars += (f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{color}" rx="3"/>'
                 f'<text x="{x+bw//2}" y="{y-4}" text-anchor="middle" font-size="9" fill="#6b7280">{val}</text>'
                 f'<text x="{x+bw//2}" y="{H-8}" text-anchor="middle" font-size="8" fill="#6b7280">{sl}</text>')
    # Y-axis
    for step in range(0,5):
        yv = int(max_v*step/4); yr = pad_t+chart_h - int(chart_h*step/4)
        bars += f'<line x1="{pad_l-4}" y1="{yr}" x2="{W-pad_r}" y2="{yr}" stroke="#f1f5f9" stroke-width="1"/>'
        bars += f'<text x="{pad_l-6}" y="{yr+3}" text-anchor="end" font-size="8" fill="#9ca3af">{yv}</text>'
    return f'<div style="background:#f8fafc;border-radius:10px;padding:12px;margin-bottom:12px"><div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px">{title}</div><svg width="{W}" height="{H}" style="max-width:100%">{bars}</svg></div>'

def _pie_chart(labels, values, title):
    if not values or sum(values)==0: return ""
    labels, values = labels[:6], values[:6]
    total = sum(values)
    cx,cy,r = 90,90,70; W,H=300,180
    paths=""; legend=""; angle=0
    for i,(lbl,val) in enumerate(zip(labels,values)):
        pct=val/total; sweep=pct*2*3.14159
        x1=cx+r*__import__('math').cos(angle); y1=cy+r*__import__('math').sin(angle)
        angle+=sweep
        x2=cx+r*__import__('math').cos(angle); y2=cy+r*__import__('math').sin(angle)
        lg=1 if pct>0.5 else 0
        col=BAR_COLORS[i%len(BAR_COLORS)]
        paths+=f'<path d="M{cx},{cy} L{x1:.1f},{y1:.1f} A{r},{r} 0 {lg},1 {x2:.1f},{y2:.1f} Z" fill="{col}" stroke="#fff" stroke-width="1.5"/>'
        legend+=f'<div style="display:flex;align-items:center;gap:5px;margin-bottom:3px;font-size:11px;color:#374151"><div style="width:10px;height:10px;border-radius:2px;background:{col};flex-shrink:0"></div>{str(lbl)[:16]} <span style="color:#6b7280;margin-left:auto">{round(pct*100)}%</span></div>'
    return (f'<div style="background:#f8fafc;border-radius:10px;padding:12px;margin-bottom:12px">'
            f'<div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px">{title}</div>'
            f'<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">'
            f'<svg width="{W//2}" height="{H}" viewBox="0 0 {W//2} {H}">{paths}</svg>'
            f'<div style="flex:1;min-width:120px">{legend}</div></div></div>')

def generate_report(profile, output_path: str) -> str:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    charts_html = ""
    stats_html  = ""

    for i, cs in enumerate(profile.columns):
        col_color = BAR_COLORS[i % len(BAR_COLORS)]
        if cs.col_type == "numeric":
            stats_html += f"""
            <div style="border:1px solid #e5e7eb;border-radius:10px;padding:1rem;background:#fff">
              <div style="font-size:12px;font-weight:700;color:#1e293b;margin-bottom:8px">
                <span style="background:#dbeafe;color:#1d4ed8;padding:2px 7px;border-radius:4px;font-size:10px;margin-right:6px">NUMERIC</span>{cs.name}
              </div>
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;font-size:12px">
                <div style="background:#f8fafc;border-radius:6px;padding:6px 8px"><div style="color:#6b7280;font-size:10px">Mean</div><div style="font-weight:700;color:#111">{cs.mean}</div></div>
                <div style="background:#f8fafc;border-radius:6px;padding:6px 8px"><div style="color:#6b7280;font-size:10px">Median</div><div style="font-weight:700;color:#111">{cs.median}</div></div>
                <div style="background:#f8fafc;border-radius:6px;padding:6px 8px"><div style="color:#6b7280;font-size:10px">Std Dev</div><div style="font-weight:700;color:#111">{cs.std}</div></div>
                <div style="background:#f8fafc;border-radius:6px;padding:6px 8px"><div style="color:#6b7280;font-size:10px">Min</div><div style="font-weight:700;color:#111">{cs.min_val}</div></div>
                <div style="background:#f8fafc;border-radius:6px;padding:6px 8px"><div style="color:#6b7280;font-size:10px">Max</div><div style="font-weight:700;color:#111">{cs.max_val}</div></div>
                <div style="background:#f8fafc;border-radius:6px;padding:6px 8px"><div style="color:#6b7280;font-size:10px">Nulls</div><div style="font-weight:700;color:{'#dc2626' if cs.nulls>0 else '#16a34a'}">{cs.nulls}</div></div>
              </div>
            </div>"""
        else:
            lbl=[v[0] for v in cs.top_values]; vals=[v[1] for v in cs.top_values]
            charts_html += _pie_chart(lbl, vals, f"Top values — {cs.name}") if len(lbl)<=6 else _bar_chart(lbl,vals,f"Top values — {cs.name}", col_color)
            stats_html += f"""
            <div style="border:1px solid #e5e7eb;border-radius:10px;padding:1rem;background:#fff">
              <div style="font-size:12px;font-weight:700;color:#1e293b;margin-bottom:8px">
                <span style="background:#f3e8ff;color:#7c3aed;padding:2px 7px;border-radius:4px;font-size:10px;margin-right:6px">CATEGORICAL</span>{cs.name}
              </div>
              <div style="font-size:12px;color:#374151">
                Unique values: <strong>{cs.unique}</strong> &nbsp;|&nbsp; Total: <strong>{cs.count}</strong> &nbsp;|&nbsp; Nulls: <strong style="color:{'#dc2626' if cs.nulls>0 else '#16a34a'}">{cs.nulls}</strong>
              </div>
              <div style="margin-top:8px">
                {"".join(f'<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #f1f5f9;font-size:12px"><span style="color:#374151">{v[0]}</span><span style="color:#6b7280">{v[1]}</span></div>' for v in cs.top_values[:5])}
              </div>
            </div>"""

    insights_html = "".join(f'<div style="padding:6px 10px;background:#eff6ff;border-left:3px solid #3b82f6;border-radius:0 6px 6px 0;margin-bottom:6px;font-size:13px;color:#1e40af">💡 {i}</div>' for i in profile.insights)
    warnings_html = "".join(f'<div style="padding:6px 10px;background:#fff7ed;border-left:3px solid #ea580c;border-radius:0 6px 6px 0;margin-bottom:6px;font-size:13px;color:#9a3412">⚠️ {w}</div>' for w in profile.warnings)

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<title>DataPulse — {profile.filename}</title>
<style>
  body{{font-family:'Segoe UI',system-ui,sans-serif;background:#f3f4f6;margin:0;padding:2rem;color:#111827}}
  .wrap{{max-width:1020px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08)}}
  .hd{{background:linear-gradient(135deg,#0f172a,#1e3a5f);color:#fff;padding:2rem 2.5rem}}
  .meta{{background:#f8fafc;padding:1.25rem 2.5rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1rem;border-bottom:1px solid #e5e7eb}}
  .mc{{text-align:center}}.ml{{font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:1px;margin-bottom:3px}}.mv{{font-size:1.1rem;font-weight:700}}
  .sec{{padding:1.5rem 2.5rem}}.sec+.sec{{border-top:1px solid #f1f5f9}}
  h2{{font-size:14px;font-weight:700;color:#1e293b;text-transform:uppercase;letter-spacing:.5px;padding-bottom:6px;border-bottom:2px solid #e5e7eb;margin-bottom:1rem}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}}
  footer{{text-align:center;padding:1rem;font-size:12px;color:#9ca3af;border-top:1px solid #f1f5f9}}
</style></head><body>
<div class="wrap">
  <div class="hd">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem">
      <div style="width:42px;height:42px;background:#3b82f6;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:22px">📊</div>
      <div><div style="font-size:1.4rem;font-weight:800">DataPulse</div>
           <div style="font-size:11px;color:#94a3b8;letter-spacing:2px;text-transform:uppercase">Automated Data Analyzer</div></div>
    </div>
    <div style="font-family:monospace;font-size:13px;color:#93c5fd">{profile.filename}</div>
  </div>

  <div class="meta">
    <div class="mc"><div class="ml">Rows</div><div class="mv">{profile.rows:,}</div></div>
    <div class="mc"><div class="ml">Columns</div><div class="mv">{profile.cols}</div></div>
    <div class="mc"><div class="ml">Numeric Cols</div><div class="mv">{sum(1 for c in profile.columns if c.col_type=='numeric')}</div></div>
    <div class="mc"><div class="ml">Categorical</div><div class="mv">{sum(1 for c in profile.columns if c.col_type=='categorical')}</div></div>
    <div class="mc"><div class="ml">Insights</div><div class="mv" style="color:#2563eb">{len(profile.insights)}</div></div>
    <div class="mc"><div class="ml">Warnings</div><div class="mv" style="color:{'#dc2626' if profile.warnings else '#16a34a'}">{len(profile.warnings)}</div></div>
    <div class="mc"><div class="ml">Scanned</div><div class="mv" style="font-size:.78rem">{ts}</div></div>
  </div>

  {'<div class="sec"><h2>Insights</h2>' + insights_html + '</div>' if profile.insights else ''}
  {'<div class="sec"><h2>Warnings</h2>' + warnings_html + '</div>' if profile.warnings else ''}
  {'<div class="sec"><h2>Charts</h2>' + charts_html + '</div>' if charts_html else ''}

  <div class="sec">
    <h2>Column Statistics</h2>
    <div class="grid">{stats_html}</div>
  </div>

  <footer>DataPulse v1.0 &nbsp;|&nbsp; Built by <strong>Daksh Shah</strong> &nbsp;|&nbsp; github.com/daksh-shah9135/datapulse</footer>
</div></body></html>"""

    Path(output_path).write_text(html, encoding="utf-8")
    return output_path
