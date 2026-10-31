import base64
import io
import os
import re
import smtplib
import ssl
from datetime import date
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from docx import Document

# =========================================================
# Page config
# =========================================================
st.set_page_config(
    page_title="بوابة الاستقالات",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Palette (beige & brown)
C_BG = "#F5EFE6"
C_CARD = "#FFFDF9"
C_BORDER = "#D6C2A7"
C_SOFT = "#EADBCE"
C_BROWN = "#8C5A2B"
C_DARK = "#5B3A1A"
C_ACCENT = "#C08A4B"
C_TEXT = "#3B2A1A"


# =========================================================
# Secrets (never hardcode credentials)
# =========================================================
def get_secret(key, default=""):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


SENDER_EMAIL = get_secret("SENDER_EMAIL")
SENDER_PASSWORD = get_secret("SENDER_PASSWORD")
SENDER_NAME = get_secret("SENDER_NAME", "HR Department")
DEFAULT_SMTP = get_secret("SMTP_SERVER", "smtp.office365.com")
DEFAULT_PORT = int(get_secret("SMTP_PORT", 587))

# =========================================================
# Styling
# =========================================================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Playfair+Display:wght@600;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Cairo', sans-serif;
    color: {C_TEXT};
}}
.stApp {{
    background:
        radial-gradient(900px 500px at 100% -10%, rgba(192,138,75,.18), transparent 60%),
        radial-gradient(700px 400px at -10% 110%, rgba(140,90,43,.12), transparent 60%),
        {C_BG};
}}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.4rem; max-width: 1400px; }}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {C_DARK} 0%, #3E2710 100%);
}}
section[data-testid="stSidebar"] * {{ color: #F5EFE6 !important; }}
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {{
    background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.2);
}}
section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.15); }}

/* Hero */
.hero {{
    background: linear-gradient(120deg, {C_DARK} 0%, {C_BROWN} 55%, {C_ACCENT} 100%);
    border-radius: 24px; padding: 26px 34px; margin-bottom: 18px;
    color: #FFF8EE; position: relative; overflow: hidden;
    box-shadow: 0 14px 40px rgba(91,58,26,.28);
    direction: rtl; text-align: right;
}}
.hero:after {{
    content: ""; position: absolute; left: -60px; top: -60px; width: 220px; height: 220px;
    border-radius: 50%; background: rgba(255,255,255,.08);
}}
.hero h1 {{ margin: 0; font-size: 30px; font-weight: 800; color: #FFF8EE; }}
.hero p {{ margin: 6px 0 0; opacity: .85; font-size: 14px; }}
.hero .chip {{
    display: inline-block; background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.25);
    border-radius: 999px; padding: 3px 14px; font-size: 12px; margin-top: 12px; margin-left: 6px;
}}

/* Cards */
.card {{
    background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 20px;
    padding: 20px 22px; margin-bottom: 16px;
    box-shadow: 0 6px 22px rgba(140,90,43,.10);
}}
.card h4 {{ margin: 0 0 4px; color: {C_DARK}; font-weight: 800; }}
.muted {{ color: #8a7560; font-size: 13px; }}

/* KPI */
.kpi {{
    background: {C_CARD}; border: 1px solid {C_BORDER}; border-radius: 18px;
    padding: 16px 18px; text-align: right; direction: rtl;
    border-right: 6px solid {C_BROWN};
    box-shadow: 0 4px 16px rgba(140,90,43,.08);
}}
.kpi .l {{ font-size: 12px; color: #8a7560; font-weight: 600; }}
.kpi .v {{ font-size: 24px; font-weight: 800; color: {C_BROWN}; margin-top: 2px; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 6px; background: {C_CARD}; padding: 6px; border-radius: 16px;
    border: 1px solid {C_BORDER};
}}
.stTabs [data-baseweb="tab"] {{
    height: 44px; border-radius: 12px; padding: 0 20px;
    color: {C_BROWN}; font-weight: 700; background: transparent;
}}
.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, {C_BROWN}, {C_DARK}) !important;
    color: #FFF8EE !important; box-shadow: 0 6px 16px rgba(91,58,26,.30);
}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none; }}

/* Buttons */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
    background: linear-gradient(135deg, {C_BROWN}, {C_DARK});
    color: #FFF8EE; font-weight: 700; border: none; border-radius: 12px;
    padding: 10px 22px; box-shadow: 0 6px 16px rgba(91,58,26,.25);
    transition: all .25s ease; width: 100%;
}}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {{
    transform: translateY(-2px); color: #fff;
    background: linear-gradient(135deg, {C_ACCENT}, {C_BROWN});
}}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input {{
    background: #FFFFFF; border: 1px solid {C_BORDER}; border-radius: 10px; color: {C_TEXT};
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {C_BROWN}; box-shadow: 0 0 0 2px rgba(140,90,43,.18);
}}
label, .stMarkdown p {{ color: {C_TEXT}; }}

