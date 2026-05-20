import json, html
from pathlib import Path

def main():
    data=json.loads(Path("results/runtime_report_v1_1.json").read_text(encoding="utf-8"))
    s=data["summary"]
    rows="\n".join(f"<tr><td><code>{html.escape(r['command'])}</code></td><td>{r['expected_decision']}</td><td>{r['decision']}</td><td>{r['command_type']}</td><td>{r['decision_pass'] and r['type_pass']}</td></tr>" for r in data["results"])
    page=(f"<!doctype html><html><head><meta charset='utf-8'><title>I2OS-CTG v1.1 Dashboard</title>"
          f"<style>body{{font-family:system-ui;margin:32px}}.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}}"
          f".card{{padding:16px;border:1px solid #ddd;border-radius:14px;box-shadow:0 2px 8px #0001}}"
          f"table{{border-collapse:collapse;width:100%;margin-top:24px}}td,th{{border-bottom:1px solid #eee;padding:8px;text-align:left}}code{{white-space:nowrap}}</style>"
          f"</head><body><h1>I2OS-CTG Runtime Shield v1.1</h1><p>Test Expansion Edition / dry-run transition governance prototype.</p>"
          f"<div class='cards'><div class='card'><b>Total</b><br>{s['total_tests']}</div><div class='card'><b>Runtime Pass</b><br>{s['runtime_pass_rate']}%</div>"
          f"<div class='card'><b>Type Pass</b><br>{s['type_pass_rate']}%</div><div class='card'><b>False GO</b><br>{s['false_go']}</div>"
          f"<div class='card'><b>False BLOCK</b><br>{s['false_block']}</div></div><h2>Runtime Tests</h2>"
          f"<table><tr><th>Command</th><th>Expected</th><th>Actual</th><th>Type</th><th>Pass</th></tr>{rows}</table></body></html>")
    Path("results/ctg_dashboard_v1_1.html").write_text(page,encoding="utf-8")
    print("generated results/ctg_dashboard_v1_1.html")
if __name__ == "__main__": main()
