from flask import Flask, request, Response
from datetime import datetime
import html
import csv
import io

app = Flask(__name__)

# =========================
#   CSS (Finance app UI)
# =========================
CSS = r"""
<style>
  :root{
    --bg1:#050B17;
    --bg2:#020617;
    --stroke:rgba(255,255,255,.10);
    --text:rgba(255,255,255,.92);
    --muted:rgba(255,255,255,.72);
    --muted2:rgba(255,255,255,.55);
    --accent:#4da3ff;
    --good:#39d98a;
    --bad:#ff5c7a;
    --input:#ffffff;
    --inputText:#0b1220;
    --shadow:0 14px 50px rgba(0,0,0,.45);
  }

  *{box-sizing:border-box}
  body{
    margin:0;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background:
      radial-gradient(900px 500px at 20% 10%, rgba(77,163,255,.18), transparent 60%),
      radial-gradient(800px 500px at 80% 20%, rgba(57,217,138,.12), transparent 55%),
      linear-gradient(180deg, var(--bg1), var(--bg2));
    color:var(--text);
    padding:42px 18px 70px;
  }

  .top{
    max-width:1100px;
    margin:0 auto 18px;
    padding:0 8px;
  }
  .top h1{ margin:0; font-size:40px; letter-spacing:.2px; }
  .top p{ margin:6px 0 0; color:var(--muted); font-size:14px; }

  .box{
    max-width:1100px;
    margin:22px auto 0;
    background:linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
    border:1px solid var(--stroke);
    border-radius:22px;
    box-shadow:var(--shadow);
    padding:22px;
  }

  .layout{
    display:grid;
    grid-template-columns: 2fr 1fr;
    gap:22px;
    align-items:start;
  }

  .main h2{ margin:0 0 4px; font-size:26px; }
  .sub{ margin:0 0 18px; color:var(--muted2); }

  .section{
    margin-top:18px;
    padding-top:18px;
    border-top:1px solid rgba(255,255,255,.08);
  }

  .sec-title{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin-bottom:10px;
  }
  .sec-title h3{ margin:0; font-size:18px; }

  .rows{display:flex; flex-direction:column; gap:10px;}

  .row{
    display:grid;
    grid-template-columns: 1.6fr .8fr auto;
    gap:10px;
    align-items:center;
  }

  input, select{
    width:100%;
    height:44px;
    padding:10px 14px;
    border-radius:14px;
    border:1px solid rgba(0,0,0,.08);
    background:var(--input);
    color:var(--inputText);
    outline:none;
    font-size:14px;
  }
  input:focus, select:focus{
    border-color:rgba(77,163,255,.9);
    box-shadow:0 0 0 3px rgba(77,163,255,.20);
  }

  .btn{
    width:100%;
    height:52px;
    border-radius:14px;
    border:0;
    background:linear-gradient(180deg, rgba(77,163,255,1), rgba(39,122,255,1));
    color:white;
    font-weight:800;
    cursor:pointer;
    margin-top:4px;
    letter-spacing:.2px;
  }
  .btn:hover{filter:brightness(1.03)}
  .btn:active{transform:translateY(1px)}

  .btn2{
    height:38px;
    padding:0 14px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.18);
    background:rgba(255,255,255,.06);
    color:rgba(255,255,255,.92);
    cursor:pointer;
    font-weight:700;
    white-space:nowrap;
  }
  .btn2:hover{background:rgba(255,255,255,.10)}
  .btn2.danger{ border-color:rgba(255,92,122,.35); }

  .side{ position:sticky; top:16px; }
  .side h3{ margin:0 0 10px; font-size:20px; }

  .summary-card{
    background:linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
    border:1px solid rgba(255,255,255,.10);
    border-radius:18px;
    padding:14px;
  }

  .summary-row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:10px 8px;
    border-top:1px solid rgba(255,255,255,.06);
    font-size:14px;
  }
  .summary-row:first-child{border-top:none}
  .summary-row span{color:rgba(255,255,255,.78)}
  .summary-row strong{font-variant-numeric: tabular-nums}

  .hint{ margin:10px 6px 0; color:rgba(255,255,255,.72); font-size:14px; }
  .hint.good{color:var(--good); font-weight:800}
  .hint.bad{color:var(--bad); font-weight:800}

  .mini-card{
    margin-top:14px;
    background:linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.03));
    border:1px solid rgba(255,255,255,.10);
    border-radius:18px;
    padding:14px;
  }
  .mini-head{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:6px 8px 10px;
    border-bottom:1px solid rgba(255,255,255,.06);
    margin-bottom:10px;
  }
  .mini-head span{color:rgba(255,255,255,.80); font-weight:800}
  .mini-head strong{color:rgba(255,255,255,.92)}
  ol{margin:0; padding-left:18px; color:rgba(255,255,255,.92)}
  li{margin:8px 0; line-height:1.25}

  .row2{display:flex; gap:10px; flex-wrap:wrap; margin-top:10px;}
  .pill{
    display:inline-block;
    padding:8px 10px;
    border-radius:999px;
    background:rgba(255,255,255,.08);
    border:1px solid rgba(255,255,255,.10);
  }
  .pill.danger{
    border-color:rgba(255,92,122,.35);
    background:rgba(255,92,122,.10);
  }
  .big{font-size:28px; margin:12px 0 0; font-variant-numeric: tabular-nums}
  a.link{color:rgba(255,255,255,.90); text-decoration:none}
  a.link:hover{text-decoration:underline}

  /* Report charts */
  .charts{
    display:grid;
    grid-template-columns: 1.35fr .85fr;
    gap:14px;
    margin-top:10px;
  }
  .chartbox{
    background:linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
    border:1px solid rgba(255,255,255,.10);
    border-radius:18px;
    padding:14px;
  }
  .chartbox h4{ margin:0 0 10px; color:rgba(255,255,255,.88); }

  .kpis{
    display:grid;
    grid-template-columns:1fr 1fr 1fr;
    gap:12px;
    margin-top:12px;
  }
  .kpi{
    background:linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
    border:1px solid rgba(255,255,255,.10);
    border-radius:18px;
    padding:14px;
  }
  .kpi .label{color:rgba(255,255,255,.72); font-size:13px}
  .kpi .value{margin-top:6px; font-size:20px; font-weight:900; font-variant-numeric: tabular-nums}

  .smallnote{
    margin-top:10px;
    color:rgba(255,255,255,.62);
    font-size:13px;
  }

  @media(max-width: 980px){
    .layout{grid-template-columns:1fr}
    .side{position:static}
    .charts{grid-template-columns:1fr}
    .kpis{grid-template-columns:1fr}
  }
  @media(max-width: 640px){
    .row{grid-template-columns:1fr}
    .btn2{width:100%}
  }
</style>
"""