/* Status pill */
.pill {{
    display: inline-block; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 700;
}}
.pill.ok {{ background: #E7F0DC; color: #44631F; border: 1px solid #C6D9A8; }}
.pill.bad {{ background: #F7E0DA; color: #8A2E1B; border: 1px solid #E8B8AC; }}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# Helpers
# =========================================================
def to_english_str(text):
    if not text:
        return ""
    trans = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    return str(text).translate(trans)


def split_emails(value):
    return [e.strip() for e in re.split(r"[;,\s]+", value or "") if e.strip()]


def valid_email(addr):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", addr) is not None


def fmt(d):
    return d.strftime("%d/%m/%Y")


def recipient_title_of(data):
    rec = (data.get("recipient_name") or "Manager").strip() or "Manager"
    return rec if rec.lower().startswith(("mr.", "ms.", "mrs.", "dr.")) else f"Mr. {rec}"


def generate_word_doc(data, exp_days):
    doc = Document()
    doc.add_heading(f"RESIGNATION APPROVAL REQUEST - {data['employee_name']}", 0)
    rows = [
        ("Recipient", f"Dear {recipient_title_of(data)}"),
        ("Employee Name", data["employee_name"]),
        ("Job Title", data["job_title"]),
        ("Branch", data["branch"]),
        ("Hiring Date", fmt(data["hiring_date"])),
        ("Resignation Date", fmt(data["resignation_date"])),
        ("Last Working Day", fmt(data["last_working_day"])),
        ("Total Experience", f"{exp_days} Days"),
        ("Total Net Pay", f"{data['net_pay']:,} EGP"),
        ("Reason for Leaving", data["reason"]),
        ("Direct Manager", data["direct_manager"]),
    ]
    table = doc.add_table(rows=0, cols=2)
    table.style = "Light Grid Accent 1"
    for k, v in rows:
        cells = table.add_row().cells
        cells[0].text, cells[1].text = k, str(v)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


def generate_excel(data, exp_days):
    df = pd.DataFrame(
        [
            {
                "Recipient Name": data.get("recipient_name", ""),
                "Employee Name": data["employee_name"],
                "Branch": data["branch"],
                "Job Title": data["job_title"],
                "Hiring Date": fmt(data["hiring_date"]),
                "Resignation Date": fmt(data["resignation_date"]),
                "Last Working Day": fmt(data["last_working_day"]),
                "Total Experience (Days)": exp_days,
                "Total Net Pay (EGP)": data["net_pay"],
                "Reason": data["reason"],
                "Direct Manager": data["direct_manager"],
            }
        ]
    )
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resignation")
        ws = writer.sheets["Resignation"]
        header = writer.book.add_format({"bold": True, "bg_color": C_BROWN, "font_color": "#FFFFFF", "border": 1})
        for i, col in enumerate(df.columns):
            ws.write(0, i, col, header)
            ws.set_column(i, i, max(16, len(col) + 4))
    return out.getvalue()


# =========================================================
# Email template (table based + inline CSS = works in Outlook/Gmail)
# =========================================================
def build_email_html(data, exp_days, note="", photo_src=None):
    e = lambda v: escape(str(v))
    photo_cell = (
        f'<img src="{photo_src}" width="88" height="114" '
        f'style="border-radius:8px;border:1px solid {C_BORDER};object-fit:cover;display:block;" alt="photo">'
        if photo_src
        else f'<div style="width:88px;height:114px;background:{C_SOFT};border-radius:8px;border:1px solid {C_BORDER};'
        f'text-align:center;line-height:114px;font-size:34px;">&#128100;</div>'
    )

    def row(label, value, shade):
        bg = "#FAF8F5" if shade else "#FFFFFF"
        return (
            f'<tr><td style="padding:9px 14px;background:{bg};border-bottom:1px solid {C_SOFT};'
            f'font-size:13px;color:#7a6650;width:38%;">{label}</td>'
            f'<td style="padding:9px 14px;background:{bg};border-bottom:1px solid {C_SOFT};'
            f'font-size:13px;color:#222;font-weight:600;">{value}</td></tr>'
        )

    rows = [
        ("Employee Name", e(data["employee_name"])),
        ("Job Title", e(data["job_title"])),
        ("Branch", e(data["branch"])),
        ("Hiring Date", fmt(data["hiring_date"])),
        ("Resignation Date", fmt(data["resignation_date"])),
        ("Last Working Day", fmt(data["last_working_day"])),
        ("Total Experience", f"{exp_days} Days"),
        ("Reason for Leaving", e(data["reason"])),
        ("Direct Manager", e(data["direct_manager"])),
        ("Handover Status", e(data.get("handover_status", ""))),
    ]
    rows_html = "".join(row(k, v, i % 2 == 0) for i, (k, v) in enumerate(rows))

    note_html = (
        f'<tr><td style="padding:0 28px 18px;"><div style="background:#FFF6E8;border-left:4px solid {C_ACCENT};'
        f'padding:12px 16px;border-radius:8px;font-size:13px;color:{C_TEXT};line-height:1.6;">'
        f'{e(note).replace(chr(10), "<br>")}</div></td></tr>'
        if note.strip()
        else ""
    )

    return f"""<!DOCTYPE html>
<html><body style="margin:0;padding:24px 12px;background:{C_BG};font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" width="640" align="center" cellpadding="0" cellspacing="0"
 style="max-width:640px;width:100%;background:{C_CARD};border:1px solid {C_BORDER};border-radius:14px;overflow:hidden;">
  <tr><td style="background:{C_BROWN};padding:22px 28px;">
    <div style="color:#F3E3CC;font-size:13px;">Dear {e(recipient_title_of(data))},</div>
    <div style="color:#FFFFFF;font-size:22px;font-weight:800;letter-spacing:.5px;margin-top:4px;">
      RESIGNATION APPROVAL REQUEST</div>
  </td></tr>
  <tr><td style="padding:22px 28px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
      <td width="100" valign="top">{photo_cell}</td>
      <td valign="middle" style="padding-left:16px;">
        <div style="font-size:18px;font-weight:800;color:#111;">{e(data['employee_name'])}</div>
        <div style="font-size:13px;color:#555;margin-top:2px;">{e(data['job_title'])}</div>
        <div style="font-size:12px;color:#888;">{e(data['branch'])}</div>
      </td></tr></table>
  </td></tr>
  <tr><td style="padding:0 28px 18px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="6"><tr>
      <td align="center" style="background:{C_BROWN};color:#fff;border-radius:10px;padding:10px 6px;">
        <div style="font-size:10px;opacity:.85;">NET PAY</div>
        <div style="font-size:15px;font-weight:800;">{data['net_pay']:,} EGP</div></td>
      <td align="center" style="background:{C_DARK};color:#fff;border-radius:10px;padding:10px 6px;">
        <div style="font-size:10px;opacity:.85;">LAST WORK DAY</div>
        <div style="font-size:15px;font-weight:800;">{fmt(data['last_working_day'])}</div></td>
      <td align="center" style="background:{C_ACCENT};color:#fff;border-radius:10px;padding:10px 6px;">
        <div style="font-size:10px;opacity:.9;">EXPERIENCE</div>
        <div style="font-size:15px;font-weight:800;">{exp_days} Days</div></td>
    </tr></table>
  </td></tr>
  <tr><td style="padding:0 28px 18px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
     style="border:1px solid {C_BORDER};border-radius:10px;overflow:hidden;">{rows_html}</table>
  </td></tr>
  {note_html}
  <tr><td style="padding:14px 28px;background:{C_SOFT};font-size:11px;color:#7a6650;text-align:center;">
    Sent via Resignation Portal &bull; {date.today().strftime('%d/%m/%Y')}
  </td></tr>
</table></body></html>"""


def build_plain_text(data, exp_days, note=""):
    lines = [
        f"Dear {recipient_title_of(data)},",
        "",
        "RESIGNATION APPROVAL REQUEST",
        "",
        f"Employee: {data['employee_name']}",
        f"Job Title: {data['job_title']}",
        f"Branch: {data['branch']}",
        f"Hiring Date: {fmt(data['hiring_date'])}",
        f"Resignation Date: {fmt(data['resignation_date'])}",
        f"Last Working Day: {fmt(data['last_working_day'])}",
        f"Total Experience: {exp_days} Days",
        f"Total Net Pay: {data['net_pay']:,} EGP",
        f"Reason: {data['reason']}",
        f"Direct Manager: {data['direct_manager']}",
    ]
    if note.strip():
        lines += ["", note.strip()]
    return "\n".join(lines)


def connect_smtp(server, port):
    if port == 465:
        s = smtplib.SMTP_SSL(server, port, timeout=20, context=ssl.create_default_context())
    else:
        s = smtplib.SMTP(server, port, timeout=20)
        s.ehlo()
        s.starttls(context=ssl.create_default_context())
        s.ehlo()
    s.login(SENDER_EMAIL, SENDER_PASSWORD)
    return s


def send_resignation_email(data, exp_days, to_list, cc_list, subject, note, server, port,
                           attach_word, attach_excel):
    photo_bytes = base64.b64decode(data["photo_b64"]) if data.get("photo_b64") else None
    html = build_email_html(data, exp_days, note, "cid:employee_photo" if photo_bytes else None)

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)

    related = MIMEMultipart("related")
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(build_plain_text(data, exp_days, note), "plain", "utf-8"))
    alt.attach(MIMEText(html, "html", "utf-8"))
    related.attach(alt)
    if photo_bytes:
        img = MIMEImage(photo_bytes)
        img.add_header("Content-ID", "<employee_photo>")
        img.add_header("Content-Disposition", "inline", filename="photo")
        related.attach(img)
    msg.attach(related)

    safe_name = re.sub(r"[^\w\-]+", "_", data["employee_name"]) or "employee"
    if attach_word:
        part = MIMEApplication(generate_word_doc(data, exp_days), Name=f"Resignation_{safe_name}.docx")
        part.add_header("Content-Disposition", "attachment", filename=f"Resignation_{safe_name}.docx")
        msg.attach(part)
    if attach_excel:
        part = MIMEApplication(generate_excel(data, exp_days), Name=f"Resignation_{safe_name}.xlsx")
        part.add_header("Content-Disposition", "attachment", filename=f"Resignation_{safe_name}.xlsx")
        msg.attach(part)

    s = connect_smtp(server, port)
    try:
        s.sendmail(SENDER_EMAIL, to_list + cc_list, msg.as_string())
    finally:
        s.quit()


# =========================================================
# Data store (session)
# =========================================================
if "resignations_db" not in st.session_state:
    st.session_state.resignations_db = [
        {
            "id": 1,
            "recipient_name": "Mohamed",
            "employee_name": "Abu Bakr Muhammad Mahmoud",
            "job_title": "Sales Casual",
            "branch": "Park-St Branch",
            "grading": "G1 - L1",
            "hiring_date": date(2026, 10, 3),
            "resignation_date": date(2026, 10, 20),
            "last_working_day": date(2026, 10, 20),
            "net_pay": 7000,
            "reason": "Education",
            "direct_manager": "Sherif S. El-Sayed",
            "notice_period": "One Month",
            "handover_status": "Team Leader",
            "absence_days": 0,
            "loan_balance": 0,
            "photo_b64": None,
        }
    ]

db = st.session_state.resignations_db

# =========================================================
# Sidebar
# =========================================================
selected_id = None
data = None
with st.sidebar:
    st.markdown("### 🏛️ بوابة الاستقالات")
    st.caption("نظام الإدارة المركزي الموحد 2026")
    st.markdown("---")
    if db:
        opts = {r["id"]: f"{r['employee_name']} · {r['branch']}" for r in db}
        selected_id = st.selectbox("🎯 الموظف الحالي", list(opts.keys()), format_func=lambda x: opts[x])
        data = next(i for i in db if i["id"] == selected_id)
    st.markdown("---")
    if SENDER_EMAIL and SENDER_PASSWORD:
        st.markdown('<span class="pill ok">● البريد مُهيّأ</span>', unsafe_allow_html=True)
        st.caption(SENDER_EMAIL)
    else:
        st.markdown('<span class="pill bad">● البريد غير مُهيّأ</span>', unsafe_allow_html=True)
        st.caption("أضف SENDER_EMAIL و SENDER_PASSWORD في secrets.toml")

# =========================================================
# Hero
# =========================================================
st.markdown(
    f"""
<div class="hero">
  <h1>🏛️ بوابة الاستقالات المؤسسية</h1>
  <p>إدارة طلبات الاستقالة، التقارير، والمراسلات الرسمية من مكان واحد.</p>
  <span class="chip">{len(db)} طلب مسجل</span>
  <span class="chip">تقرير A4 جاهز للطباعة</span>
  <span class="chip">إرسال بريد بالقالب الرسمي</span>
</div>
""",
    unsafe_allow_html=True,
)

tab_hub, tab_mail, tab_manage, tab_analytics = st.tabs(
    ["📄 التقرير والتصدير", "✉️ إرسال بالقالب", "⚙️ إدارة البيانات", "📊 التحليلات"]
)

# =========================================================
# TAB 1 – Report
# =========================================================
with tab_hub:
    if not data:
        st.warning("لا توجد استقالات مسجلة. أضف واحدة من تبويب إدارة البيانات.")
    else:
        exp_days = max((data["last_working_day"] - data["hiring_date"]).days, 0)

        k1, k2, k3, k4 = st.columns(4)
        for col, label, val in [
            (k1, "الموظف", data["employee_name"]),
            (k2, "مدة الخبرة", f"{exp_days} يوم"),
            (k3, "إجمالي المستحقات", f"{data['net_pay']:,} EGP"),
            (k4, "آخر يوم عمل", fmt(data["last_working_day"])),
        ]:
            col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v" style="font-size:{18 if label=="الموظف" else 24}px">{escape(str(val))}</div></div>', unsafe_allow_html=True)

        st.write("")
        b1, b2, _ = st.columns([1, 1, 2])
        safe = re.sub(r"[^\w\-]+", "_", data["employee_name"])
        b1.download_button("📄 تصدير Word", generate_word_doc(data, exp_days), f"Resignation_{safe}.docx")
        b2.download_button("📊 تصدير Excel", generate_excel(data, exp_days), f"Resignation_{safe}.xlsx")

        st.write("")
        photo_src = f"data:image/png;base64,{data['photo_b64']}" if data.get("photo_b64") else None
        card = build_email_html(data, exp_days, "", photo_src)
        png_name = f"Resignation_{safe}.png"
        page = f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
          body{{margin:0;background:transparent;font-family:Arial,sans-serif}}
          .bar{{display:flex;gap:8px;justify-content:flex-end;margin-bottom:10px}}
          .b{{background:linear-gradient(135deg,{C_BROWN},{C_DARK});color:#fff;border:0;padding:9px 18px;
              border-radius:10px;font-weight:700;cursor:pointer}}
          @media print{{.bar{{display:none}}}}
        </style>
        <div class="bar">
          <button class="b" onclick="dl()">🖼️ تنزيل PNG</button>
          <button class="b" onclick="window.print()">🖨️ طباعة A4</button>
        </div>
        <div id="cap">{card}</div>
        <script>
          function dl(){{
            html2canvas(document.getElementById('cap'),{{scale:2,useCORS:true}}).then(c=>{{
              const a=document.createElement('a');a.download="{png_name}";
              a.href=c.toDataURL('image/png');a.click();}});
          }}
        </script>"""
        components.html(page, height=780, scrolling=True)

# =========================================================
# TAB 2 – Email with template
# =========================================================
with tab_mail:
    if not data:
        st.warning("اختر موظفاً أولاً.")
    else:
        exp_days = max((data["last_working_day"] - data["hiring_date"]).days, 0)
        left, right = st.columns([1, 1.5])

        with left:
            st.markdown('<div class="card"><h4>✉️ إعدادات الإرسال</h4>'
                        '<div class="muted">يُرسل من إيميل الشركة المُعرّف في secrets.toml</div></div>',
                        unsafe_allow_html=True)
            to_raw = st.text_input("إلى (يمكن أكثر من إيميل بفاصلة)", placeholder="hr@company.com, boss@company.com")
            cc_raw = st.text_input("نسخة (CC)", placeholder="manager@company.com")
            subject = st.text_input("الموضوع", value=f"Resignation Approval Request - {data['employee_name']}")
            note = st.text_area("ملاحظة إضافية داخل الرسالة (اختياري)", height=90)

            a1, a2 = st.columns(2)
            attach_word = a1.checkbox("إرفاق Word", value=True)
            attach_excel = a2.checkbox("إرفاق Excel", value=False)

            with st.expander("⚙️ إعدادات السيرفر"):
                smtp_server = st.text_input("SMTP Server", value=DEFAULT_SMTP)
                smtp_port = st.selectbox("Port", [587, 465, 25], index=[587, 465, 25].index(DEFAULT_PORT) if DEFAULT_PORT in (587, 465, 25) else 0)
                if st.button("🔌 اختبار الاتصال"):
                    if not (SENDER_EMAIL and SENDER_PASSWORD):
                        st.error("بيانات الإيميل غير موجودة في secrets.toml")
                    else:
                        try:
                            with st.spinner("جاري الاتصال..."):
                                s = connect_smtp(smtp_server.strip(), int(smtp_port))
                                s.quit()
                            st.success("✅ الاتصال وتسجيل الدخول ناجحان")
                        except Exception as ex:
                            st.error(f"❌ {ex}")

            if st.button("🚀 إرسال الآن"):
                to_list, cc_list = split_emails(to_raw), split_emails(cc_raw)
                bad = [x for x in to_list + cc_list if not valid_email(x)]
                if not (SENDER_EMAIL and SENDER_PASSWORD):
                    st.error("أضف SENDER_EMAIL و SENDER_PASSWORD في ملف secrets.toml")
                elif not to_list:
                    st.error("اكتب إيميل المستلم.")
                elif bad:
                    st.error(f"إيميل غير صحيح: {', '.join(bad)}")
                else:
                    try:
                        with st.spinner("جاري الإرسال..."):
                            send_resignation_email(
                                data, exp_days, to_list, cc_list, subject, note,
                                smtp_server.strip(), int(smtp_port), attach_word, attach_excel,
                            )
                        st.success(f"✅ تم الإرسال إلى {len(to_list + cc_list)} مستلم")
                    except smtplib.SMTPAuthenticationError:
                        st.error("❌ فشل تسجيل الدخول. استخدم App Password، وتأكد أن SMTP AUTH مفعّل لصندوق البريد.")
                    except Exception as ex:
                        st.error(f"❌ فشل الإرسال: {ex}")

        with right:
            st.markdown('<div class="card"><h4>👁️ معاينة الرسالة</h4>'
                        '<div class="muted">هذا هو الشكل الذي سيصل للمستلم</div></div>',
                        unsafe_allow_html=True)
            prev_photo = f"data:image/png;base64,{data['photo_b64']}" if data.get("photo_b64") else None
            components.html(build_email_html(data, exp_days, note, prev_photo), height=820, scrolling=True)

# =========================================================
# TAB 3 – Manage
# =========================================================
with tab_manage:
    st.markdown('<div class="card"><h4>⚙️ إدارة بيانات الاستقالة</h4></div>', unsafe_allow_html=True)
    action = st.radio("نوع العملية", ["إضافة ➕", "تعديل ✏️", "حذف 🗑️"], horizontal=True)

    if action == "حذف 🗑️":
        if data:
            st.warning(f"سيتم حذف: {data['employee_name']}")
            if st.button("❌ تأكيد الحذف"):
                st.session_state.resignations_db = [r for r in db if r["id"] != selected_id]
                st.rerun()
        else:
            st.info("لا توجد بيانات للحذف.")
    else:
        editing = action == "تعديل ✏️" and data is not None
        target = data if editing else {
            "id": None, "recipient_name": "", "employee_name": "", "job_title": "", "branch": "",
            "hiring_date": date.today(), "resignation_date": date.today(),
            "last_working_day": date.today(), "net_pay": 0, "reason": "", "direct_manager": "",
            "handover_status": "", "photo_b64": None,
        }
        with st.form("manage_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_name = st.text_input("اسم الموظف", value=target["employee_name"])
                j_title = st.text_input("المسمى الوظيفي", value=target["job_title"])
                br = st.text_input("الفرع", value=target["branch"])
                rec = st.text_input("الموجه له الطلب (Recipient)", value=target.get("recipient_name", ""))
                mgr = st.text_input("المدير المباشر", value=target["direct_manager"])
            with c2:
                h_dt = st.date_input("تاريخ التعيين", value=target["hiring_date"])
                r_dt = st.date_input("تاريخ الاستقالة", value=target["resignation_date"])
                l_dt = st.date_input("آخر يوم عمل", value=target["last_working_day"])
                pay = st.number_input("إجمالي المستحقات (EGP)", value=int(target["net_pay"]), step=100)
                rsn = st.text_input("سبب الاستقالة", value=target["reason"])
            handover = st.text_input("حالة التسليم (Handover)", value=target.get("handover_status", ""))
            photo = st.file_uploader("الصورة الشخصية", type=["png", "jpg", "jpeg"])

            if st.form_submit_button("💾 حفظ"):
                if not e_name.strip():
                    st.error("اسم الموظف مطلوب.")
                elif l_dt < h_dt:
                    st.error("آخر يوم عمل لا يمكن أن يسبق تاريخ التعيين.")
                else:
                    p_b64 = base64.b64encode(photo.getvalue()).decode() if photo else target.get("photo_b64")
                    new_id = target["id"] if editing else (max([r["id"] for r in db], default=0) + 1)
                    rec_new = {
                        "id": new_id,
                        "recipient_name": to_english_str(rec),
                        "employee_name": to_english_str(e_name),
                        "job_title": to_english_str(j_title),
                        "branch": to_english_str(br),
                        "grading": target.get("grading", "G1"),
                        "hiring_date": h_dt, "resignation_date": r_dt, "last_working_day": l_dt,
                        "net_pay": int(pay), "reason": to_english_str(rsn),
                        "direct_manager": to_english_str(mgr),
                        "notice_period": target.get("notice_period", "One Month"),
                        "handover_status": to_english_str(handover),
                        "absence_days": 0, "loan_balance": 0, "photo_b64": p_b64,
                    }
                    if editing:
                        idx = next(i for i, x in enumerate(db) if x["id"] == target["id"])
                        db[idx] = rec_new
                    else:
                        db.insert(0, rec_new)
                    st.rerun()

# =========================================================
# TAB 4 – Analytics
# =========================================================
with tab_analytics:
    if not db:
        st.info("لا توجد بيانات.")
    else:
        df = pd.DataFrame(db)
        m1, m2, m3 = st.columns(3)
        for col, label, val in [
            (m1, "إجمالي الاستقالات", len(df)),
            (m2, "عدد الفروع", df["branch"].nunique()),
            (m3, "إجمالي المستحقات", f"{df['net_pay'].sum():,} EGP"),
        ]:
            col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{val}</div></div>', unsafe_allow_html=True)
        st.write("")
        g1, g2 = st.columns(2)
        with g1:
            st.markdown('<div class="card"><h4>الاستقالات حسب الفرع</h4></div>', unsafe_allow_html=True)
            st.bar_chart(df["branch"].value_counts(), color=C_BROWN)
        with g2:
            st.markdown('<div class="card"><h4>الاستقالات حسب السبب</h4></div>', unsafe_allow_html=True)
            st.bar_chart(df["reason"].value_counts(), color=C_ACCENT)
        st.dataframe(
            df[["employee_name", "job_title", "branch", "last_working_day", "net_pay", "reason"]],
            use_container_width=True, hide_index=True,
        )
