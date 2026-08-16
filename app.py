import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import datetime
import random

app = Flask(__name__)
app.secret_key = "o2_spa_secret_key_2026"

def init_db():
    conn = sqlite3.connect("o2_spa_pro.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY, full_name TEXT NOT NULL, role TEXT NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY AUTOINCREMENT, name_ar TEXT NOT NULL, name_en TEXT NOT NULL, category TEXT, price REAL NOT NULL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_id INTEGER, client_name TEXT, service_name TEXT, service_price REAL, commission REAL, date TEXT, time TEXT, FOREIGN KEY(staff_id) REFERENCES staff(id))")
    
    cursor.execute("SELECT COUNT(*) FROM staff")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO staff (id, full_name, role) VALUES (?, ?, ?)", [
            (1001, "أسامة", "حلاق (Barber)"),
            (1002, "هشام", "حمام مغربي (Moroccan Bath)"),
            (1003, "عقيل", "مساج (Massage Therapist)")
        ])
    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO services (name_ar, name_en, category, price) VALUES (?, ?, ?, ?)", [
            ("حلاقة رأس", "Hair Cut", "حلاقة", 50.0),
            ("مساج عادي", "Regular Massage", "مساج", 150.0),
            ("مساج رياضي", "Sports Massage", "مساج", 200.0),
            ("حمام مغربي ذهبي", "Golden Moroccan Bath", "حمام مغربي", 450.0),
            ("جاكوزي", "Jacuzzi", "استرخاء", 50.0)
        ])
    conn.commit()
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
        <title>O2 SPA - Enterprise System</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Cairo', sans-serif; background-color: #0b0f19; color: #f8fafc; }}
            .gold-gradient {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }}
            .card-bg {{ background-color: #111827; border: 1px solid #1f2937; }}
        </style>
    </head>
    <body class="min-h-screen flex flex-col justify-between">
        <header class="card-bg shadow-lg p-4 flex justify-between items-center border-b border-gray-800">
            <a href="/" class="flex items-center space-x-3 {'space-x-reverse' if lang == 'ar' else ''}">
                <div class="w-10 h-10 rounded-full gold-gradient flex items-center justify-center font-bold text-black text-lg">O2</div>
                <div>
                    <h1 class="text-lg font-bold text-amber-400">O2 SPA</h1>
                    <p class="text-xs text-gray-400">Executive Suite</p>
                </div>
            </a>
            <div class="flex items-center space-x-2 {'space-x-reverse' if lang == 'ar' else ''}">
                <a href="/" class="bg-gray-800 text-gray-300 px-3 py-1.5 rounded-lg text-sm font-semibold border border-gray-700 hover:bg-gray-700">{'الرئيسية' if lang == 'ar' else 'Home'}</a>
                <a href="/lang/{'en' if lang == 'ar' else 'ar'}" class="bg-gray-800 text-amber-400 px-3 py-1.5 rounded-lg text-sm font-semibold border border-gray-700 hover:bg-gray-700">
                    {'English' if lang == 'ar' else 'العربية'}
                </a>
            </div>
        </header>

        <main class="container mx-auto p-4 max-w-4xl flex-grow">
            {content_html}
        </main>

        <footer class="text-center p-4 text-gray-500 text-xs border-t border-gray-800 card-bg mt-8">
            &copy; 2026 O2 SPA Management System. All Rights Reserved.
        </footer>
    </body>
    </html>
    """
    return render_template_string(base_template, **kwargs)

@app.route('/lang/<string:code>')
def set_lang(code):
    session['lang'] = code
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    lang = session.get('lang', 'ar')
    content = f"""
    <div class="py-12 text-center">
        <h2 class="text-3xl font-bold text-amber-400 mb-4">{'مرحباً بكم في نظام O2 SPA الفاخر' if lang == 'ar' else 'Welcome to O2 SPA System'}</h2>
        <p class="text-gray-400 mb-8">{'يرجى اختيار بوابة الدخول المناسبة لك' if lang == 'ar' else 'Please select your portal'}</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-xl mx-auto">
            <a href="/staff-login" class="card-bg p-6 rounded-2xl shadow-xl hover:border-amber-500 transition duration-300 block text-center">
                <div class="text-4xl mb-3">👤</div>
                <h3 class="text-xl font-bold text-amber-400 mb-2">{'بوابة الموظف' if lang == 'ar' else 'Staff Portal'}</h3>
                <p class="text-gray-400 text-sm">{'تسجيل الدخول بالرقم التعريفي (ID)' if lang == 'ar' else 'Login via Personal ID'}</p>
            </a>
            <a href="/admin-login" class="card-bg p-6 rounded-2xl shadow-xl hover:border-amber-500 transition duration-300 block text-center">
                <div class="text-4xl mb-3">🛡️</div>
                <h3 class="text-xl font-bold text-amber-400 mb-2">{'بوابة الاستقبال' if lang == 'ar' else 'Reception Portal'}</h3>
                <p class="text-gray-400 text-sm">{'الإدارة، الحجوزات، والعمولات' if lang == 'ar' else 'Management & Bookings'}</p>
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
        conn = sqlite3.connect("o2_spa_pro.db")
        staff = conn.execute("SELECT * FROM staff WHERE id=?", (staff_id,)).fetchone()
        conn.close()
        if staff:
            session['staff_id'] = staff_id
            return redirect(url_for('staff_dashboard'))
        else:
            flash('الرقم التعريفي غير صحيح' if lang == 'ar' else 'Invalid ID', 'error')
            
    content = f"""
    <div class="max-w-md mx-auto card-bg p-8 rounded-2xl shadow-xl mt-10">
        <h2 class="text-2xl font-bold text-amber-400 mb-6 text-center">{'تسجيل دخول الموظف' if lang == 'ar' else 'Staff Login'}</h2>
        {{% with messages = get_flashed_messages(with_categories=true) %}}
            {{% if messages %}}
                {{% for cat, msg in messages %}}
                    <div class="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-4 text-sm">{{{{ msg }}}}</div>
                {{% endfor %}}
            {{% endif %}}
        {{% endwith %}}
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm text-gray-300 mb-2">{'أدخل الرقم التعريفي (Staff ID):' if lang == 'ar' else 'Enter Staff ID:'}</label>
                <input type="number" name="staff_id" required class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:border-amber-500 focus:outline-none">
            </div>
            <button type="submit" class="w-full gold-gradient text-black font-bold p-3 rounded-lg hover:opacity-90 transition">{'دخول للحساب' if lang == 'ar' else 'Login'}</button>
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
        
    conn = sqlite3.connect("o2_spa_pro.db")
    staff = conn.execute("SELECT * FROM staff WHERE id=?", (staff_id,)).fetchone()
    bookings = conn.execute("SELECT client_name, service_name, service_price, commission, date, time FROM bookings WHERE staff_id=?", (staff_id,)).fetchall()
    leaderboard = conn.execute("""
        SELECT staff.full_name, staff.role, COUNT(bookings.id), SUM(bookings.service_price)
        FROM bookings JOIN staff ON bookings.staff_id = staff.id
        GROUP BY staff.id ORDER BY SUM(bookings.service_price) DESC
    """).fetchall()
    conn.close()
    
    total_rev = sum([b[2] for b in bookings]) if bookings else 0
    total_comm = sum([b[3] for b in bookings]) if bookings else 0
    
    content = f"""
    <div class="space-y-6 mt-6">
        <div class="card-bg p-6 rounded-2xl flex justify-between items-center">
            <div>
                <h2 class="text-2xl font-bold text-amber-400">{{{{ staff[1] }}}}</h2>
                <p class="text-gray-400 text-sm">{{{{ staff[2] }}}} (ID: {{{{ staff[0] }}}})</p>
            </div>
            <a href="/staff-login" class="bg-red-900 text-red-200 px-4 py-2 rounded-lg text-sm">{'خروج' if lang == 'ar' else 'Logout'}</a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="card-bg p-4 rounded-xl text-center"><p class="text-gray-400 text-sm">{'عدد الزبائن' if lang == 'ar' else 'Clients'}</p><p class="text-2xl font-bold text-white">{{{{ bookings|length }}}}</p></div>
            <div class="card-bg p-4 rounded-xl text-center"><p class="text-gray-400 text-sm">{'إجمالي المدفوعات' if lang == 'ar' else 'Revenue'}</p><p class="text-2xl font-bold text-amber-400">{{{{ "%.2f"|format(total_rev) }}}} AED</p></div>
            <div class="card-bg p-4 rounded-xl text-center"><p class="text-gray-400 text-sm">{'أرباح عمولتك (5%)' if lang == 'ar' else 'Commission (5%)'}</p><p class="text-2xl font-bold text-emerald-400">{{{{ "%.2f"|format(total_comm) }}}} AED</p></div>
        </div>

        <div class="card-bg p-6 rounded-2xl">
            <h3 class="text-xl font-bold text-amber-400 mb-4">{'سجل خدماتك المقدمة' if lang == 'ar' else 'Your Services Record'}</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-right text-sm">
                    <thead><tr class="border-b border-gray-800 text-gray-400"><th class="pb-3">{'الزبون' if lang == 'ar' else 'Client'}</th><th class="pb-3">{'الخدمة' if lang == 'ar' else 'Service'}</th><th class="pb-3">{'السعر' if lang == 'ar' else 'Price'}</th><th class="pb-3">{'العمولة' if lang == 'ar' else 'Commission'}</th><th class="pb-3">{'التاريخ' if lang == 'ar' else 'Date'}</th></tr></thead>
                    <tbody>
                        {{% for b in bookings %}}
                        <tr class="border-b border-gray-800/50"><td class="py-3">{{{{ b[0] }}}}</td><td class="py-3">{{{{ b[1] }}}}</td><td class="py-3">{{{{ b[2] }}}} AED</td><td class="py-3 text-emerald-400">{{{{ b[3] }}}} AED</td><td class="py-3 text-gray-400">{{{{ b[4] }}}}</td></tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card-bg p-6 rounded-2xl">
            <h3 class="text-xl font-bold text-amber-400 mb-4">{'لوحة متصدرين المركز' if lang == 'ar' else 'Center Leaderboard'}</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-right text-sm">
                    <thead><tr class="border-b border-gray-800 text-gray-400"><th class="pb-3">{'الموظف' if lang == 'ar' else 'Staff'}</th><th class="pb-3">{'الوظيفة' if lang == 'ar' else 'Role'}</th><th class="pb-3">{'الخدمات' if lang == 'ar' else 'Services'}</th><th class="pb-3">{'الإيرادات' if lang == 'ar' else 'Revenue'}</th></tr></thead>
                    <tbody>
                        {{% for lb in leaderboard %}}
                        <tr class="border-b border-gray-800/50"><td class="py-3 font-semibold">{{{{ lb[0] }}}}</td><td class="py-3 text-gray-400">{{{{ lb[1] }}}}</td><td class="py-3">{{{{ lb[2] }}}}</td><td class="py-3 text-amber-400">{{{{ lb[3] }}}} AED</td></tr>
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
    <div class="max-w-md mx-auto card-bg p-8 rounded-2xl shadow-xl mt-10">
        <h2 class="text-2xl font-bold text-amber-400 mb-6 text-center">{'دخول موظف الاستقبال' if lang == 'ar' else 'Receptionist Login'}</h2>
        {{% with messages = get_flashed_messages(with_categories=true) %}}
            {{% if messages %}}
                {{% for cat, msg in messages %}}
                    <div class="bg-red-900 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-4 text-sm">{{{{ msg }}}}</div>
                {{% endfor %}}
            {{% endif %}}
        {{% endwith %}}
        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-sm text-gray-300 mb-2">{'أدخل كلمة المرور السرية:' if lang == 'ar' else 'Enter Secret Password:'}</label>
                <input type="password" name="password" required class="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:border-amber-500 focus:outline-none">
            </div>
            <button type="submit" class="w-full gold-gradient text-black font-bold p-3 rounded-lg hover:opacity-90 transition">{'دخول لوحة التحكم' if lang == 'ar' else 'Access Admin Panel'}</button>
        </form>
    </div>
    """
    return render_page(content)

@app.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    lang = session.get('lang', 'ar')
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
        
    conn = sqlite3.connect("o2_spa_pro.db")
    
    if request.method == 'POST' and 'add_booking' in request.form:
        client = request.form.get('client_name')
        staff_id = request.form.get('staff_id', type=int)
        service_name = request.form.get('service_name')
        price = request.form.get('price', type=float)
        comm = price * 0.05
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        time_str = datetime.datetime.now().strftime("%H:%M")
        conn.execute("INSERT INTO bookings (staff_id, client_name, service_name, service_price, commission, date, time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (staff_id, client, service_name, price, comm, date_str, time_str))
        conn.commit()
        
    if request.method == 'POST' and 'add_staff' in request.form:
        s_name = request.form.get('staff_name')
        s_role = request.form.get('staff_role')
        new_id = random.randint(1000, 9999)
        try:
            conn.execute("INSERT INTO staff (id, full_name, role) VALUES (?, ?, ?)", (new_id, s_name, s_role))
            conn.commit()
        except:
            pass
            
    if request.method == 'POST' and 'delete_booking' in request.form:
        b_id = request.form.get('booking_id', type=int)
        conn.execute("DELETE FROM bookings WHERE id=?", (b_id,))
        conn.commit()

    staff_list = conn.execute("SELECT * FROM staff").fetchall()
    services_list = conn.execute("SELECT * FROM services").fetchall()
    bookings_list = conn.execute("""
        SELECT bookings.id, bookings.client_name, staff.full_name, bookings.service_name, bookings.service_price, bookings.commission, bookings.date 
        FROM bookings JOIN staff ON bookings.staff_id = staff.id
    """).fetchall()
    leaderboard = conn.execute("""
        SELECT staff.id, staff.full_name, staff.role, COUNT(bookings.id), SUM(bookings.service_price), SUM(bookings.commission)
        FROM bookings JOIN staff ON bookings.staff_id = staff.id
        GROUP BY staff.id ORDER BY SUM(bookings.service_price) DESC
    """).fetchall()
    conn.close()

    content = f"""
    <div class="space-y-8 mt-6">
        <div class="card-bg p-6 rounded-2xl flex justify-between items-center">
            <h2 class="text-2xl font-bold text-amber-400">{'لوحة تحكم موظف الاستقبال' if lang == 'ar' else 'Receptionist Control Panel'}</h2>
            <a href="/" class="bg-red-900 text-red-200 px-4 py-2 rounded-lg text-sm">{'خروج' if lang == 'ar' else 'Logout'}</a>
        </div>

        <div class="card-bg p-6 rounded-2xl">
            <h3 class="text-xl font-bold text-amber-400 mb-4">{'➕ تسجيل خدمة جديدة وتوزيعها' if lang == 'ar' else '➕ Register New Service'}</h3>
            <form method="POST" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input type="hidden" name="add_booking" value="1">
                <div>
                    <label class="block text-sm text-gray-300 mb-1">{'اسم الزبون:' if lang == 'ar' else 'Client Name:'}</label>
                    <input type="text" name="client_name" required class="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white">
                </div>
                <div>
                    <label class="block text-sm text-gray-300 mb-1">{'الموظف المسؤول:' if lang == 'ar' else 'Assigned Staff:'}</label>
                    <select name="staff_id" class="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white">
                        {{% for s in staff_list %}}
                        <option value="{{{{ s[0] }}}}">{{{{ s[1] }}}} ({{{{ s[2] }}}})</option>
                        {{% endfor %}}
                    </select>
                </div>
                <div>
                    <label class="block text-sm text-gray-300 mb-1">{'اسم الخدمة:' if lang == 'ar' else 'Service Name:'}</label>
                    <input type="text" name="service_name" required class="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white">
                </div>
                <div>
                    <label class="block text-sm text-gray-300 mb-1">{'مبلغ الدفع (AED):' if lang == 'ar' else 'Price (AED):'}</label>
                    <input type="number" step="0.1" name="price" required class="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white">
                </div>
                <div class="md:col-span-2">
                    <button type="submit" class="w-full gold-gradient text-black font-bold p-3 rounded-lg">{'حفظ الخدمة وحساب 5%' if lang == 'ar' else 'Save & Calculate 5%'}</button>
                </div>
            </form>
        </div>

        <div class="card-bg p-6 rounded-2xl">
            <h3 class="text-xl font-bold text-amber-400 mb-4">{'🏆 لوحة المتصدرين والعمولات' if lang == 'ar' else '🏆 Leaderboard & Commissions'}</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-right text-sm">
                    <thead><tr class="border-b border-gray-800 text-gray-400"><th class="pb-3">ID</th><th class="pb-3">{'الموظف' if lang == 'ar' else 'Staff'}</th><th class="pb-3">{'الخدمات' if lang == 'ar' else 'Services'}</th><th class="pb-3">{'الإيرادات' if lang == 'ar' else 'Revenue'}</th><th class="pb-3">{'عمولة 5%' if lang == 'ar' else 'Commission'}</th></tr></thead>
                    <tbody>
                        {{% for lb in leaderboard %}}
                        <tr class="border-b border-gray-800/50"><td class="py-3">{{{{ lb[0] }}}}</td><td class="py-3 font-semibold">{{{{ lb[1] }}}}</td><td class="py-3">{{{{ lb[3] }}}}</td><td class="py-3 text-amber-400">{{{{ lb[4] }}}} AED</td><td class="py-3 text-emerald-400">{{{{ lb[5] }}}} AED</td></tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="card-bg p-6 rounded-2xl">
                <h3 class="text-xl font-bold text-amber-400 mb-4">{'👥 إضافة موظف جديد' if lang == 'ar' else '👥 Add New Staff'}</h3>
                <form method="POST" class="space-y-4">
                    <input type="hidden" name="add_staff" value="1">
                    <input type="text" name="staff_name" placeholder="{'الاسم الكامل' if lang == 'ar' else 'Full Name'}" required class="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white">
                    <input type="text" name="staff_role" placeholder="{'المسمى الوظيفي' if lang == 'ar' else 'Role'}" required class="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white">
                    <button type="submit" class="w-full bg-gray-800 text-amber-400 border border-amber-500 font-bold p-2.5 rounded-lg">{'تسجيل وتوليد ID' if lang == 'ar' else 'Register & Generate ID'}</button>
                </form>
            </div>
            <div class="card-bg p-6 rounded-2xl">
                <h3 class="text-xl font-bold text-amber-400 mb-4">{'📋 قائمة طاقم العمل' if lang == 'ar' else '📋 Staff List'}</h3>
                <div class="space-y-2 max-h-48 overflow-y-auto">
                    {{% for s in staff_list %}}
                    <div class="flex justify-between items-center bg-gray-900 p-2.5 rounded-lg text-sm">
                        <span>{{{{ s[1] }}}} ({{{{ s[2] }}}})</span>
                        <span class="text-amber-400 font-mono">ID: {{{{ s[0] }}}}</span>
                    </div>
                    {{% endfor %}}
                </div>
            </div>
        </div>

        <div class="card-bg p-6 rounded-2xl">
            <h3 class="text-xl font-bold text-amber-400 mb-4">{'🗑️ سجل المعاملات (للحذف والتعديل)' if lang == 'ar' else '🗑️ Bookings Log (Edit/Delete)'}</h3>
            <div class="overflow-x-auto">
                <table class="w-full text-right text-sm">
                    <thead><tr class="border-b border-gray-800 text-gray-400"><th class="pb-3">ID</th><th class="pb-3">{'الزبون' if lang == 'ar' else 'Client'}</th><th class="pb-3">{'الموظف' if lang == 'ar' else 'Staff'}</th><th class="pb-3">{'الخدمة' if lang == 'ar' else 'Service'}</th><th class="pb-3">{'السعر' if lang == 'ar' else 'Price'}</th><th class="pb-3">{'الإجراء' if lang == 'ar' else 'Action'}</th></tr></thead>
                    <tbody>
                        {{% for bk in bookings_list %}}
                        <tr class="border-b border-gray-800/50">
                            <td class="py-3">{{{{ bk[0] }}}}</td>
                            <td class="py-3">{{{{ bk[1] }}}}</td>
                            <td class="py-3">{{{{ bk[2] }}}}</td>
                            <td class="py-3">{{{{ bk[3] }}}}</td>
                            <td class="py-3">{{{{ bk[4] }}}} AED</td>
                            <td class="py-3">
                                <form method="POST" onsubmit="return confirm('هل أنت متأكد من الحذف؟');">
                                    <input type="hidden" name="delete_booking" value="1">
                                    <input type="hidden" name="booking_id" value="{{{{ bk[0] }}}}">
                                    <button type="submit" class="bg-red-900 text-red-200 px-3 py-1 rounded text-xs">{'حذف' if lang == 'ar' else 'Delete'}</button>
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