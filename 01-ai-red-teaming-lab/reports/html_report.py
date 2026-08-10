# reports/html_report.py
import os
import json
from datetime import datetime
from collections import defaultdict
from scoring.evaluator import Evaluator


class HTMLReportGenerator:

    def __init__(self, all_results: list, retest_results: list):
        self.all_results    = all_results
        self.retest_results = retest_results
        self.evaluator      = Evaluator(all_results)
        self.summary        = self.evaluator.summary()
        self.timestamp      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ts_file        = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate(self, output_path: str = "results/") -> str:
        os.makedirs(output_path, exist_ok=True)
        filename = f"{output_path}report_{self.ts_file}.html"
        s    = self.summary
        cats = s["by_category"]
        labels    = list(cats.keys())
        succeeded = [cats[c]["succeeded"] for c in labels]
        blocked   = [cats[c]["blocked"]   for c in labels]
        hits      = [r for r in self.all_results if r["success"]]

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>AI Red Team Report</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    body{{font-family:'Segoe UI',sans-serif;background:#0d1117;color:#c9d1d9;margin:0;padding:0}}
    header{{background:#161b22;border-bottom:2px solid #f85149;padding:2rem 3rem}}
    header h1{{color:#f85149;margin:0}}
    main{{max-width:1200px;margin:0 auto;padding:2rem 3rem}}
    h2{{color:#58a6ff;border-left:4px solid #58a6ff;padding-left:.75rem}}
    .cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}}
    .card{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1.5rem;text-align:center}}
    .card .value{{font-size:2.5rem;font-weight:700}}
    .card .label{{font-size:.8rem;color:#8b949e;text-transform:uppercase}}
    .blue{{color:#58a6ff}}.red{{color:#f85149}}.green{{color:#3fb950}}.yellow{{color:#d29922}}
    .charts{{display:grid;grid-template-columns:1fr 2fr;gap:1.5rem;margin-bottom:2rem}}
    .chart-box{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem}}
    table{{width:100%;border-collapse:collapse;font-size:.85rem}}
    th{{background:#21262d;color:#8b949e;padding:.75rem 1rem;text-align:left;font-size:.75rem;text-transform:uppercase}}
    td{{padding:.75rem 1rem;border-bottom:1px solid #21262d;vertical-align:top}}
    .badge{{display:inline-block;padding:.2rem .6rem;border-radius:20px;font-size:.75rem;font-weight:600}}
    .b-red{{background:#f851491a;color:#f85149}}
    .b-green{{background:#3fb9501a;color:#3fb950}}
    .b-yellow{{background:#d299221a;color:#d29922}}
    .b-blue{{background:#58a6ff1a;color:#58a6ff}}
    footer{{text-align:center;padding:2rem;color:#8b949e;font-size:.8rem;border-top:1px solid #21262d}}
  </style>
</head>
<body>
<header>
  <h1>🔴 AI Red Team Assessment Report</h1>
  <p style="color:#8b949e">Target: AcmeCorp Chatbot · {self.timestamp}</p>
</header>
<main>

<h2>Executive Summary</h2>
<div class="cards">
  <div class="card"><div class="value blue">{s["total_attacks"]}</div><div class="label">Total Attacks</div></div>
  <div class="card"><div class="value red">{s["succeeded"]}</div><div class="label">Succeeded</div></div>
  <div class="card"><div class="value green">{s["blocked"]}</div><div class="label">Blocked</div></div>
  <div class="card"><div class="value yellow">{s["success_rate"]}</div><div class="label">Success Rate</div></div>
</div>

<h2>Attack Analysis</h2>
<div class="charts">
  <div class="chart-box"><h3 style="color:#8b949e;font-size:.9rem">Result Distribution</h3><canvas id="pie"></canvas></div>
  <div class="chart-box"><h3 style="color:#8b949e;font-size:.9rem">By Category</h3><canvas id="bar"></canvas></div>
</div>

<h2>Findings — Successful Attacks</h2>
{"<p style='color:#3fb950'>✅ No successful attacks</p>" if not hits else ""}
{"" if not hits else f'''
<table>
  <thead><tr><th>ID</th><th>Name</th><th>OWASP</th><th>Risk</th><th>Result</th><th>Reason</th></tr></thead>
  <tbody>
  ''' + "".join(f"""
  <tr>
    <td><code>{h["attack_id"]}</code></td>
    <td>{h["attack_name"]}</td>
    <td><small>{h.get("owasp","N/A")}</small></td>
    <td><span class="badge b-red">{h.get("risk_rating","N/A")}</span></td>
    <td><span class="badge b-red">Succeeded</span></td>
    <td><small>{h.get("reason","N/A")}</small></td>
  </tr>
  """ for h in hits) + "</tbody></table>"}

<h2>All Attack Results</h2>
<table>
  <thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Risk</th><th>Result</th></tr></thead>
  <tbody>
  {"".join(f'''
  <tr>
    <td><code>{r["attack_id"]}</code></td>
    <td>{r["attack_name"]}</td>
    <td>{r["attack_type"]}</td>
    <td>{r.get("risk_rating","N/A")}</td>
    <td><span class="badge {'b-red' if r['success'] else 'b-green'}">{'Succeeded' if r['success'] else 'Blocked'}</span></td>
  </tr>
  ''' for r in self.all_results)}
  </tbody>
</table>

<h2>Retest Results</h2>
{"<p style='color:#8b949e'>No retest results.</p>" if not self.retest_results else f'''
<table>
  <thead><tr><th>Attack ID</th><th>Mitigation</th><th>Result</th><th>Evidence</th></tr></thead>
  <tbody>
  ''' + "".join(f"""
  <tr>
    <td><code>{r["attack_id"]}</code></td>
    <td>{r.get("mitigation_applied","N/A")}</td>
    <td><span class="badge {'b-green' if r.get('mitigation_effective') else 'b-red'}">{'Fixed' if r.get('mitigation_effective') else 'Still Vulnerable'}</span></td>
    <td><small>{r.get("retest_reason","N/A")}</small></td>
  </tr>
  """ for r in self.retest_results) + "</tbody></table>"}

</main>
<footer>AI Red Teaming Lab · OWASP LLM Top 10 · MITRE ATLAS · {self.timestamp}</footer>

<script>
new Chart(document.getElementById("pie"),{{
  type:"doughnut",
  data:{{
    labels:["Succeeded","Blocked"],
    datasets:[{{data:[{s["succeeded"]},{s["blocked"]}],backgroundColor:["#f85149","#3fb950"],borderColor:["#21262d"],borderWidth:3}}]
  }},
  options:{{responsive:true,plugins:{{legend:{{position:"bottom",labels:{{color:"#c9d1d9"}}}}}}}}
}});

new Chart(document.getElementById("bar"),{{
  type:"bar",
  data:{{
    labels:{json.dumps(labels)},
    datasets:[
      {{label:"Succeeded",data:{json.dumps(succeeded)},backgroundColor:"#f8514966",borderColor:"#f85149",borderWidth:2,borderRadius:4}},
      {{label:"Blocked",data:{json.dumps(blocked)},backgroundColor:"#3fb95066",borderColor:"#3fb950",borderWidth:2,borderRadius:4}}
    ]
  }},
  options:{{
    responsive:true,
    scales:{{
      x:{{ticks:{{color:"#8b949e"}},grid:{{color:"#21262d"}}}},
      y:{{ticks:{{color:"#8b949e",stepSize:1}},grid:{{color:"#21262d"}},beginAtZero:true}}
    }},
    plugins:{{legend:{{labels:{{color:"#c9d1d9"}}}}}}
  }}
}});
</script>
</body>
</html>"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  HTML report saved: {filename}")
        return filename