# =========================
#   JS (Live totals + save/restore + weekly/monthly/quarterly/annual)
# =========================
JS = r"""
<script>
const STORAGE_KEY = "budgetPlanner_v2";

function moneyGBP(n){
  try{
    return new Intl.NumberFormat('en-GB', { style:'currency', currency:'GBP' }).format(n);
  }catch(e){
    return "£" + (Math.round(n*100)/100).toFixed(2);
  }
}

function monthlyFactor(){
  const sel = document.getElementById('freq');
  const freq = (sel && sel.value) ? sel.value : 'monthly';
  if(freq === 'weekly') return 52/12;
  if(freq === 'quarterly') return 1/3;
  if(freq === 'annual') return 1/12;
  return 1;
}

function freqLabel(){
  const sel = document.getElementById('freq');
  const v = (sel && sel.value) ? sel.value : 'monthly';
  if(v === 'weekly') return 'Weekly inputs → Monthly totals';
  if(v === 'quarterly') return 'Quarterly inputs → Monthly totals';
  if(v === 'annual') return 'Annual inputs → Monthly totals';
  return 'Monthly inputs';
}

function buildRowHTML(sectionId){
  return `
    <input type="text" name="${sectionId}_name" placeholder="Name">
    <input type="number" name="${sectionId}_amount" step="0.01" placeholder="Amount">
    <button type="button" class="btn2 danger">Remove</button>
  `;
}

function addLine(sectionId){
  const wrap = document.getElementById(sectionId);
  if(!wrap) return;

  const div = document.createElement('div');
  div.className = 'row';
  div.innerHTML = buildRowHTML(sectionId);

  div.querySelector('button').addEventListener('click', ()=>{
    div.remove();
    saveState();
    updateAll();
  });

  wrap.appendChild(div);
  saveState();
  updateAll();
}

function getRows(sectionId){
  const wrap = document.getElementById(sectionId);
  if(!wrap) return [];
  return Array.from(wrap.querySelectorAll('.row'));
}

function readTotalMonthly(sectionId){
  const factor = monthlyFactor();
  let total = 0;
  getRows(sectionId).forEach(r=>{
    const inputs = r.querySelectorAll('input');
    if(inputs.length < 2) return;
    const v = parseFloat(inputs[1].value || "");
    if(!isNaN(v)) total += (v * factor);
  });
  return total;
}

function updateLiveTotals(){
  const income = readTotalMonthly('income');
  const out = readTotalMonthly('outgoings');
  const left = income - out;

  const elIncome = document.getElementById('liveIncome');
  const elOut = document.getElementById('liveOut');
  const elLeft = document.getElementById('liveLeft');
  const elStatus = document.getElementById('liveStatus');
  const elMode = document.getElementById('liveMode');

  if(elIncome) elIncome.textContent = moneyGBP(income);
  if(elOut) elOut.textContent = moneyGBP(out);
  if(elLeft) elLeft.textContent = moneyGBP(left);

  if(elMode) elMode.textContent = freqLabel();

  if(elStatus){
    if(income === 0 && out === 0){
      elStatus.textContent = "Start typing amounts…";
      elStatus.className = "hint";
    }else if(left >= 0){
      elStatus.textContent = "Surplus ✅";
      elStatus.className = "hint good";
    }else{
      elStatus.textContent = "Deficit ❌";
      elStatus.className = "hint bad";
    }
  }
}

function updateTopIncome(){
  const list = document.getElementById('topIncome');
  const hint = document.getElementById('incomeHint');
  if(!list) return;

  const factor = monthlyFactor();
  const items = [];
  getRows('income').forEach(r=>{
    const inputs = r.querySelectorAll('input');
    if(inputs.length < 2) return;

    const name = (inputs[0].value || "").trim();
    const v = parseFloat(inputs[1].value || "");

    if(!name) return;
    if(isNaN(v) || v <= 0) return;

    items.push({name, vMonthly: v * factor});
  });

  items.sort((a,b)=> b.vMonthly - a.vMonthly);
  const total = readTotalMonthly('income') || 0;

  list.innerHTML = "";
  if(items.length === 0){
    if(hint) hint.textContent = "Add income to see your biggest sources.";
    return;
  }

  if(hint) hint.textContent = "Your biggest income sources (monthly equiv):";
  items.slice(0,3).forEach((x)=>{
    const pct = total > 0 ? Math.round((x.vMonthly/total)*100) : 0;
    const li = document.createElement('li');
    li.textContent = `${x.name} — ${moneyGBP(x.vMonthly)} (${pct}%)`;
    list.appendChild(li);
  });
}

function updateTopOutgoings(){
  const list = document.getElementById('topSpends');
  const hint = document.getElementById('topHint');
  if(!list) return;

  const factor = monthlyFactor();
  const items = [];
  getRows('outgoings').forEach(r=>{
    const inputs = r.querySelectorAll('input');
    if(inputs.length < 2) return;

    const name = (inputs[0].value || "").trim();
    const v = parseFloat(inputs[1].value || "");

    if(!name) return;
    if(isNaN(v) || v <= 0) return;

    items.push({name, vMonthly: v * factor});
  });

  items.sort((a,b)=> b.vMonthly - a.vMonthly);
  const total = readTotalMonthly('outgoings') || 0;

  list.innerHTML = "";
  if(items.length === 0){
    if(hint) hint.textContent = "Add outgoings to see your biggest costs.";
    return;
  }

  if(hint) hint.textContent = "Your biggest monthly costs (monthly equiv):";
  items.slice(0,3).forEach((x)=>{
    const pct = total > 0 ? Math.round((x.vMonthly/total)*100) : 0;
    const li = document.createElement('li');
    li.textContent = `${x.name} — ${moneyGBP(x.vMonthly)} (${pct}%)`;
    list.appendChild(li);
  });
}

function updateAll(){
  updateLiveTotals();
  updateTopIncome();
  updateTopOutgoings();
}

/* ===== SAVE / RESTORE ===== */
function getFormState(){
  const freq = (document.getElementById('freq')?.value) || "monthly";

  function readSection(id){
    const rows = [];
    document.querySelectorAll(`#${id} .row`).forEach(r=>{
      const inputs = r.querySelectorAll('input');
      if(inputs.length < 2) return;
      rows.push({
        name: inputs[0].value || "",
        amount: inputs[1].value || ""
      });
    });
    return rows;
  }

  return {
    freq,
    income: readSection('income'),
    outgoings: readSection('outgoings')
  };
}

function saveState(){
  try{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(getFormState()));
  }catch(e){}
}

function loadState(){
  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    if(!raw) return;
    const state = JSON.parse(raw);

    const freqEl = document.getElementById('freq');
    if(freqEl && state.freq) freqEl.value = state.freq;

    function rebuildSection(id, arr, sectionId){
      const wrap = document.getElementById(id);
      if(!wrap) return;
      wrap.innerHTML = "";

      (arr || []).forEach(item=>{
        const div = document.createElement('div');
        div.className = 'row';
        div.innerHTML = buildRowHTML(sectionId);

        const inputs = div.querySelectorAll('input');
        inputs[0].value = item.name || "";
        inputs[1].value = item.amount || "";

        div.querySelector('button').addEventListener('click', ()=>{
          div.remove();
          saveState();
          updateAll();
        });

        wrap.appendChild(div);
      });

      if(wrap.querySelectorAll('.row').length === 0){
        addLine(sectionId);
        addLine(sectionId);
      }
    }

    rebuildSection('income', state.income, 'income');
    rebuildSection('outgoings', state.outgoings, 'outgoings');
  }catch(e){}
}

function clearSaved(){
  try{ localStorage.removeItem(STORAGE_KEY); }catch(e){}
  location.reload();
}
/* ===== END SAVE / RESTORE ===== */

document.addEventListener('input', (e)=>{
  if(e.target && e.target.matches('input, select')){
    saveState();
    updateAll();
  }
});

window.addEventListener('load', ()=>{
  loadState();
  updateAll();
});
</script>
"""

