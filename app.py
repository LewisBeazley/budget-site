from flask import Flask, request, Response
from datetime import datetime

app = Flask(__name__)

CSS = """
<style>
  body {font-family: Arial, sans-serif; background:#f5f5f5; padding:40px;}
  .box {background:#fff; padding:24px; border-radius:12px; max-width:900px; margin:auto; box-shadow:0 6px 18px rgba(0,0,0,.08);}
  h1 {margin:0 0 6px;}
  .sub {margin:0 0 18px; color:#555;}
  .section {margin-top:18px; padding-top:18px; border-top:1px solid #eee;}
  .sec-title {display:flex; align-items:center; justify-content:space-between; margin:0 0 10px;}
  .rows {display:flex; flex-direction:column; gap:10px;}
  .row {display:grid; grid-template-columns: 1.2fr 0.6fr auto; gap:10px; align-items:center;}
  input {width:100%; padding:10px 12px; border:1px solid #ddd; border-radius:10px; font-size:14px;}
  input:focus {outline:none; border-color:#888;}
  .btn {padding:10px 12px; border-radius:10px; border:0; background:#111; color:#fff; cursor:pointer;}
  .btn:hover {opacity:.92;}
  .btn2 {padding:10px 12px; border-radius:10px; border:1px solid #ddd; background:#fff; cursor:pointer;}
  .btn2:hover {background:#fafafa;}
  .danger {border:1px solid #f0caca; background:#fff3f3;}
  .pill {display:inline-block; padding:8px 10px; border-radius:999px; background:#eee;}
  .row2 {display:flex; gap:10px; flex-wrap:wrap; margin-top:10px;}
  .big {font-size:28px; margin:10px 0 0;}
  a {color:#111;}
  @media(max-width:720px){ .row{grid-template-columns:1fr; } }
</style>
"""

JS = """
<script>
function addLine(sectionId){
  const wrap = document.getElementById(sectionId);
  const div = document.createElement('div');
  div.className = 'row';
  div.innerHTML = `
    <input name="${sectionId}_name" placeholder="Name (e.g. Netflix, Wages, Child benefit)">
    <input name="${sectionId}_amount" type="number" step="0.01" placeholder="Amount">
    <button type="button" class="btn2" onclick="this.parentElement.remove()">Remove</button>
  `;
  wrap.appendChild(div);
}
</script>
"""

def parse_lines(prefix: str):
    """
    Reads pairs of fields like:
      income_name, income_amount (multiple)
      outgoings_name, outgoings_amount (multiple)
    Returns list of (name, amount)
    """
    names = request.form.getlist(f"{prefix}_name")
    amounts = request.form.getlist(f"{prefix}_amount")
    lines = []
    for n, a in zip(names, amounts):
        name = (n or "").strip()
        amt = float(a) if (a and a.strip() != "") else 0.0
        if name == "" and amt == 0:
            continue
        # If they typed amount but no name, give it a default label
        if name == "":
            name = "Unnamed"
        lines.append((name, amt))
    return lines

def money(x: float) -> str:
    return f"£{x:,.2f}"

@app.get("/")
def home():
    # Start with a couple of rows in each section
    return f"""
    <html>
    <head>
      <title>Budget Planner</title>
      {CSS}
      {JS}
    </head>
    <body>
      <div class="box">
        <h1>Household Budget Planner</h1>
        <p class="sub">Free-type your income and outgoings. Add/remove lines as needed.</p>

        <form method="post" action="/calculate">

          <div class="section">
            <div class="sec-title">
              <h2 style="margin:0;">Income</h2>
              <button type="button" class="btn2" onclick="addLine('income')">+ Add income line</button>
            </div>

            <div class="rows" id="income">
              <div class="row">
                <input name="income_name" placeholder="Name (e.g. Salary)">
                <input name="income_amount" type="number" step="0.01" placeholder="Amount">
                <button type="button" class="btn2" onclick="this.parentElement.remove()">Remove</button>
              </div>
              <div class="row">
                <input name="income_name" placeholder="Name (e.g. Other income)">
                <input name="income_amount" type="number" step="0.01" placeholder="Amount">
                <button type="button" class="btn2" onclick="this.parentElement.remove()">Remove</button>
              </div>
            </div>
          </div>

          <div class="section">
            <div class="sec-title">
              <h2 style="margin:0;">Outgoings</h2>
              <button type="button" class="btn2" onclick="addLine('outgoings')">+ Add outgoing line</button>
            </div>

            <div class="rows" id="outgoings">
              <div class="row">
                <input name="outgoings_name" placeholder="Name (e.g. Rent/Mortgage)">
                <input name="outgoings_amount" type="number" step="0.01" placeholder="Amount">
                <button type="button" class="btn2" onclick="this.parentElement.remove()">Remove</button>
              </div>
              <div class="row">
                <input name="outgoings_name" placeholder="Name (e.g. Bills)">
                <input name="outgoings_amount" type="number" step="0.01" placeholder="Amount">
                <button type="button" class="btn2" onclick="this.parentElement.remove()">Remove</button>
              </div>
            </div>
          </div>

          <div class="section">
            <button class="btn" type="submit" style="width:100%;">Calculate</button>
          </div>

        </form>
      </div>
    </body>
    </html>
    """

