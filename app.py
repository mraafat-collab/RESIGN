import streamlit as st
import pandas as pd
from datetime import date
import streamlit.components.v1 as components
import base64
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from docx import Document

# ---------------------------------------------------------
# FIXED SENDER CREDENTIALS
# ---------------------------------------------------------
DEFAULT_SENDER_EMAIL = "m.raafat@mojoefood.com"
DEFAULT_SENDER_PASSWORD = "gnpa2b6kXBPKi53"

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Corporate Resignation Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Ultimate Futuristic UI/UX Styling (Glassmorphism & Gold/Dark Theme)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background: #0F172A;
        color: #F8FAFC;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    }

    /* Top Navigation Pills */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 41, 59, 0.7);
        padding: 8px;
        border-radius: 16px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent;
        border-radius: 12px;
        color: #94A3B8;
        font-weight: 700;
        font-size: 14px;
        border: none;
        padding: 0px 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #F1F5F9;
        background: rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0px 4px 20px rgba(217, 119, 6, 0.4) !important;
    }

    /* Glass Cards Wrapper */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    
    /* Custom Metric Styling */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #F59E0B !important;
    }

    /* Primary Buttons Styling */
    .stButton>button {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
        color: white;
        font-weight: 700;
        border-radius: 12px;
        border: none;
        padding: 12px 28px;
        box-shadow: 0 4px 14px 0 rgba(217, 119, 6, 0.39);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(217, 119, 6, 0.55);
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    }
</style>
""", unsafe_allow_html=True)

# Helper Function
def to_english_str(text):
    if not text:
        return ""
    arabic_num = "٠١٢٣٤٥٦٧٨٩"
    english_num = "0123456789"
    trans = str.maketrans(arabic_num, english_num)
    return str(text).translate(trans)

# Helper for Word (.docx)
def generate_word_doc(data, exp_days):
    doc = Document()
    doc.add_heading(f"RESIGNATION APPROVAL REQUEST - {data['employee_name']}", 0)
    doc.add_paragraph(f"Recipient: Dear {data.get('recipient_name', 'Manager')}")
    doc.add_paragraph(f"Employee Name: {data['employee_name']}")
    doc.add_paragraph(f"Job Title: {data['job_title']}")
    doc.add_paragraph(f"Branch: {data['branch']}")
    doc.add_paragraph(f"Hiring Date: {data['hiring_date'].strftime('%d/%m/%Y')}")
    doc.add_paragraph(f"Resignation Date: {data['resignation_date'].strftime('%d/%m/%Y')}")
    doc.add_paragraph(f"Last Working Day: {data['last_working_day'].strftime('%d/%m/%Y')}")
    doc.add_paragraph(f"Total Experience: {exp_days} Days")
    doc.add_paragraph(f"Total Net Pay: {data['net_pay']} EGP")
    doc.add_paragraph(f"Reason for Leaving: {data['reason']}")
    doc.add_paragraph(f"Direct Manager: {data['direct_manager']}")
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# Helper for Excel (.xlsx)
def generate_excel(data, exp_days):
    df_single = pd.DataFrame([{
        "Recipient Name": data.get('recipient_name', ''),
        "Employee Name": data['employee_name'],
        "Branch": data['branch'],
        "Job Title": data['job_title'],
        "Hiring Date": data['hiring_date'].strftime('%Y-%m-%d'),
        "Resignation Date": data['resignation_date'].strftime('%Y-%m-%d'),
        "Last Working Day": data['last_working_day'].strftime('%Y-%m-%d'),
        "Total Experience (Days)": exp_days,
        "Total Net Pay (EGP)": data['net_pay'],
        "Reason": data['reason'],
        "Direct Manager": data['direct_manager']
    }])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_single.to_excel(writer, index=False, sheet_name='Resignation')
    return output.getvalue()

# Database Initialization
if 'resignations_db' not in st.session_state:
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
            "photo_b64": None
        }
    ]

# ---------------------------------------------------------
# Sidebar - Quick Selector & Master Control
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/3d-fluency/94/corporate-user.png", width=70)
    st.title("بوابة الاستقالات")
    st.caption("نظام الإدارة المركزي الموحد 2026")
    st.markdown("---")
    
    if st.session_state.resignations_db:
        emp_options = {r['id']: f"{r['employee_name']} ({r['branch']})" for r in st.session_state.resignations_db}
        selected_id = st.selectbox("🎯 اختر الموظف الحالي:", options=list(emp_options.keys()), format_func=lambda x: emp_options[x])
        data = next(item for item in st.session_state.resignations_db if item["id"] == selected_id)
    else:
        data = None

    st.markdown("---")
    st.success(f"⚡ إيميل النظام المعتمد:\n`{DEFAULT_SENDER_EMAIL}`")

# ---------------------------------------------------------
# Top Navigation Tabs
# ---------------------------------------------------------
tab_hub, tab_manage, tab_analytics = st.tabs([
    "🚀 مركز التحكم والتقرير A4", 
    "⚙️ إدارة وتعديل البيانات", 
    "📊 التحليلات والداشبورد"
])

# ---------------------------------------------------------
# TAB 1: ALL-IN-ONE CONTROL HUB
# ---------------------------------------------------------
with tab_hub:
    if not data:
        st.warning("⚠️ لا توجد بيانات استقالات مسجلة حالياً.")
    else:
        exp_days = max((data['last_working_day'] - data['hiring_date']).days, 0)
        h_date = data['hiring_date'].strftime("%d/%m/%Y")
        r_date = data['resignation_date'].strftime("%d/%m/%Y")
        l_date = data['last_working_day'].strftime("%d/%m/%Y")
        
        recipient = data.get('recipient_name', 'Manager').strip()
        recipient_title = recipient if recipient.lower().startswith(("mr.", "ms.")) else f"Mr. {recipient}"

        # Top Control Row (Smart Actions)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col_act1, col_act2, col_act3, col_act4 = st.columns([2, 2, 3, 1])
        
        with col_act1:
            st.download_button("📄 تصدير Word (.docx)", generate_word_doc(data, exp_days), f"Resignation_{data['employee_name']}.docx", use_container_width=True)
        with col_act2:
            st.download_button("📊 تصدير Excel (.xlsx)", generate_excel(data, exp_days), f"Resignation_{data['employee_name']}.xlsx", use_container_width=True)
        with col_act3:
            st.info(f"👤 الموظف المعروض: **{data['employee_name']}**")
        with col_act4:
            st.metric("الخبرة", f"{exp_days} يوم")
            
        st.markdown('</div>', unsafe_allow_html=True)

        # Split View: Left Email Panel, Right Integrated Preview
        c_left, c_right = st.columns([1, 2])

        with c_left:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("✉️ إرسال بريد الكتروني مباشر")
            st.caption("يتم الإرسال تلقائياً عبر سيرفر الشركة")
            
            to_email = st.text_input("إلى (Main Receiver):", placeholder="recipient@company.com", key="hub_to")
            cc_email = st.text_input("نسخة كربونية (CC):", placeholder="manager@company.com", key="hub_cc")
            smtp_server = st.text_input("سيرفر SMTP:", value="smtp.office365.com", key="hub_smtp")

            if st.button("🚀 إرسال التقرير الآن"):
                if to_email:
                    try:
                        msg = MIMEMultipart('alternative')
                        msg['Subject'] = f"Resignation Approval Request - {data['employee_name']}"
                        msg['From'] = DEFAULT_SENDER_EMAIL
                        msg['To'] = to_email.strip()
                        
                        recipients = [to_email.strip()]
                        if cc_email.strip():
                            msg['Cc'] = cc_email.strip()
                            recipients.append(cc_email.strip())

                        email_html = f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; background:#F8F6F0; padding:20px;">
                            <div style="background:#FAF8F5; border:1px solid #D6C2A7; padding:20px; border-radius:10px; max-width:600px; margin:auto;">
                                <h3 style="color:#8C5A2B;">Dear {recipient_title},</h3>
                                <h2 style="color:#8C5A2B;">RESIGNATION APPROVAL REQUEST</h2>
                                <hr style="border:1px solid #EADBCE;">
                                <p><b>Employee Name:</b> {data['employee_name']}</p>
                                <p><b>Branch:</b> {data['branch']}</p>
                                <p><b>Job Title:</b> {data['job_title']}</p>
                                <p><b>Last Working Day:</b> {l_date}</p>
                                <p><b>Total Net Pay:</b> {data['net_pay']} EGP</p>
                            </div>
                        </body>
                        </html>
                        """
                        msg.attach(MIMEText(email_html, 'html'))
                        
                        server = smtplib.SMTP(smtp_server.strip(), 587, timeout=12)
                        server.ehlo()
                        server.starttls()
                        server.login(DEFAULT_SENDER_EMAIL, DEFAULT_SENDER_PASSWORD)
                        server.sendmail(DEFAULT_SENDER_EMAIL, recipients, msg.as_string())
                        server.quit()
                        
                        st.success("✅ تم الإرسال بنجاح!")
                    except Exception as e:
                        st.error(f"❌ فشل الإرسال: {e}")
                else:
                    st.error("يرجى كتابة إيميل المستلم.")
            st.markdown('</div>', unsafe_allow_html=True)

        with c_right:
            # Render HTML Card Component & Canvas Print Scripts
            if data.get('photo_b64'):
                img_html = f'<img src="data:image/png;base64,{data["photo_b64"]}" style="width:100px; height:130px; border-radius:8px; object-fit:cover; border:1px solid #D6C2A7;" />'
            else:
                img_html = '<div style="width:100px; height:130px; background:#EADBCE; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:36px; border:1px solid #D6C2A7;">👤</div>'

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
                    body {{ font-family: 'Inter', sans-serif; background: transparent; margin: 0; padding: 0; }}
                    .a4-card {{ background-color: #FAF8F5; border: 1.5px solid #D6C2A7; border-radius: 12px; padding: 22px; margin: 0 auto; }}
                    .custom-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; border: 1px solid #D6C2A7; }}
                    .custom-table th {{ background-color: #8C5A2B; color: white; padding: 6px 10px; text-align: left; font-size: 12px; }}
                    .custom-table td {{ padding: 5px 10px; border-bottom: 1px solid #EADBCE; font-size: 12px; color: #222; }}
                    .custom-table tr:nth-child(even) {{ background-color: #FAF8F5; }}
                    .metric-badge {{ background-color: #8C5A2B; color: white; border-radius: 12px; padding: 4px; text-align: center; font-size: 10px; font-weight:700; }}
                    .metric-box {{ background-color: #FAF8F5; border: 1px solid #D6C2A7; border-radius: 6px; padding: 5px; text-align: center; font-weight: 800; font-size: 12px; }}
                    .action-btn {{ background-color: #8C5A2B; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: bold; cursor: pointer; }}
                </style>
            </head>
            <body>
                <div style="display:flex; justify-content:flex-end; gap:8px; margin-bottom:10px;">
                    <button onclick="downloadAsImage()" class="action-btn">🖼️ تنزيل صورة PNG</button>
                    <button onclick="window.print()" class="action-btn">🖨️ طباعة A4</button>
                </div>
                <div id="capture-card" class="a4-card">
                    <table style="width:100%; border:none;">
                        <tr>
                            <td style="width:60%; vertical-align:top; border:none;">
                                <div style="color:#8C5A2B; font-size:15px; font-weight:700;">Dear {recipient_title},</div>
                                <div style="color:#8C5A2B; font-weight:800; font-size:22px;">RESIGNATION<br>APPROVAL REQUEST</div>
                            </td>
                            <td style="width:40%; vertical-align:top; border:none;">
                                <div style="display:flex; gap:10px; align-items:center;">
                                    {img_html}
                                    <div>
                                        <div style="font-size:15px; font-weight:800; color:#111;">{data['employee_name']}</div>
                                        <div style="font-size:12px; color:#555;">{data['job_title']}</div>
                                        <div style="font-size:11px; color:#777;">{data['branch']}</div>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </table>
                    <div style="display:flex; gap:6px; margin-top:12px;">
                        <div style="flex:1;"><div class="metric-badge">Net Pay</div><div class="metric-box">{data["net_pay"]} EGP</div></div>
                        <div style="flex:1;"><div class="metric-badge">Last Work Day</div><div class="metric-box">{l_date}</div></div>
                        <div style="flex:1;"><div class="metric-badge">Manager</div><div class="metric-box">{data["direct_manager"]}</div></div>
                    </div>
                    <table class="custom-table">
                        <thead><tr><th>Field</th><th>Details</th></tr></thead>
                        <tbody>
                            <tr><td>Employee Name</td><td><b>{data['employee_name']}</b></td></tr>
                            <tr><td>Branch</td><td>{data['branch']}</td></tr>
                            <tr><td>Hiring Date</td><td>{h_date}</td></tr>
                            <tr><td>Resignation Date</td><td>{r_date}</td></tr>
                            <tr><td>Last Working Day</td><td>{l_date}</td></tr>
                            <tr><td>Total Experience</td><td>{exp_days} Days</td></tr>
                            <tr><td>Reason for Leaving</td><td>{data['reason']}</td></tr>
                            <tr><td>Handover Status</td><td>{data['handover_status']}</td></tr>
                        </tbody>
                    </table>
                </div>
                <script>
                    function downloadAsImage() {{
                        html2canvas(document.getElementById("capture-card"), {{ scale: 2 }}).then(canvas => {{
                            const link = document.createElement("a");
                            link.download = "Resignation_{data['employee_name']}.png";
                            link.href = canvas.toDataURL("image/png");
                            link.click();
                        }});
                    }}
                </script>
            </body>
            </html>
            """
            components.html(html_content, height=650, scrolling=True)

# ---------------------------------------------------------
# TAB 2: DATA MANAGEMENT
# ---------------------------------------------------------
with tab_manage:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("⚙️ إدارة واستحداث بيانات الاستقالة")
    
    action = st.radio("نوع العملية:", ["إضافة استقالة جديدة ➕", "تعديل الاستقالة الحالية ✏️", "حذف استقالة 🗑️"], horizontal=True)

    if action == "حذف استقالة 🗑️":
        if st.session_state.resignations_db:
            if st.button("❌ تأكيد الحذف النهائي"):
                st.session_state.resignations_db = [r for r in st.session_state.resignations_db if r['id'] != selected_id]
                st.success("تم الحذف بنجاح!")
                st.rerun()
    else:
        target = data if (action == "تعديل الاستقالة الحالية ✏️" and data) else {
            "id": None, "recipient_name": "", "employee_name": "", "job_title": "",
            "branch": "", "grading": "", "hiring_date": date.today(),
            "resignation_date": date.today(), "last_working_day": date.today(),
            "net_pay": 0, "reason": "", "direct_manager": "", "notice_period": "",
            "handover_status": "", "absence_days": 0, "loan_balance": 0, "photo_b64": None
        }

        with st.form("manage_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_name = to_english_str(st.text_input("اسم الموظف:", value=target['employee_name']))
                j_title = to_english_str(st.text_input("المسمى الوظيفي:", value=target['job_title']))
                br = to_english_str(st.text_input("الفرع:", value=target['branch']))
                rec_name = to_english_str(st.text_input("الموجه له الطلب (Recipient):", value=target.get('recipient_name', '')))
                mgr = to_english_str(st.text_input("المدير المباشر:", value=target['direct_manager']))
            with c2:
                h_dt = st.date_input("تاريخ التعيين:", value=target['hiring_date'])
                r_dt = st.date_input("تاريخ الاستقالة:", value=target['resignation_date'])
                l_dt = st.date_input("آخر يوم عمل:", value=target['last_working_day'])
                pay = st.number_input("إجمالي المستحقات (EGP):", value=int(target['net_pay']))
                rsn = to_english_str(st.text_input("سبب الاستقالة:", value=target['reason']))
                
            photo = st.file_uploader("الصورة الشخصية (4x6):", type=["png", "jpg"])
            
            if st.form_submit_button("💾 حفظ وحفظ التعديلات"):
                p_b64 = base64.b64encode(photo.getvalue()).decode() if photo else target.get('photo_b64')
                new_rec = {
                    "id": target['id'] if target['id'] else len(st.session_state.resignations_db) + 1,
                    "recipient_name": rec_name, "employee_name": e_name, "job_title": j_title,
                    "branch": br, "grading": "G1", "hiring_date": h_dt, "resignation_date": r_dt,
                    "last_working_day": l_dt, "net_pay": pay, "reason": rsn, "direct_manager": mgr,
                    "notice_period": "One Month", "handover_status": "Completed",
                    "absence_days": 0, "loan_balance": 0, "photo_b64": p_b64
                }
                if action == "تعديل الاستقالة الحالية ✏️" and target['id']:
                    idx = next(i for i, item in enumerate(st.session_state.resignations_db) if item["id"] == target['id'])
                    st.session_state.resignations_db[idx] = new_rec
                else:
                    st.session_state.resignations_db.insert(0, new_rec)
                st.success("تم الحفظ بنجاح!")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: DASHBOARD ANALYTICS
# ---------------------------------------------------------
with tab_analytics:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 الداشبورد والتحليلات الإحصائية")
    if st.session_state.resignations_db:
        df = pd.DataFrame(st.session_state.resignations_db)
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي الاستقالات", len(df))
        m2.metric("عدد الفروع", df['branch'].nunique())
        m3.metric("إجمالي المستحقات", f"{df['net_pay'].sum():,} EGP")
        st.markdown("---")
        st.bar_chart(df['branch'].value_counts())
    st.markdown('</div>', unsafe_allow_html=True)