# =========================
#   Helpers
# =========================
def freq_to_monthly_factor(freq: str) -> float:
  freq = (freq or "monthly").lower()
  if freq == "weekly":
    return 52.0 / 12.0
  if freq == "quarterly":
    return 1.0 / 3.0
  if freq == "annual":
    return 1.0 / 12.0
  return 1.0

def freq_pretty(freq: str) -> str:
  freq = (freq or "monthly").lower()
  return {"weekly":"Weekly", "monthly":"Monthly", "quarterly":"Quarterly", "annual":"Annually"}.get(freq, "Monthly")

def parse_lines(prefix: str):
  names = request.form.getlist(f"{prefix}_name")
  amounts = request.form.getlist(f"{prefix}_amount")
  lines = []
  for n, a in zip(names, amounts):
    name = (n or "").strip()
    try:
      amt = float(a) if a and a.strip() != "" else 0.0
    except ValueError:
      amt = 0.0
    if name == "" and amt == 0:
      continue
    if name == "":
      name = "Unnamed"
    lines.append((name, amt))
  return lines

def money(x: float) -> str:
  return f"£{x:,.2f}"

def shell(title: str, body_html: str) -> str:
  return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  {CSS}
  {JS}
</head>
<body>
{body_html}
</body>
</html>
"""

# =========================
#   Routes
# =========================
@app.get("/")
def home():
  body = """
