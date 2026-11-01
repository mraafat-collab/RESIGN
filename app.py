import html, os, re, smtplib, sqlite3, ssl
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

DB = os.environ.get("DB_PATH", "data.db")
F = ["name", "title", "branch", "hire_date", "resign_date", "last_day", "net_pay", "reason", "manager", "recipient"]
app = FastAPI()

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

with db() as c:
    c.execute("CREATE TABLE IF NOT EXISTS r(id INTEGER PRIMARY KEY AUTOINCREMENT," +
              ",".join(f"{k} REAL" if k == "net_pay" else f"{k} TEXT" for k in F) + ",status TEXT DEFAULT 'Pending')")

class R(BaseModel):
    name: str; hire_date: str; resign_date: str; last_day: str
    title: str = ""; branch: str = ""; net_pay: float = 0; reason: str = ""; manager: str = ""; recipient: str = ""

class Mail(BaseModel):
    to: str; cc: str = ""; subject: str = ""; note: str = ""

def row(i):
    with db() as c:
        r = c.execute("select * from r where id=?", (i,)).fetchone()
    if not r: raise HTTPException(404, "غير موجود")
    return dict(r)

def tpl(r, note=""):
    e = html.escape
    days = max((date.fromisoformat(r["last_day"]) - date.fromisoformat(r["hire_date"])).days, 0)
    rows = [("Employee", r["name"]), ("Job Title", r["title"]), ("Branch", r["branch"]), ("Hiring Date", r["hire_date"]),
            ("Resignation Date", r["resign_date"]), ("Last Working Day", r["last_day"]), ("Experience", f"{days} Days"),
            ("Net Pay", f"{r['net_pay']:,.0f} EGP"), ("Reason", r["reason"]), ("Direct Manager", r["manager"]), ("Status", r["status"])]
    tr = "".join(f'<tr style="background:{"#FAF8F5" if i % 2 == 0 else "#fff"}"><td style="padding:9px 14px;color:#7a6650;font-size:13px;width:38%">{k}</td>'
                 f'<td style="padding:9px 14px;font-size:13px;font-weight:600">{e(str(v))}</td></tr>' for i, (k, v) in enumerate(rows) if v)
    n = f'<div style="margin:0 28px 18px;background:#FFF6E8;border-left:4px solid #C08A4B;padding:12px 16px;border-radius:8px;font-size:13px">{e(note)}</div>' if note.strip() else ""
    rec = (r["recipient"] or "Manager").strip()
    return f'''<html><body style="margin:0;padding:24px 12px;background:#F7F2EA;font-family:Arial,sans-serif">
<table width="640" align="center" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background:#FFFDF9;border:1px solid #D6C2A7;border-radius:14px;overflow:hidden">
<tr><td style="background:#8C5A2B;padding:22px 28px"><div style="color:#F3E3CC;font-size:13px">Dear {e(rec if rec.lower().startswith(("mr.","ms.")) else "Mr. "+rec)},</div>
<div style="color:#fff;font-size:22px;font-weight:800;margin-top:4px">RESIGNATION APPROVAL REQUEST</div></td></tr>
<tr><td style="padding:20px 28px"><div style="font-size:18px;font-weight:800">{e(r["name"])}</div><div style="color:#555;font-size:13px">{e(r["title"])} · {e(r["branch"])}</div></td></tr>
<tr><td style="padding:0 28px 18px"><table width="100%" cellspacing="0" style="border:1px solid #D6C2A7">{tr}</table></td></tr>
<tr><td>{n}</td></tr>
<tr><td style="padding:12px 28px;background:#EADBCE;font-size:11px;color:#7a6650;text-align:center">Resignation Portal · {date.today():%d/%m/%Y}</td></tr></table></body></html>'''

@app.get("/api/r")
def lst():
    with db() as c: return [dict(x) for x in c.execute("select * from r order by id desc")]

@app.post("/api/r")
def add(b: R):
    with db() as c:
        cur = c.execute(f"insert into r({','.join(F)}) values({','.join('?' * len(F))})", [getattr(b, k) for k in F])
        return {"id": cur.lastrowid}

@app.put("/api/r/{i}")
def upd(i: int, b: R):
    with db() as c: c.execute("update r set " + ",".join(f"{k}=?" for k in F) + " where id=?", [getattr(b, k) for k in F] + [i])
    return {"ok": 1}

@app.post("/api/r/{i}/status/{s}")
def status(i: int, s: str):
    if s not in ("Pending", "Approved", "Rejected"): raise HTTPException(400, "حالة غير صحيحة")
    with db() as c: c.execute("update r set status=? where id=?", (s, i))
    return {"ok": 1}

@app.delete("/api/r/{i}")
def rm(i: int):
    with db() as c: c.execute("delete from r where id=?", (i,))
    return {"ok": 1}

@app.get("/api/r/{i}/preview", response_class=HTMLResponse)
def preview(i: int, note: str = ""): return tpl(row(i), note)

@app.post("/api/r/{i}/mail")
def mail(i: int, m: Mail):
    u, p = os.environ.get("SENDER_EMAIL"), os.environ.get("SENDER_PASSWORD")
    if not (u and p): raise HTTPException(400, "SENDER_EMAIL / SENDER_PASSWORD غير مضبوطين")
    r = row(i)
    to = [x for x in re.split(r"[;,\s]+", m.to) if x]; cc = [x for x in re.split(r"[;,\s]+", m.cc) if x]
    if not to: raise HTTPException(400, "اكتب إيميل المستلم")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = m.subject or f"Resignation Approval Request - {r['name']}"
    msg["From"] = formataddr((os.environ.get("SENDER_NAME", "HR Department"), u)); msg["To"] = ", ".join(to)
    if cc: msg["Cc"] = ", ".join(cc)
    msg.attach(MIMEText(tpl(r, m.note), "html", "utf-8"))
    try:
        s = smtplib.SMTP(os.environ.get("SMTP_SERVER", "smtp.office365.com"), int(os.environ.get("SMTP_PORT", 587)), timeout=20)
        s.starttls(context=ssl.create_default_context()); s.login(u, p); s.sendmail(u, to + cc, msg.as_string()); s.quit()
    except Exception as ex:
        raise HTTPException(500, f"فشل الإرسال: {ex}")
    return {"ok": 1}

@app.get("/api/backup")
def backup(): return FileResponse(DB, filename="backup.db")

app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True))
