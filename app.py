import html, os, re, shutil, smtplib, sqlite3, ssl
from contextlib import contextmanager
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# ---- Persistence: set DB_PATH to a folder on a PERSISTENT disk/volume (e.g. /var/data/data.db),
# otherwise most hosts wipe the file on every restart/redeploy.
DB = os.environ.get("DB_PATH", "data.db")
PERSISTENT = bool(os.environ.get("DB_PATH"))
SPEC = {  # table -> required / text / numeric fields
    "r": dict(req=["name", "hire_date", "resign_date", "last_day"], txt=["title", "branch", "reason", "manager", "recipient"], num=["net_pay"]),
    "h": dict(req=["name", "hire_date"], txt=["title", "branch", "grading", "education", "age", "address", "experience", "manager", "recipient"],
              num=["basic", "allowance", "kpi"]),
}
fields = lambda t: SPEC[t]["req"] + SPEC[t]["txt"] + SPEC[t]["num"]
app = FastAPI()


@contextmanager
def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init():
    os.makedirs(os.path.dirname(os.path.abspath(DB)), exist_ok=True)
    with db() as c:
        for t in SPEC:
            typ = lambda k: "REAL" if k in SPEC[t]["num"] else "TEXT"
            c.execute(f"CREATE TABLE IF NOT EXISTS {t}(id INTEGER PRIMARY KEY AUTOINCREMENT," +
                      ",".join(f"{k} {typ(k)}" for k in fields(t)) + ",status TEXT DEFAULT 'Pending')")
            have = {x[1] for x in c.execute(f"PRAGMA table_info({t})")}
            for k in fields(t):
                if k not in have:
                    c.execute(f"ALTER TABLE {t} ADD COLUMN {k} {typ(k)}")


init()


def check(t):
    if t not in SPEC:
        raise HTTPException(404, "غير موجود")


def values(t, b):
    for k in SPEC[t]["req"]:
        if not str(b.get(k) or "").strip():
            raise HTTPException(400, f"الحقل مطلوب: {k}")
    return [float(b.get(k) or 0) if k in SPEC[t]["num"] else str(b.get(k) or "").strip() for k in fields(t)]


def row(t, i):
    check(t)
    with db() as c:
        r = c.execute(f"select * from {t} where id=?", (i,)).fetchone()
    if not r:
        raise HTTPException(404, "غير موجود")
    return dict(r)


def tpl(t, r, note=""):
    e = html.escape
    if t == "r":
        days = max((date.fromisoformat(r["last_day"]) - date.fromisoformat(r["hire_date"])).days, 0)
        head = "RESIGNATION APPROVAL REQUEST"
        rows = [("Employee", r["name"]), ("Job Title", r["title"]), ("Branch", r["branch"]), ("Hiring Date", r["hire_date"]),
                ("Resignation Date", r["resign_date"]), ("Last Working Day", r["last_day"]), ("Experience", f"{days} Days"),
                ("Net Pay", f"{r['net_pay']:,.0f} EGP"), ("Reason", r["reason"]), ("Direct Manager", r["manager"]), ("Status", r["status"])]
    else:
        total = (r["basic"] or 0) + (r["allowance"] or 0) + (r["kpi"] or 0)
        head = "NEW HIRE APPROVAL FORM"
        rows = [("Employee", r["name"]), ("Job Title", r["title"]), ("Branch", r["branch"]), ("Hiring Date", r["hire_date"]),
                ("Grading", r["grading"]), ("Net Basic Salary", f"{r['basic']:,.0f} EGP"), ("Net Allowance", f"{r['allowance']:,.0f} EGP"),
                ("Net KPI 100%", f"{r['kpi']:,.0f} EGP"), ("Total Net to pay", f"{total:,.0f} EGP"), ("Education", r["education"]),
                ("Age", r["age"]), ("Address", r["address"]), ("Experience", r["experience"]), ("Direct Manager", r["manager"]), ("Status", r["status"])]
    tr = "".join(f'<tr style="background:{"#FAF8F5" if i % 2 == 0 else "#fff"}"><td style="padding:9px 14px;color:#7a6650;font-size:13px;width:38%">{k}</td>'
                 f'<td style="padding:9px 14px;font-size:13px;font-weight:600">{e(str(v))}</td></tr>' for i, (k, v) in enumerate(rows) if v)
    n = (f'<div style="margin:0 28px 18px;background:#FFF6E8;border-left:4px solid #C08A4B;padding:12px 16px;border-radius:8px;font-size:13px">{e(note)}</div>'
         if note.strip() else "")
    rec = (r["recipient"] or "Manager").strip()
    rec = rec if rec.lower().startswith(("mr.", "ms.")) else "Mr. " + rec
    return f'''<html><body style="margin:0;padding:24px 12px;background:#F7F2EA;font-family:Arial,sans-serif">
<table width="640" align="center" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background:#FFFDF9;border:1px solid #D6C2A7;border-radius:14px;overflow:hidden">
<tr><td style="background:#8C5A2B;padding:22px 28px"><div style="color:#F3E3CC;font-size:13px">Dear {e(rec)},</div>
<div style="color:#fff;font-size:22px;font-weight:800;margin-top:4px">{head}</div></td></tr>
<tr><td style="padding:20px 28px"><div style="font-size:18px;font-weight:800">{e(r["name"])}</div><div style="color:#555;font-size:13px">{e(r["title"])} · {e(r["branch"])}</div></td></tr>
<tr><td style="padding:0 28px 18px"><table width="100%" cellspacing="0" style="border:1px solid #D6C2A7">{tr}</table></td></tr>
<tr><td>{n}</td></tr>
<tr><td style="padding:12px 28px;background:#EADBCE;font-size:11px;color:#7a6650;text-align:center">HR Portal · {date.today():%d/%m/%Y}</td></tr></table></body></html>'''