<div class="top">
  <h1>Budget Planner</h1>
  <p>Enter amounts in your chosen frequency. The app converts everything into monthly totals for the summary + report.</p>
</div>

<div class="box">
  <div class="layout">

    <div class="main">
      <h2>Household Budget</h2>
      <p class="sub">Free-type your income and outgoings. Add/remove lines as needed.</p>

      <form method="post" action="/report">

        <div class="section" style="padding-top:0;border-top:none;margin-top:0;">
          <div class="sec-title">
            <h3 style="margin:0;">I’m entering numbers as</h3>
            <div style="min-width:220px;">
              <select id="freq" name="freq">
                <option value="weekly">Weekly</option>
                <option value="monthly" selected>Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="annual">Annually</option>
              </select>
            </div>
          </div>
          <div class="smallnote">Totals and charts show <b>monthly equivalents</b> so everything stays comparable.</div>
        </div>

        <div class="section">
          <div class="sec-title">
            <h3>Income</h3>
            <button type="button" class="btn2" onclick="addLine('income')">+ Add income line</button>
          </div>

          <div class="rows" id="income">
            <div class="row">
              <input type="text" name="income_name" placeholder="Name (e.g. Salary)">
              <input type="number" name="income_amount" step="0.01" placeholder="Amount">
              <button type="button" class="btn2 danger" onclick="this.parentElement.remove(); saveState(); updateAll();">Remove</button>
            </div>
            <div class="row">
              <input type="text" name="income_name" placeholder="Name (e.g. Other income)">
              <input type="number" name="income_amount" step="0.01" placeholder="Amount">
              <button type="button" class="btn2 danger" onclick="this.parentElement.remove(); saveState(); updateAll();">Remove</button>
            </div>
          </div>
        </div>

        <div class="section">
          <div class="sec-title">
            <h3>Outgoings</h3>
            <button type="button" class="btn2" onclick="addLine('outgoings')">+ Add outgoing line</button>
          </div>

          <div class="rows" id="outgoings">
            <div class="row">
              <input type="text" name="outgoings_name" placeholder="Name (e.g. Rent/Mortgage)">
              <input type="number" name="outgoings_amount" step="0.01" placeholder="Amount">
              <button type="button" class="btn2 danger" onclick="this.parentElement.remove(); saveState(); updateAll();">Remove</button>
            </div>
            <div class="row">
              <input type="text" name="outgoings_name" placeholder="Name (e.g. Bills)">
              <input type="number" name="outgoings_amount" step="0.01" placeholder="Amount">
              <button type="button" class="btn2 danger" onclick="this.parentElement.remove(); saveState(); updateAll();">Remove</button>
            </div>
          </div>
        </div>

        <div class="section">
          <button class="btn" type="submit">Run report</button>
          <div class="smallnote" style="margin-top:10px;">
            <button type="button" class="btn2" onclick="clearSaved()">Clear saved data</button>
          </div>
        </div>

      </form>
    </div>

    <div class="side">
      <h3>Summary</h3>

      <div class="summary-card">
        <div class="summary-row"><span>Total income (monthly)</span><strong id="liveIncome">£0.00</strong></div>
        <div class="summary-row"><span>Total outgoings (monthly)</span><strong id="liveOut">£0.00</strong></div>
        <div class="summary-row"><span>Remaining (monthly)</span><strong id="liveLeft">£0.00</strong></div>
      </div>

      <div class="hint" id="liveMode">Monthly inputs</div>
      <p class="hint" id="liveStatus">Start typing amounts…</p>

      <div class="mini-card">
        <div class="mini-head">
          <span>Top income</span>
          <strong>Monthly equiv</strong>
        </div>
        <ol id="topIncome"></ol>
        <div class="hint" id="incomeHint" style="margin-top:10px;">Add income to see your biggest sources.</div>
      </div>

      <div class="mini-card">
        <div class="mini-head">
          <span>Top outgoings</span>
          <strong>Monthly equiv</strong>
        </div>
        <ol id="topSpends"></ol>
        <div class="hint" id="topHint" style="margin-top:10px;">Add outgoings to see your biggest costs.</div>
      </div>
    </div>

  </div>