@app.post("/calculate")
def calculate():
    income_lines = parse_lines("income")
    outgoing_lines = parse_lines("outgoings")

    total_income = sum(a for _, a in income_lines)
    total_out = sum(a for _, a in outgoing_lines)
    left = total_income - total_out

    status = "Surplus ✅" if left >= 0 else "Deficit ❌"
    pill_class = "pill" if left >= 0 else "pill danger"

    # Hidden fields to pass user entries to /download
    hidden_income = "\n".join(
        f"<input type='hidden' name='income_name' value='{n}'>"
        f"<input type='hidden' name='income_amount' value='{a}'>"
        for n, a in income_lines
    )
    hidden_out = "\n".join(
        f"<input type='hidden' name='outgoings_name' value='{n}'>"
        f"<input type='hidden' name='outgoings_amount' value='{a}'>"
        for n, a in outgoing_lines
    )

    income_list_html = "".join(f"<li>{n}: {money(a)}</li>" for n, a in income_lines) or "<li>None</li>"
    out_list_html = "".join(f"<li>{n}: {money(a)}</li>" for n, a in outgoing_lines) or "<li>None</li>"

    return f"""
    <html>
    <head>
      <title>Budget Result</title>
      {CSS}
    </head>
    <body>
      <div class="box">
        <h1>Budget Result</h1>
        <p class="sub">Your totals and breakdown.</p>

        <div class="row2">
          <span class="pill"><b>Total income:</b> {money(total_income)}</span>
          <span class="pill"><b>Total outgoings:</b> {money(total_out)}</span>
          <span class="{pill_class}"><b>{status}</b></span>
        </div>

        <p class="big"><b>Money left:</b> {money(left)}</p>

        <div class="section">
          <h2 style="margin:0 0 10px;">Income breakdown</h2>
          <ul>{income_list_html}</ul>
        </div>

        <div class="section">
          <h2 style="margin:0 0 10px;">Outgoings breakdown</h2>
          <ul>{out_list_html}</ul>
        </div>

        <div class="section row2">
          <form method="post" action="/download">
            {hidden_income}
            {hidden_out}
            <button class="btn" type="submit">Download my budget (CSV)</button>
          </form>
          <a href="/" style="align-self:center;">← Back</a>
        </div>
      </div>
    </body>
    </html>
    """

@app.post("/download")
def download():
    income_lines = parse_lines("income")
    outgoing_lines = parse_lines("outgoings")

    total_income = sum(a for _, a in income_lines)
    total_out = sum(a for _, a in outgoing_lines)
    left = total_income - total_out

    # CSV (Excel-friendly)
    lines = []
    lines.append("Type,Name,Amount")
    for n, a in income_lines:
        lines.append(f"Income,{n},{a:.2f}")
    for n, a in outgoing_lines:
        lines.append(f"Outgoings,{n},{a:.2f}")
    lines.append(f"Totals,Total income,{total_income:.2f}")
    lines.append(f"Totals,Total outgoings,{total_out:.2f}")
    lines.append(f"Totals,Money left,{left:.2f}")

    csv_content = "\n".join(lines)
    filename = f"budget_{datetime.now().strftime('%Y-%m-%d')}.csv"

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

if __name__ == "__main__":
    app.run(debug=True)