# ---- utility routes (must come before /api/{t})
@app.get("/api/info")
def info():
    with db() as c:
        n = {t: c.execute(f"select count(*) from {t}").fetchone()[0] for t in SPEC}
    return {"db": os.path.abspath(DB), "persistent": PERSISTENT, "counts": n}


@app.get("/api/backup")
def backup():
    return FileResponse(DB, filename="backup.db")


@app.post("/api/restore")
async def restore(req: Request):
    data = await req.body()
    if data[:16] != b"SQLite format 3\x00":
        raise HTTPException(400, "الملف ليس قاعدة بيانات صحيحة")
    tmp = DB + ".restore"
    with open(tmp, "wb") as f:
        f.write(data)
    try:
        con = sqlite3.connect(tmp)
        names = {x[0] for x in con.execute("select name from sqlite_master where type='table'")}
        con.close()
    except sqlite3.DatabaseError:
        names = set()
    if not names & set(SPEC):
        os.remove(tmp)
        raise HTTPException(400, "الملف لا يحتوي على بيانات الاستقالات أو التعيينات")
    if os.path.exists(DB):
        shutil.copy(DB, DB + ".before_restore")
    os.replace(tmp, DB)
    init()
    return {"ok": 1}


# ---- generic CRUD: /api/r (resignations) and /api/h (new hires)
@app.get("/api/{t}")
def lst(t: str):
    check(t)
    with db() as c:
        return [dict(x) for x in c.execute(f"select * from {t} order by id desc")]


@app.post("/api/{t}")
def add(t: str, b: dict = Body(...)):
    check(t)
    v = values(t, b)
    with db() as c:
        cur = c.execute(f"insert into {t}({','.join(fields(t))}) values({','.join('?' * len(v))})", v)
        return {"id": cur.lastrowid}


@app.put("/api/{t}/{i}")
def upd(t: str, i: int, b: dict = Body(...)):
    check(t)
    v = values(t, b)
    with db() as c:
        c.execute(f"update {t} set " + ",".join(f"{k}=?" for k in fields(t)) + " where id=?", v + [i])
    return {"ok": 1}


@app.post("/api/{t}/{i}/status/{s}")
def status(t: str, i: int, s: str):
    check(t)
    if s not in ("Pending", "Approved", "Rejected"):
        raise HTTPException(400, "حالة غير صحيحة")
    with db() as c:
        c.execute(f"update {t} set status=? where id=?", (s, i))
    return {"ok": 1}


@app.delete("/api/{t}/{i}")
def rm(t: str, i: int):
    check(t)
    with db() as c:
        c.execute(f"delete from {t} where id=?", (i,))
    return {"ok": 1}


@app.get("/api/{t}/{i}/preview", response_class=HTMLResponse)
def preview(t: str, i: int, note: str = ""):
    return tpl(t, row(t, i), note)


@app.post("/api/{t}/{i}/mail")
def mail(t: str, i: int, m: dict = Body(...)):
    u, p = os.environ.get("SENDER_EMAIL"), os.environ.get("SENDER_PASSWORD")
    if not (u and p):
        raise HTTPException(400, "SENDER_EMAIL / SENDER_PASSWORD غير مضبوطين")
    r = row(t, i)
    to = [x for x in re.split(r"[;,\s]+", m.get("to", "")) if x]
    cc = [x for x in re.split(r"[;,\s]+", m.get("cc", "")) if x]
    if not to:
        raise HTTPException(400, "اكتب إيميل المستلم")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = m.get("subject") or f"{'Resignation' if t == 'r' else 'New Hire'} Approval Request - {r['name']}"
    msg["From"] = formataddr((os.environ.get("SENDER_NAME", "HR Department"), u))
    msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg.attach(MIMEText(tpl(t, r, m.get("note", "")), "html", "utf-8"))
    try:
        s = smtplib.SMTP(os.environ.get("SMTP_SERVER", "smtp.office365.com"), int(os.environ.get("SMTP_PORT", 587)), timeout=20)
        s.starttls(context=ssl.create_default_context())
        s.login(u, p)
        s.sendmail(u, to + cc, msg.as_string())
        s.quit()
    except Exception as ex:
        raise HTTPException(500, f"فشل الإرسال: {ex}")
    return {"ok": 1}


app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"), html=True))