</div>
"""
  return shell("Budget Planner", body)

@app.post("/report")
def report():
  freq = request.form.get("freq", "monthly")
  factor = freq_to_monthly_factor(freq)
  freq_name = freq_pretty(freq)

  income_lines_raw = parse_lines("income")
  outgoing_lines_raw = parse_lines("outgoings")

  # Convert to monthly equivalents
  income_lines = [(n, a * factor) for n, a in income_lines_raw]
  outgoing_lines = [(n, a * factor) for n, a in outgoing_lines_raw]

  total_income = sum(a for _, a in income_lines)
  total_out = sum(a for _, a in outgoing_lines)
  left = total_income - total_out

  annual_income = total_income * 12
  annual_out = total_out * 12
  annual_left = left * 12

  status = "Surplus ✅" if left >= 0 else "Deficit ❌"
  pill_class = "pill" if left >= 0 else "pill danger"

  income_list_html = "".join(
    f"<li>{html.escape(n)}: {money(a)}</li>" for n, a in income_lines
  ) or "<li>None</li>"

  out_list_html = "".join(
    f"<li>{html.escape(n)}: {money(a)}</li>" for n, a in outgoing_lines
  ) or "<li>None</li>"

  biggest_income = max(income_lines, key=lambda x: x[1], default=("None", 0.0))
  biggest_out = max(outgoing_lines, key=lambda x: x[1], default=("None", 0.0))

  # Keep original raw data in hidden fields + carry freq through to download
  hidden_freq = f"<input type='hidden' name='freq' value='{html.escape(freq, quote=True)}'>"
  hidden_income = "\n".join(
    f"<input type='hidden' name='income_name' value='{html.escape(n, quote=True)}'>"
    f"<input type='hidden' name='income_amount' value='{a}'>"
    for n, a in income_lines_raw
  )
  hidden_out = "\n".join(
    f"<input type='hidden' name='outgoings_name' value='{html.escape(n, quote=True)}'>"
    f"<input type='hidden' name='outgoings_amount' value='{a}'>"
    for n, a in outgoing_lines_raw
  )

  chart_js = f"""
