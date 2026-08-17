import os
import sqlite3
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import datetime
import random

app = Flask(__name__)
app.secret_key = "o2_spa_enterprise_secret_key_2026"

# جلب رابط قاعدة البيانات السحابية من متغيرات البيئة على Render، أو العمل محلياً
DATABASE_URL = os.environ.get("DATABASE_URL", "")

def get_db_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        return sqlite3.connect("o2_spa_pro.db")

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if DATABASE_URL:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY, 
                full_name TEXT NOT NULL, 
                role TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY, 
                name_ar TEXT NOT NULL, 
                name_en TEXT NOT NULL, 
                category TEXT, 
                price REAL NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY, 
                staff_id INTEGER, 
                client_name TEXT, 
                service_name TEXT, 
                service_price REAL, 
                commission REAL, 
                date TEXT, 
                time TEXT
            )
        """)
    else:
        cursor.execute("CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY, full_name TEXT NOT NULL, role TEXT NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, name_ar TEXT NOT NULL, name_en TEXT NOT NULL, category TEXT, price REAL NOT NULL)")
        cursor.execute("CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_id INTEGER, client_name TEXT, service_name TEXT, service_price REAL, commission REAL, date TEXT, time TEXT, FOREIGN KEY(staff_id) REFERENCES staff(id))")
    
    cursor.execute("SELECT COUNT(*) FROM staff")
    if cursor.fetchone()[0] == 0:
        default_staff = [
            (1001, "أسامة", "حلاق (Barber)"),
            (1002, "هشام", "حمام مغربي (Moroccan Bath)"),
            (1003, "عقيل", "مساج (Massage Therapist)")
        ]
        for s in default_staff:
            if DATABASE_URL:
                cursor.execute("INSERT INTO staff (id, full_name, role) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING", s)
            else:
                cursor.execute("INSERT OR IGNORE INTO staff (id, full_name, role) VALUES (?, ?, ?)", s)
                
    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        default_services = [
            ("حلاقة رأس", "Hair Cut", "حلاقة", 50.0),
            ("مساج عادي", "Regular Massage", "مساج", 150.0),
            ("مساج رياضي", "Sports Massage", "مساج", 200.0),
            ("حمام مغربي ذهبي", "Golden Moroccan Bath", "حمام مغربي", 450.0),
            ("جاكوزي", "Jacuzzi", "استرخاء", 50.0)
        ]
        for s in default_services:
            if DATABASE_URL:
                cursor.execute("INSERT INTO services (name_ar, name_en, category, price) VALUES (%s, %s, %s, %s)", s)
            else:
                cursor.execute("INSERT INTO services (name_ar, name_en, category, price) VALUES (?, ?, ?, ?)", s)
                
    conn.commit()
    cursor.close()
    conn.close()

init_db()

def render_page(content_html, **kwargs):
    lang = session.get('lang', 'ar')
    base_template = f"""
    <!DOCTYPE html>
    <html lang="{lang}" dir="{'rtl' if lang == 'ar' else 'ltr'}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>O2 SPA - Luxury Executive Management</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Cairo', sans-serif; background-color: #07090e; color: #f1f5f9; }}
            .gold-gradient {{ background: linear-gradient(135deg, #d4af37 0%, #aa771c 100%); }}
            .card-bg {{ background-color: #111827; border: 1px solid #1f2937; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3); }}
            .gold-text {{ color: #d4af37; }}
            .gold-border {{ border-color: #aa771c; }}
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between selection:bg-amber-500 selection:text-black">
        <header class="card-bg shadow-2xl p-4 flex justify-between items-center border-b border-gray-800 sticky top-0 z-50">
            <a href="/" class="flex items-center space-x-3 {'space-x-reverse' if lang == 'ar' else ''}">
                <div class="w-11 h-11 rounded-xl gold-gradient flex items-center justify-center font-bold text-black text-lg shadow-md overflow-hidden border border-amber-300">
                    <img src="/static/logo.jpg" alt="O2" onerror="this.style.display='none';this.parentElement.innerText='O2';" class="w-full h-full object-cover">
                </div>
                <div>
                    <h1 class="text-lg font-bold gold-text tracking-wide">O2 SPA</h1>
                    <p class="text-[10px] text-gray-400 uppercase tracking-widest">Executive Suite</p>
                </div>
            </a>
            <div class="flex items-center space-x-2 {'space-x-reverse' if lang == 'ar' else ''}">
                <a href="/" class="bg-gray-900 text-gray-300 px-3.5 py-2 rounded-xl text-xs font-semibold border border-gray-800 hover:border-amber-500 transition">{'الرئيسية' if lang == 'ar' else 'Home'}</a>
                <a href="/lang/{'en' if lang == 'ar' else 'ar'}" class="bg-gray-900 gold-text px-3.5 py-2 rounded-xl text-xs font-semibold border border-gray-800 hover:border-amber-500 transition">
                    {'English' if lang == 'ar' else 'العربية'}
                </a>
            </div>
        </header>

        <main class="container mx-auto p-4 max-w-4xl flex-grow">
            {content_html}
        </main>

        <footer class="text-center p-4 text-gray-500 text-xs border-t border-gray-800/80 card-bg mt-12">
            &copy; 2026 O2 SPA Management System. All Rights Reserved. Designed for Excellence.
        </footer>
    </body>
    </html>
    """
    return render_template_string(base_template, **kwargs)

@app.route('/lang/<string:code>')
def set_lang(code):
    session['lang'] = code
    return redirect(request.referrer or url_for('index'))

@app.route('/static/logo.jpg')
def serve_logo():
    from flask import send_file
    for filename in ["logo.jpeg", "logo.JPG", "logo.jpg", "logo"]:
        if os.path.exists(filename):
            return send_file(filename)
    return "", 404

@app.route('/')
def index():
    lang = session.get('lang', 'ar')
    content = f"""
    <div class="py-16 text-center">
        <div class="inline-block p-4 rounded-2xl gold-gradient text-black font-extrabold text-2xl mb-6 shadow-xl">O2</div>
        <h2 class="text-3xl font-bold gold-text mb-3">{'مرحباً بكم في نظام O2 SPA الفاخر' if lang == 'ar' else 'Welcome to O2 SPA System'}</h2>
        <p class="text-gray-400 mb-10 text-sm">{'يرجى اختيار بوابة الدخول الخاصة بك للمتابعة' if lang == 'ar' else 'Please select your secure portal'}</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-xl mx-auto">
            <a href="/staff-login" class="card-bg p-6 rounded-2xl shadow-xl hover:border-amber-600 transition duration-300 block text-center group">
                <div class="text-4xl mb-3 group-hover:scale-110 transition">👤</div>
                <h3 class="text-xl font-bold gold-text mb-1">{'بوابة الموظف' if lang == 'ar' else 'Staff Portal'}</h3>
                <p class="text-gray-400 text-xs">{'تسجيل الدخول برقمك التعريفي (ID)' if lang == 'ar' else 'Login via Personal ID'}</p>
            </a>
            <a href="/admin-login" class="card-bg p-6 rounded-2xl shadow-xl hover:border-amber-600 transition duration-300 block text-center group">
                <div class="text-4xl mb-3 group-hover:scale-110 transition">🛡️</div>
                <h3 class="text-xl font-bold gold-text mb-1">{'بوابة الاستقبال' if lang == 'ar' else 'Reception Portal'}</h3>
                <p class="text-gray-400 text-xs">{'الإدارة، الحجوزات، والعمولات' if lang == 'ar' else 'Management & Bookings'}</p>
            </a>
        </div>
    </div>
    """
    return render_page(content)

@app.route('/staff-login', methods=['GET', 'POST'])
def staff_login():
    lang = session.get('lang', 'ar')
    if request.method == 'POST':
        staff_id = request.form.get('staff_id', type=int)
        conn = get_db_connection()
        cursor = conn.cursor()
        if DATABASE_URL:
            cursor.execute("SELECT * FROM staff WHERE id=%s", (staff_id,))
        else:
            cursor.execute("SELECT * FROM staff WHERE id=?", (staff_id,))
        staff = cursor.fetchone()
        cursor.close()
        conn.close()
        if staff:
            session['staff_id'] = staff_id
            return redirect(url_for('staff_dashboard'))
        else:
            flash('الرقم التعريفي غير صحيح' if lang == 'ar' else 'Invalid ID', 'error')
            
    content = f"""
    <div class="max-w-md mx-auto card-bg p-8 rounded-2xl shadow-2xl mt-12 border border-gray-800">
        <h2 class="text-2xl font-bold gold-text mb-6 text-center">{'تسجيل دخول الموظف' if lang == 'ar' else 'Staff Login'}</h2>
        {{% with messages = get_flashed_messages(with_categories=true) %}}
            {{% if messages %}}
                {{% for cat, msg in messages %}}
                    <div class="bg-red-950/80 border border-red-800 text-red-200 px-4 py-3 rounded-xl mb-4 text-xs">{{{{ msg }}}}</div>
                {{% endfor %}}
            {{% endif %}}
        {{% endwith %}}
        <form method="POST" class="space-y-5">
            <div>
                <label class="block text-xs font-semibold text-gray-300 mb-2">{'أدخل الرقم التعريفي (Staff ID):' if lang == 'ar' else 'Enter Staff ID:'}</label>
                <input type="number" name="staff_id" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-white focus:border-amber-500 focus:outline-none text-sm">
            </div>
            <button type="submit" class="w-full gold-gradient text-black font-bold p-3 rounded-xl hover:opacity-90 transition text-sm shadow-lg">{'دخول للحساب' if lang == 'ar' else 'Login'}</button>
        </form>
    </div>
    """
    return render_page(content)

@app.route('/staff-dashboard')
def staff_dashboard():
    lang = session.get('lang', 'ar')
    staff_id = session.get('staff_id')
    if not staff_id:
        return redirect(url_for('staff_login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    if DATABASE_URL:
        cursor.execute("SELECT * FROM staff WHERE id=%s", (staff_id,))
        staff = cursor.fetchone()
        cursor.execute("SELECT client_name, service_name, service_price, commission, date, time FROM bookings WHERE staff_id=%s", (staff_id,))
        bookings = cursor.fetchall()
        cursor.execute("""
            SELECT staff.full_name, staff.role, COUNT(bookings.id), SUM(bookings.service_price)
            FROM bookings JOIN staff ON bookings.staff_id = staff.id
            GROUP BY staff.id, staff.full_name, staff.role ORDER BY SUM(bookings.service_price) DESC
        """)
        leaderboard = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM staff WHERE id=?", (staff_id,))
        staff = cursor.fetchone()
        cursor.execute("SELECT client_name, service_name, service_price, commission, date, time FROM bookings WHERE staff_id=?", (staff_id,))
        bookings = cursor.fetchall()
        cursor.execute("""
            SELECT staff.full_name, staff.role, COUNT(bookings.id), SUM(bookings.service_price)
            FROM bookings JOIN staff ON bookings.staff_id = staff.id
            GROUP BY staff.id ORDER BY SUM(bookings.service_price) DESC
        """)
        leaderboard = cursor.fetchall()
    cursor.close()
    conn.close()
    
    total_rev = sum([b[2] for b in bookings]) if bookings else 0
    total_comm = sum([b[3] for b in bookings]) if bookings else 0
    
    content = f"""
    <div class="space-y-6 mt-4">
        <div class="card-bg p-6 rounded-2xl flex justify-between items-center shadow-xl">
            <div>
                <h2 class="text-2xl font-bold gold-text">{{{{ staff[1] }}}}</h2>
                <p class="text-gray-400 text-xs mt-1">{{{{ staff[2] }}}} | ID: <span class="text-amber-400 font-mono font-bold">{{{{ staff[0] }}}}</span></p>
            </div>
            <a href="/staff-login" class="bg-red-950/80 border border-red-900 text-red-200 px-4 py-2 rounded-xl text-xs font-semibold hover:bg-red-900 transition">{'خروج' if lang == 'ar' else 'Logout'}</a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="card-bg p-5 rounded-xl text-center"><p class="text-gray-400 text-xs">{'عدد الزبائن' if lang == 'ar' else 'Clients'}</p><p class="text-2xl font-bold text-white mt-1">{{{{ bookings|length }}}}</p></div>
            <div class="card-bg p-5 rounded-xl text-center"><p class="text-gray-400 text-xs">{'إجمالي المدفوعات' if lang == 'ar' else 'Revenue'}</p><p class="text-2xl font-bold gold-text mt-1">{{{{ "%.2f"|format(total_rev) }}}} AED</p></div>
            <div class="card-bg p-5 rounded-xl text-center"><p class="text-gray-400 text-xs">{'أرباح عمولتك (5%)' if lang == 'ar' else 'Commission (5%)'}</p><p class="text-2xl font-bold text-emerald-400 mt-1">{{{{ "%.2f"|format(total_comm) }}}} AED</p></div>
        </div>

        <div class="card-bg p-6 rounded-2xl shadow-xl">
            <h3 class="text-lg font-bold gold-text mb-4">{'سجل خدماتك المقدمة' if lang == 'ar' else 'Your Services Record'}</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-right text-xs">
                    <thead><tr class="border-b border-gray-800 text-gray-400"><th class="pb-3">{'الزبون' if lang == 'ar' else 'Client'}</th><th class="pb-3">{'الخدمة' if lang == 'ar' else 'Service'}</th><th class="pb-3">{'السعر' if lang == 'ar' else 'Price'}</th><th class="pb-3">{'العمولة' if lang == 'ar' else 'Commission'}</th><th class="pb-3">{'التاريخ' if lang == 'ar' else 'Date'}</th></tr></thead>
                    <tbody>
                        {{% for b in bookings %}}
                        <tr class="border-b border-gray-800/40 hover:bg-gray-900/55"><td class="py-3 font-medium">{{{{ b[0] }}}}</td><td class="py-3 text-gray-300">{{{{ b[1] }}}}</td><td class="py-3 text-amber-300">{{{{ b[2] }}}} AED</td><td class="py-3 text-emerald-400 font-bold">{{{{ b[3] }}}} AED</td><td class="py-3 text-gray-400">{{{{ b[4] }}}}</td></tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card-bg p-6 rounded-2xl shadow-xl">
            <h3 class="text-lg font-bold gold-text mb-4">{'لوحة متصدرين المركز' if lang == 'ar' else 'Center Leaderboard'}</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-right text-xs">
                    <thead><tr class="border-b border-gray-800 text-gray-400"><th class="pb-3">{'الموظف' if lang == 'ar' else 'Staff'}</th><th class="pb-3">{'الوظيفة' if lang == 'ar' else 'Role'}</th><th class="pb-3">{'الخدمات' if lang == 'ar' else 'Services'}</th><th class="pb-3">{'الإيرادات' if lang == 'ar' else 'Revenue'}</th></tr></thead>
                    <tbody>
                        {{% for lb in leaderboard %}}
                        <tr class="border-b border-gray-800/40 hover:bg-gray-900/55"><td class="py-3 font-bold text-white">{{{{ lb[0] }}}}</td><td class="py-3 text-gray-400">{{{{ lb[1] }}}}</td><td class="py-3">{{{{ lb[2] }}}}</td><td class="py-3 gold-text font-bold">{{{{ lb[3] }}}} AED</td></tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """
    return render_page(content, staff=staff, bookings=bookings, leaderboard=leaderboard, total_rev=total_rev, total_comm=total_comm)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    lang = session.get('lang', 'ar')
    if request.method == 'POST':
        pwd = request.form.get('password')
        if pwd == "SpaAdmin2026#":
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('كلمة المرور غير صحيحة ( SpaAdmin2026# )' if lang == 'ar' else 'Incorrect password', 'error')
            
    content = f"""
    <div class="max-w-md mx-auto card-bg p-8 rounded-2xl shadow-2xl mt-12 border border-gray-800">
        <h2 class="text-2xl font-bold gold-text mb-6 text-center">{'دخول موظف الاستقبال' if lang == 'ar' else 'Receptionist Login'}</h2>
        {{% with messages = get_flashed_messages(with_categories=true) %}}
            {{% if messages %}}
                {{% for cat, msg in messages %}}
                    <div class="bg-red-950/80 border border-red-800 text-red-200 px-4 py-3 rounded-xl mb-4 text-xs">{{{{ msg }}}}</div>
                {{% endfor %}}
            {{% endif %}}
        {{% endwith %}}
        <form method="POST" class="space-y-5">
            <div>
                <label class="block text-xs font-semibold text-gray-300 mb-2">{'أدخل كلمة المرور السرية:' if lang == 'ar' else 'Enter Secret Password:'}</label>
                <input type="password" name="password" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-white focus:border-amber-500 focus:outline-none text-sm">
            </div>
            <button type="submit" class="w-full gold-gradient text-black font-bold p-3 rounded-xl hover:opacity-90 transition text-sm shadow-lg">{'دخول لوحة التحكم' if lang == 'ar' else 'Access Admin Panel'}</button>
        </form>
    </div>
    """
    return render_page(content)

@app.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    lang = session.get('lang', 'ar')
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST' and 'add_booking' in request.form:
        client = request.form.get('client_name')
        staff_id = request.form.get('staff_id', type=int)
        service_name = request.form.get('service_name')
        price = request.form.get('price', type=float)
        comm = price * 0.05
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        time_str = datetime.datetime.now().strftime("%H:%M")
        if DATABASE_URL:
            cursor.execute("INSERT INTO bookings (staff_id, client_name, service_name, service_price, commission, date, time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                         (staff_id, client, service_name, price, comm, date_str, time_str))
        else:
            cursor.execute("INSERT INTO bookings (staff_id, client_name, service_name, service_price, commission, date, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (staff_id, client, service_name, price, comm, date_str, time_str))
        conn.commit()
        
    if request.method == 'POST' and 'add_staff' in request.form:
        s_name = request.form.get('staff_name')
        s_role = request.form.get('staff_role')
        new_id = random.randint(1000, 9999)
        try:
            if DATABASE_URL:
                cursor.execute("INSERT INTO staff (id, full_name, role) VALUES (%s, %s, %s)", (new_id, s_name, s_role))
            else:
                cursor.execute("INSERT INTO staff (id, full_name, role) VALUES (?, ?, ?)", (new_id, s_name, s_role))
            conn.commit()
        except:
            pass

    # خاصية حذف موظف باحترافية
    if request.method == 'POST' and 'delete_staff' in request.form:
        s_id = request.form.get('staff_id', type=int)
        try:
            if DATABASE_URL:
                cursor.execute("DELETE FROM bookings WHERE staff_id=%s", (s_id,))
                cursor.execute("DELETE FROM staff WHERE id=%s", (s_id,))
            else:
                cursor.execute("DELETE FROM bookings WHERE staff_id=?", (s_id,))
                cursor.execute("DELETE FROM staff WHERE id=?", (s_id,))
            conn.commit()
        except:
            pass
            
    if request.method == 'POST' and 'delete_booking' in request.form:
        b_id = request.form.get('booking_id', type=int)
        if DATABASE_URL:
            cursor.execute("DELETE FROM bookings WHERE id=%s", (b_id,))
        else:
            cursor.execute("DELETE FROM bookings WHERE id=?", (b_id,))
        conn.commit()

    if DATABASE_URL:
        cursor.execute("SELECT * FROM staff")
        staff_list = cursor.fetchall()
        cursor.execute("SELECT * FROM services")
        services_list = cursor.fetchall()
        cursor.execute("""
            SELECT bookings.id, bookings.client_name, staff.full_name, bookings.service_name, bookings.service_price, bookings.commission, bookings.date 
            FROM bookings JOIN staff ON bookings.staff_id = staff.id
        """)
        bookings_list = cursor.fetchall()
        cursor.execute("""
            SELECT staff.id, staff.full_name, staff.role, COUNT(bookings.id), SUM(bookings.service_price), SUM(bookings.commission)
            FROM bookings JOIN staff ON bookings.staff_id = staff.id
            GROUP BY staff.id, staff.full_name, staff.role ORDER BY SUM(bookings.service_price) DESC
        """)
        leaderboard = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM staff")
        staff_list = cursor.fetchall()
        cursor.execute("SELECT * FROM services")
        services_list = cursor.fetchall()
        cursor.execute("""
            SELECT bookings.id, bookings.client_name, staff.full_name, bookings.service_name, bookings.service_price, bookings.commission, bookings.date 
            FROM bookings JOIN staff ON bookings.staff_id = staff.id
        """)
        bookings_list = cursor.fetchall()
        cursor.execute("""
            SELECT staff.id, staff.full_name, staff.role, COUNT(bookings.id), SUM(bookings.service_price), SUM(bookings.commission)
            FROM bookings JOIN staff ON bookings.staff_id = staff.id
            GROUP BY staff.id ORDER BY SUM(bookings.service_price) DESC
        """)
        leaderboard = cursor.fetchall()
        
    cursor.close()
    conn.close()

    content = f"""
    <div class="space-y-8 mt-4">
        <div class="card-bg p-6 rounded-2xl flex justify-between items-center shadow-xl">
            <h2 class="text-2xl font-bold gold-text">{'لوحة تحكم موظف الاستقبال' if lang == 'ar' else 'Receptionist Control Panel'}</h2>
            <a href="/" class="bg-red-950/80 border border-red-900 text-red-200 px-4 py-2 rounded-xl text-xs font-semibold hover:bg-red-900 transition">{'خروج' if lang == 'ar' else 'Logout'}</a>
        </div>

        <div class="card-bg p-6 rounded-2xl shadow-xl">
            <h3 class="text-lg font-bold gold-text mb-4">{'➕ تسجيل خدمة جديدة وتوزيعها' if lang == 'ar' else '➕ Register New Service'}</h3>
            <form method="POST" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input type="hidden" name="add_booking" value="1">
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1.5">{'اسم الزبون:' if lang == 'ar' else 'Client Name:'}</label>
                    <input type="text" name="client_name" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-white text-sm focus:border-amber-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1.5">{'الموظف المسؤول:' if lang == 'ar' else 'Assigned Staff:'}</label>
                    <select name="staff_id" class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-white text-sm focus:border-amber-500 focus:outline-none">
                        {{% for s in staff_list %}}
                        <option value="{{{{ s[0] }}}}">{{{{ s[1] }}}} ({{{{ s[2] }}}})</option>
                        {{% endfor %}}
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1.5">{'اسم الخدمة:' if lang == 'ar' else 'Service Name:'}</label>
                    <input type="text" name="service_name" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-white text-sm focus:border-amber-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-300 mb-1.5">{'مبلغ الدفع (AED):' if lang == 'ar' else 'Price (AED):'}</label>
                    <input type="number" step="0.1" name="price" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-white text-sm focus:border-amber-500 focus:outline-none">
                </div>
                <div class="md:col-span-2 pt-2">
                    <button type="submit" class="w-full gold-gradient text-black font-bold p-3.5 rounded-xl text-sm shadow-lg hover:opacity-90 transition">{'حفظ الخدمة وحساب 5%' if lang == 'ar' else 'Save & Calculate 5%'}</button>
                </div>
            </form>
        </div>

        <div class="card-bg p-6 rounded-2xl shadow-xl">
            <h3 class="text-lg font-bold gold-text mb-4">{'🏆 لوحة المتصدرين والعمولات' if lang == 'ar' else '🏆 Leaderboard & Commissions'}</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-right text-xs">
                    <thead><tr class="border-b border-gray-800 text-gray-400"><th class="pb-3">ID</th><th class="pb-3">{'الموظف' if lang == 'ar' else 'Staff'}</th><th class="pb-3">{'الخدمات' if lang == 'ar' else 'Services'}</th><th class="pb-3">{'الإيرادات' if lang == 'ar' else 'Revenue'}</th><th class="pb-3">{'عمولة 5%' if lang == 'ar' else 'Commission'}</th></tr></thead>
                    <tbody>
                        {{% for lb in leaderboard %}}
                        <tr class="border-b border-gray-800/40 hover:bg-gray-900/55"><td class="py-3 font-mono text-amber-400">{{{{ lb[0] }}}}</td><td class="py-3 font-bold text-white">{{{{ lb[1] }}}}</td><td class="py-3">{{{{ lb[3] }}}}</td><td class="py-3 gold-text font-bold">{{{{ lb[4] }}}} AED</td><td class="py-3 text-emerald-400 font-bold">{{{{ lb[5] }}}} AED</td></tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="card-bg p-6 rounded-2xl shadow-xl">
                <h3 class="text-lg font-bold gold-text mb-4">{'👥 إضافة موظف جديد' if lang == 'ar' else '👥 Add New Staff'}</h3>
                <form method="POST" class="space-y-4">
                    <input type="hidden" name="add_staff" value="1">
                    <input type="text" name="staff_name" placeholder="{'الاسم الكامل' if lang == 'ar' else 'Full Name'}" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-white text-sm focus:border-amber-500 focus:outline-none">
                    <input type="text" name="staff_role" placeholder="{'المسمى الوظيفي' if lang == 'ar' else 'Role'}" required class="w-full bg-gray-950 border border-gray-800 rounded-xl p-3 text-white text-sm focus:border-amber-500 focus:outline-none">
                    <button type="submit" class="w-full bg-gray-900 gold-text border border-amber-600 font-bold p-3 rounded-xl text-sm hover:bg-gray-800 transition">{'تسجيل وتوليد ID' if lang == 'ar' else 'Register & Generate ID'}</button>
                </form>
            </div>
            
            <div class="card-bg p-6 rounded-2xl shadow-xl">
                <h3 class="text-lg font-bold gold-text mb-4">{'📋 قائمة طاقم العمل والحذف' if lang == 'ar' else '📋 Staff Management'}</h3>
                <div class="space-y-2.5 max-h-52 overflow-y-auto pr-1">
                    {{% for s in staff_list %}}
                    <div class="flex justify-between items-center bg-gray-950 p-3 rounded-xl text-xs border border-gray-800/80">
                        <div>
                            <span class="font-bold text-white">{{{{ s[1] }}}}</span>
                            <span class="text-gray-400 block text-[10px] mt-0.5">{{{{ s[2] }}}}}}</span>
                        </div>
                        <div class="flex items-center space-x-2 {'space-x-reverse' if lang == 'ar' else ''}">
                            <span class="text-amber-400 font-mono font-bold">ID: {{{{ s[0] }}}}</span>
                            <form method="POST" onsubmit="return confirm('هل أنت متأكد من حذف هذا الموظف؟');" class="inline">
                                <input type="hidden" name="delete_staff" value="1">
                                <input type="hidden" name="staff_id" value="{{{{ s[0] }}}}">
                                <button type="submit" class="bg-red-950 text-red-300 border border-red-900 px-2 py-1 rounded-lg text-[10px] hover:bg-red-900 transition">{'حذف' if lang == 'ar' else 'Delete'}</button>
                            </form>
                        </div>
                    </div>
                    {{% endfor %}}
                </div>
            </div>
        </div>

        <div class="card-bg p-6 rounded-2xl shadow-xl">
            <h3 class="text-lg font-bold gold-text mb-4">{'🗑️ سجل المعاملات الحية' if lang == 'ar' else '🗑️ Live Transactions Log'}</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-right text-xs">
                    <thead><tr class="border-b border-gray-800 text-gray-400"><th class="pb-3">ID</th><th class="pb-3">{'الزبون' if lang == 'ar' else 'Client'}</th><th class="pb-3">{'الموظف' if lang == 'ar' else 'Staff'}</th><th class="pb-3">{'الخدمة' if lang == 'ar' else 'Service'}</th><th class="pb-3">{'السعر' if lang == 'ar' else 'Price'}</th><th class="pb-3">{'الإجراء' if lang == 'ar' else 'Action'}</th></tr></thead>
                    <tbody>
                        {{% for bk in bookings_list %}}
                        <tr class="border-b border-gray-800/40 hover:bg-gray-900/55">
                            <td class="py-3 font-mono text-gray-400">{{{{ bk[0] }}}}</td>
                            <td class="py-3 font-medium text-white">{{{{ bk[1] }}}}</td>
                            <td class="py-3 text-gray-300">{{{{ bk[2] }}}}</td>
                            <td class="py-3 text-gray-300">{{{{ bk[3] }}}}</td>
                            <td class="py-3 gold-text font-bold">{{{{ bk[4] }}}} AED</td>
                            <td class="py-3">
                                <form method="POST" onsubmit="return confirm('هل أنت متأكد من حذف هذا السجل؟');">
                                    <input type="hidden" name="delete_booking" value="1">
                                    <input type="hidden" name="booking_id" value="{{{{ bk[0] }}}}">
                                    <button type="submit" class="bg-red-950 text-red-300 border border-red-900 px-2.5 py-1 rounded-lg text-[10px] hover:bg-red-900 transition">{'حذف' if lang == 'ar' else 'Delete'}</button>
                                </form>
                            </td>
                        </tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    """
    return render_page(content, staff_list=staff_list, services_list=services_list, bookings_list=bookings_list, leaderboard=leaderboard)

if __name__ == '__main__':
    app.run(debug=True, port=5000)