<script>
(function(){{
  const income = {total_income};
  const outgoings = {total_out};
  const left = income - outgoings;

  new Chart(document.getElementById('barChart'), {{
    type: 'bar',
    data: {{
      labels: ['Income (monthly)', 'Outgoings (monthly)'],
      datasets: [{{ label:'£', data:[income, outgoings] }}]
    }},
    options: {{
      responsive:true,
      plugins: {{ legend: {{ display:false }} }},
      scales: {{
        y: {{
          ticks: {{
            callback: function(value) {{
              try {{
                return new Intl.NumberFormat('en-GB', {{ style:'currency', currency:'GBP' }}).format(value);
              }} catch(e) {{
                return '£' + value;
              }}
            }}
          }}
        }}
      }}
    }}
  }});

  new Chart(document.getElementById('donutChart'), {{
    type: 'doughnut',
    data: {{
      labels: ['Outgoings (monthly)', 'Remaining (monthly)'],
      datasets: [{{ data:[outgoings, Math.max(left, 0)] }}]
    }},
    options: {{
      responsive:true,
      plugins: {{
        legend: {{ position:'bottom' }}
      }}
    }}
  }});
}})();
</script>
"""

  body = f"""
<div class="top">
  <h1>Report</h1>
  <p>Inputs were <b>{freq_name}</b>. All figures below are <b>monthly equivalents</b> (and annual projections).</p>
</div>

<div class="box">
  <div class="layout">

    <div class="main">
      <div class="row2">
        <span class="pill"><b>Total income (monthly):</b> {money(total_income)}</span>
        <span class="pill"><b>Total outgoings (monthly):</b> {money(total_out)}</span>
        <span class="{pill_class}"><b>{status}</b></span>
      </div>

      <p class="big"><b>Money left (monthly):</b> {money(left)}</p>

      <div class="charts section">
        <div class="chartbox">
          <h4>Income vs Outgoings</h4>
          <canvas id="barChart" height="140"></canvas>
        </div>
        <div class="chartbox">
          <h4>Breakdown</h4>
          <canvas id="donutChart" height="140"></canvas>
        </div>
      </div>

      <div class="kpis">
        <div class="kpi">
          <div class="label">Annual income projection</div>
          <div class="value">{money(annual_income)}</div>
        </div>
        <div class="kpi">
          <div class="label">Annual outgoings projection</div>
          <div class="value">{money(annual_out)}</div>
        </div>
        <div class="kpi">
          <div class="label">Annual Remaining projection</div>
          <div class="value">{money(annual_left)}</div>
        </div>
      </div>

      <div class="kpis">
        <div class="kpi">
          <div class="label">Biggest income source (monthly equiv)</div>
          <div class="value">{html.escape(biggest_income[0])}</div>
          <div class="hint" style="margin:6px 0 0;">{money(biggest_income[1])}</div>
        </div>
        <div class="kpi">
          <div class="label">Biggest outgoing (monthly equiv)</div>
          <div class="value">{html.escape(biggest_out[0])}</div>
          <div class="hint" style="margin:6px 0 0;">{money(biggest_out[1])}</div>
        </div>
        <div class="kpi">
          <div class="label">Savings rate (left / income)</div>
          <div class="value">{(round((left/total_income)*100) if total_income else 0)}%</div>
          <div class="hint" style="margin:6px 0 0;">(informational)</div>
        </div>
      </div>

      <div class="section">
        <h3>Income breakdown (monthly equiv)</h3>
        <ul>{income_list_html}</ul>
      </div>

      <div class="section">
        <h3>Outgoings breakdown (monthly equiv)</h3>
        <ul>{out_list_html}</ul>
      </div>

      <div class="section row2">
        <form method="post" action="/download">
          {hidden_freq}
          {hidden_income}
          {hidden_out}
          <button class="btn" type="submit">Download report data (CSV)</button>
        </form>
        <a class="link" href="/">← Back to editor</a>
      </div>

      {chart_js}
    </div>

    <div class="side">
      <h3>Summary</h3>
      <div class="summary-card">
        <div class="summary-row"><span>Inputs frequency</span><strong>{freq_name}</strong></div>
        <div class="summary-row"><span>Monthly income</span><strong>{money(total_income)}</strong></div>
        <div class="summary-row"><span>Monthly outgoings</span><strong>{money(total_out)}</strong></div>
        <div class="summary-row"><span>Monthly Remaining</span><strong>{money(left)}</strong></div>
      </div>
      <p class="hint {'good' if left >= 0 else 'bad'}">{status}</p>

      <div class="mini-card">
        <div class="mini-head">
          <span>Report date</span>
          <strong>{datetime.now().strftime('%d %b %Y')}</strong>
        </div>
        <div class="hint" style="margin-top:10px;">
          Autosave is on — use “Clear saved data” on the editor page if needed.
        </div>
      </div>
    </div>

  </div>
</div>
"""
  return shell("Report", body)

@app.post("/download")
def download():
  freq = request.form.get("freq", "monthly")
  factor = freq_to_monthly_factor(freq)

  income_lines_raw = parse_lines("income")
  outgoing_lines_raw = parse_lines("outgoings")

  income_lines = [(n, a * factor) for n, a in income_lines_raw]
  outgoing_lines = [(n, a * factor) for n, a in outgoing_lines_raw]

  total_income = sum(a for _, a in income_lines)
  total_out = sum(a for _, a in outgoing_lines)
  left = total_income - total_out

  output = io.StringIO()
  writer = csv.writer(output)
  writer.writerow(["Note", f"Inputs frequency: {freq_pretty(freq)} (exported as monthly equivalents)"])
  writer.writerow([])
  writer.writerow(["Type", "Name", "MonthlyEquivalentAmount"])

  for n, a in income_lines:
    writer.writerow(["Income", n, f"{a:.2f}"])
  for n, a in outgoing_lines:
    writer.writerow(["Outgoings", n, f"{a:.2f}"])

  writer.writerow([])
  writer.writerow(["Totals", "Total income (monthly)", f"{total_income:.2f}"])
  writer.writerow(["Totals", "Total outgoings (monthly)", f"{total_out:.2f}"])
  writer.writerow(["Totals", "Money left (monthly)", f"{left:.2f}"])
  writer.writerow(["Totals", "Annual Remaining projection", f"{(left*12):.2f}"])

  filename = f"budget_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
  return Response(
    output.getvalue(),
    mimetype="text/csv",
    headers={"Content-Disposition": f"attachment; filename={filename}"},
  )

if __name__ == "__main__":
  app.run(debug=True)
