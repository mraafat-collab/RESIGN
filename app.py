<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة الموارد البشرية | HR Management Portal</title>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Google Fonts: Cairo -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brand: {
                            50: '#FDFBF7',
                            100: '#F7F2EA',
                            200: '#EADBCE',
                            300: '#D6C2A7',
                            400: '#C08A4B',
                            500: '#A36D33',
                            600: '#8C5A2B',
                            700: '#6E431E',
                            800: '#523014',
                            900: '#381F0A',
                        }
                    },
                    fontFamily: {
                        sans: ['Cairo', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Cairo', sans-serif;
            background-color: #F7F2EA;
        }
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #F7F2EA;
        }
        ::-webkit-scrollbar-thumb {
            background: #D6C2A7;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #8C5A2B;
        }
        .tab-active {
            border-bottom: 3px solid #8C5A2B;
            color: #8C5A2B;
            font-weight: 700;
        }
        .modal-backdrop {
            background-color: rgba(30, 20, 10, 0.45);
            backdrop-filter: blur(4px);
        }
    </style>
</head>
<body class="text-gray-800 antialiased flex h-screen overflow-hidden">

    <!-- Toast Notification Container -->
    <div id="toast-container" class="fixed top-5 left-5 z-50 flex flex-col gap-2"></div>

    <!-- SIDEBAR -->
    <aside class="w-64 bg-white border-l border-brand-200 flex flex-col justify-between shadow-lg z-20 transition-all duration-300">
        <div>
            <!-- Logo / Header -->
            <div class="p-6 border-b border-brand-100 flex items-center justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-brand-600 flex items-center justify-center text-white shadow-md font-bold text-lg">
                        HR
                    </div>
                    <div>
                        <h1 class="font-extrabold text-brand-900 text-lg leading-tight">بوابة الموارد البشرية</h1>
                        <p class="text-xs text-brand-400 font-medium">نظام التعيينات والاستقالات</p>
                    </div>
                </div>
            </div>

            <!-- Navigation Links -->
            <nav class="p-4 space-y-1.5">
                <button onclick="switchTab('dashboard')" id="nav-dashboard" class="nav-item w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all bg-brand-50 text-brand-600 shadow-sm">
                    <i class="fa-solid fa-chart-pie w-5 text-center text-base"></i>
                    <span>لوحة التحكم الرئيسية</span>
                </button>

                <button onclick="switchTab('resignations')" id="nav-resignations" class="nav-item w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-gray-600 hover:bg-brand-50 hover:text-brand-600">
                    <i class="fa-solid fa-user-minus w-5 text-center text-base"></i>
                    <span>طلبات الاستقالة</span>
                    <span id="badge-r-count" class="mr-auto text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-bold">0</span>
                </button>

                <button onclick="switchTab('hires')" id="nav-hires" class="nav-item w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-gray-600 hover:bg-brand-50 hover:text-brand-600">
                    <i class="fa-solid fa-user-plus w-5 text-center text-base"></i>
                    <span>التعيينات الجديدة</span>
                    <span id="badge-h-count" class="mr-auto text-xs px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-bold">0</span>
                </button>

                <button onclick="switchTab('reports')" id="nav-reports" class="nav-item w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-gray-600 hover:bg-brand-50 hover:text-brand-600">
                    <i class="fa-solid fa-chart-column w-5 text-center text-base"></i>
                    <span>التقارير والإحصائيات</span>
                </button>

                <button onclick="switchTab('settings')" id="nav-settings" class="nav-item w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all text-gray-600 hover:bg-brand-50 hover:text-brand-600">
                    <i class="fa-solid fa-database w-5 text-center text-base"></i>
                    <span>قاعدة البيانات والحفظ</span>
                </button>
            </nav>
        </div>

        <!-- System Storage Status Widget -->
        <div class="p-4 border-t border-brand-100 bg-brand-50/50">
            <div class="p-3 bg-white rounded-xl border border-brand-200 shadow-xs">
                <div class="flex items-center justify-between text-xs font-bold text-gray-700 mb-1">
                    <span class="flex items-center gap-1.5">
                        <span id="storage-status-dot" class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        حالة الحفظ:
                    </span>
                    <span id="storage-status-text" class="text-emerald-700 font-bold">نشط متصل</span>
                </div>
                <p id="storage-path-text" class="text-[11px] text-gray-500 truncate" title="جاري الاتصال...">جاري التحقق من قاعدة البيانات...</p>
            </div>
        </div>
    </aside>

    <!-- MAIN CONTENT AREA -->
    <main class="flex-1 flex flex-col h-full overflow-hidden">

        <!-- Top Header Bar -->
        <header class="h-16 bg-white border-b border-brand-200 px-8 flex items-center justify-between shadow-xs z-10">
            <div class="flex items-center gap-3">
                <h2 id="page-title" class="text-xl font-bold text-brand-900">لوحة التحكم الرئيسية</h2>
                <span id="page-subtitle" class="text-xs text-gray-500 bg-brand-100 px-2.5 py-1 rounded-full font-medium">نظرة عامة على البيانات</span>
            </div>

            <!-- Header Action buttons -->
            <div class="flex items-center gap-3">
                <button onclick="openModal('r')" class="bg-amber-50 hover:bg-amber-100 text-brand-700 font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 border border-brand-300 transition-all">
                    <i class="fa-solid fa-user-minus"></i>
                    <span>تسجيل استقالة</span>
                </button>

                <button onclick="openModal('h')" class="bg-brand-600 hover:bg-brand-700 text-white font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-2 shadow-sm transition-all">
                    <i class="fa-solid fa-user-plus"></i>
                    <span>إضافة تعيين جديد</span>
                </button>
            </div>
        </header>

        <!-- Dynamic Content Body -->
        <div class="flex-1 overflow-y-auto p-8 space-y-8">

            <!-- PAGE 1: DASHBOARD OVERVIEW -->
            <section id="view-dashboard" class="space-y-8">
                <!-- Persistent Warning Banner (If local temporary storage) -->
                <div id="persistence-warning" class="hidden bg-amber-50 border-r-4 border-amber-500 p-4 rounded-xl shadow-xs flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <i class="fa-solid fa-triangle-exclamation text-amber-600 text-xl"></i>
                        <div>
                            <h4 class="font-bold text-amber-900 text-sm">تنبيه الحفظ الدائم (Persistence Alert)</h4>
                            <p class="text-xs text-amber-800">يتم تشغيل التطبيق حالياً بدون مجلد مخصص للتخزين الدائم (DB_PATH غير مضبوط). لضمان عدم مسح البيانات عند إعادة تشغيل الخادم، قم بضبط متغيّر البيئة <code class="bg-amber-100 px-1 py-0.5 rounded text-red-700">DB_PATH</code>.</p>
                        </div>
                    </div>
                    <button onclick="switchTab('settings')" class="text-xs font-bold bg-amber-600 text-white px-3 py-1.5 rounded-lg hover:bg-amber-700 transition">تعليمات الضبط</button>
                </div>

                <!-- KPI Cards Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- Stat Card 1 -->
                    <div class="bg-white p-6 rounded-2xl border border-brand-200 shadow-sm flex items-center justify-between hover:shadow-md transition">
                        <div>
                            <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">إجمالي الاستقالات</p>
                            <h3 id="stat-resignations" class="text-2xl font-black text-brand-900">0</h3>
                            <p class="text-[11px] text-gray-500 mt-1"><span id="stat-r-pending" class="text-amber-600 font-bold">0</span> معلقة بانتظار الموافقة</p>
                        </div>
                        <div class="w-12 h-12 bg-red-50 rounded-2xl flex items-center justify-center text-red-600 text-xl font-bold border border-red-100">
                            <i class="fa-solid fa-file-signature"></i>
                        </div>
                    </div>

                    <!-- Stat Card 2 -->
                    <div class="bg-white p-6 rounded-2xl border border-brand-200 shadow-sm flex items-center justify-between hover:shadow-md transition">
                        <div>
                            <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">إجمالي التعيينات</p>
                            <h3 id="stat-hires" class="text-2xl font-black text-brand-900">0</h3>
                            <p class="text-[11px] text-gray-500 mt-1"><span id="stat-h-pending" class="text-emerald-600 font-bold">0</span> طلب جديد معلق</p>
                        </div>
                        <div class="w-12 h-12 bg-emerald-50 rounded-2xl flex items-center justify-center text-emerald-600 text-xl font-bold border border-emerald-100">
                            <i class="fa-solid fa-user-check"></i>
                        </div>
                    </div>

                    <!-- Stat Card 3 -->
                    <div class="bg-white p-6 rounded-2xl border border-brand-200 shadow-sm flex items-center justify-between hover:shadow-md transition">
                        <div>
                            <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">إجمالي التكلفة الشهرية للتعيينات</p>
                            <h3 id="stat-total-payroll" class="text-2xl font-black text-brand-800">0 EGP</h3>
                            <p class="text-[11px] text-gray-500 mt-1">الرواتب الأساسية + البدالات + KPI</p>
                        </div>
                        <div class="w-12 h-12 bg-brand-50 rounded-2xl flex items-center justify-center text-brand-600 text-xl font-bold border border-brand-200">
                            <i class="fa-solid fa-money-bill-wave"></i>
                        </div>
                    </div>

                    <!-- Stat Card 4 -->
                    <div class="bg-white p-6 rounded-2xl border border-brand-200 shadow-sm flex items-center justify-between hover:shadow-md transition">
                        <div>
                            <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">معدل الموافقة</p>
                            <h3 id="stat-approval-rate" class="text-2xl font-black text-brand-900">0%</h3>
                            <p class="text-[11px] text-gray-500 mt-1">من إجمالي الطلبات المقدمة</p>
                        </div>
                        <div class="w-12 h-12 bg-amber-50 rounded-2xl flex items-center justify-center text-amber-600 text-xl font-bold border border-amber-100">
                            <i class="fa-solid fa-chart-line"></i>
                        </div>
                    </div>
                </div>

                <!-- Recent Activity Overview Split -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <!-- Recent Resignations Table Snippet -->
                    <div class="bg-white rounded-2xl border border-brand-200 p-6 shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="font-bold text-gray-900 flex items-center gap-2 text-base">
                                <i class="fa-solid fa-clock-rotate-left text-brand-600"></i>
                                أحدث الاستقالات المسجلة
                            </h3>
                            <button onclick="switchTab('resignations')" class="text-xs font-bold text-brand-600 hover:text-brand-800">عرض الكل &larr;</button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead>
                                    <tr class="text-gray-500 border-b border-gray-100 pb-2">
                                        <th class="pb-3">الموظف</th>
                                        <th class="pb-3">المسمى الوظيفي</th>
                                        <th class="pb-3">آخر يوم عمل</th>
                                        <th class="pb-3">الحالة</th>
                                    </tr>
                                </thead>
                                <tbody id="dash-recent-r" class="divide-y divide-gray-50">
                                    <!-- Dynamic -->
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Recent Hires Table Snippet -->
                    <div class="bg-white rounded-2xl border border-brand-200 p-6 shadow-sm">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="font-bold text-gray-900 flex items-center gap-2 text-base">
                                <i class="fa-solid fa-user-plus text-brand-600"></i>
                                أحدث التعيينات المسجلة
                            </h3>
                            <button onclick="switchTab('hires')" class="text-xs font-bold text-brand-600 hover:text-brand-800">عرض الكل &larr;</button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-right text-xs">
                                <thead>
                                    <tr class="text-gray-500 border-b border-gray-100 pb-2">
                                        <th class="pb-3">الموظف</th>
                                        <th class="pb-3">الوظيفة</th>
                                        <th class="pb-3">الفرع</th>
                                        <th class="pb-3">إجمالي صافي الراتب</th>
                                        <th class="pb-3">الحالة</th>
                                    </tr>
                                </thead>
                                <tbody id="dash-recent-h" class="divide-y divide-gray-50">
                                    <!-- Dynamic -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- PAGE 2: RESIGNATIONS VIEW -->
            <section id="view-resignations" class="hidden space-y-6">
                <!-- Top Toolbar & Search -->
                <div class="bg-white p-5 rounded-2xl border border-brand-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
                    <!-- Status Tabs -->
                    <div class="flex items-center gap-2 bg-brand-50 p-1.5 rounded-xl border border-brand-100 w-full md:w-auto">
                        <button onclick="filterTable('r', 'All')" id="filter-r-All" class="px-4 py-2 rounded-lg text-xs font-bold transition bg-white shadow-xs text-brand-800">الكل</button>
                        <button onclick="filterTable('r', 'Pending')" id="filter-r-Pending" class="px-4 py-2 rounded-lg text-xs font-bold transition text-gray-600 hover:text-brand-800">معلقة</button>
                        <button onclick="filterTable('r', 'Approved')" id="filter-r-Approved" class="px-4 py-2 rounded-lg text-xs font-bold transition text-gray-600 hover:text-brand-800">مقبولة</button>
                        <button onclick="filterTable('r', 'Rejected')" id="filter-r-Rejected" class="px-4 py-2 rounded-lg text-xs font-bold transition text-gray-600 hover:text-brand-800">مرفوضة</button>
                    </div>

                    <!-- Search Input -->
                    <div class="relative w-full md:w-72">
                        <i class="fa-solid fa-magnifying-glass absolute right-3.5 top-3 text-gray-400 text-sm"></i>
                        <input type="text" id="search-r" onkeyup="renderTable('r')" placeholder="بحث عن اسم الموظف، المسمى، الفرع..." class="w-full pl-4 pr-10 py-2 bg-gray-50 border border-brand-200 rounded-xl text-xs focus:ring-2 focus:ring-brand-600 outline-none transition">
                    </div>
                </div>

                <!-- Main Resignations Table -->
                <div class="bg-white rounded-2xl border border-brand-200 shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-right text-xs">
                            <thead class="bg-brand-50/70 border-b border-brand-200 text-gray-700 font-bold">
                                <tr>
                                    <th class="p-4">#</th>
                                    <th class="p-4">اسم الموظف</th>
                                    <th class="p-4">المسمى الوظيفي</th>
                                    <th class="p-4">الفرع</th>
                                    <th class="p-4">تاريخ التعيين</th>
                                    <th class="p-4">تاريخ الاستقالة</th>
                                    <th class="p-4">آخر يوم عمل</th>
                                    <th class="p-4">صافي المستحقات</th>
                                    <th class="p-4">الحالة</th>
                                    <th class="p-4 text-center">الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody id="table-r-body" class="divide-y divide-gray-100 font-medium">
                                <!-- Dynamic JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <!-- PAGE 3: NEW HIRES VIEW -->
            <section id="view-hires" class="hidden space-y-6">
                <!-- Top Toolbar & Search -->
                <div class="bg-white p-5 rounded-2xl border border-brand-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
                    <!-- Status Tabs -->
                    <div class="flex items-center gap-2 bg-brand-50 p-1.5 rounded-xl border border-brand-100 w-full md:w-auto">
                        <button onclick="filterTable('h', 'All')" id="filter-h-All" class="px-4 py-2 rounded-lg text-xs font-bold transition bg-white shadow-xs text-brand-800">الكل</button>
                        <button onclick="filterTable('h', 'Pending')" id="filter-h-Pending" class="px-4 py-2 rounded-lg text-xs font-bold transition text-gray-600 hover:text-brand-800">معلقة</button>
                        <button onclick="filterTable('h', 'Approved')" id="filter-h-Approved" class="px-4 py-2 rounded-lg text-xs font-bold transition text-gray-600 hover:text-brand-800">مقبولة</button>
                        <button onclick="filterTable('h', 'Rejected')" id="filter-h-Rejected" class="px-4 py-2 rounded-lg text-xs font-bold transition text-gray-600 hover:text-brand-800">مرفوضة</button>
                    </div>

                    <!-- Search Input -->
                    <div class="relative w-full md:w-72">
                        <i class="fa-solid fa-magnifying-glass absolute right-3.5 top-3 text-gray-400 text-sm"></i>
                        <input type="text" id="search-h" onkeyup="renderTable('h')" placeholder="بحث باسم الموظف أو الفرع أو المؤهل..." class="w-full pl-4 pr-10 py-2 bg-gray-50 border border-brand-200 rounded-xl text-xs focus:ring-2 focus:ring-brand-600 outline-none transition">
                    </div>
                </div>

                <!-- Main New Hires Table -->
                <div class="bg-white rounded-2xl border border-brand-200 shadow-sm overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-right text-xs">
                            <thead class="bg-brand-50/70 border-b border-brand-200 text-gray-700 font-bold">
                                <tr>
                                    <th class="p-4">#</th>
                                    <th class="p-4">اسم المرشح</th>
                                    <th class="p-4">المسمى الوظيفي</th>
                                    <th class="p-4">الفرع / الدرجة</th>
                                    <th class="p-4">تاريخ المباشرة</th>
                                    <th class="p-4">الأساسي</th>
                                    <th class="p-4">البدلات</th>
                                    <th class="p-4">KPI 100%</th>
                                    <th class="p-4">إجمالي الصافي</th>
                                    <th class="p-4">الحالة</th>
                                    <th class="p-4 text-center">الإجراءات</th>
                                </tr>
                            </thead>
                            <tbody id="table-h-body" class="divide-y divide-gray-100 font-medium">
                                <!-- Dynamic JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <!-- PAGE 4: REPORTS & ANALYTICS VIEW -->
            <section id="view-reports" class="hidden space-y-8">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <!-- Resignations vs Hires Chart -->
                    <div class="bg-white p-6 rounded-2xl border border-brand-200 shadow-sm">
                        <h3 class="font-bold text-brand-900 mb-4 flex items-center gap-2">
                            <i class="fa-solid fa-chart-line text-brand-600"></i>
                            مقارنة طلبات التعيين والاستقالة
                        </h3>
                        <div class="h-64">
                            <canvas id="chart-comparison"></canvas>
                        </div>
                    </div>

                    <!-- Salary Distribution Breakdown Chart -->
                    <div class="bg-white p-6 rounded-2xl border border-brand-200 shadow-sm">
                        <h3 class="font-bold text-brand-900 mb-4 flex items-center gap-2">
                            <i class="fa-solid fa-chart-pie text-brand-600"></i>
                            توزيع تكلفة التعيينات الجديدة (الرواتب والبدلات)
                        </h3>
                        <div class="h-64 flex items-center justify-center">
                            <canvas id="chart-salaries"></canvas>
                        </div>
                    </div>
                </div>
            </section>

            <!-- PAGE 5: DATABASE & BACKUP SETTINGS -->
            <section id="view-settings" class="hidden space-y-8 max-w-4xl">

                <!-- Persistence Troubleshooting Box -->
                <div class="bg-white p-6 rounded-2xl border border-brand-200 shadow-sm space-y-4">
                    <h3 class="text-base font-bold text-brand-900 flex items-center gap-2">
                        <i class="fa-solid fa-database text-brand-600"></i>
                        كيفية منع ضياع البيانات عند إعادة تشغيل السيرفر (Data Persistence)
                    </h3>
                    <p class="text-xs text-gray-600 leading-relaxed">
                        إذا كنت تستخدم استضافة مثل (Render, Railway, Heroku, Docker)، فإن أي تغيير يتم حفظه داخل المجلد المؤقت يتم مسحه تلقائياً عند إعادة التحديث. لحفظ الاستقالات والتعيينات بشكل دائم:
                    </p>
                    <div class="bg-brand-50 p-4 rounded-xl border border-brand-200 font-mono text-xs text-brand-900 space-y-2 dir-ltr text-left">
                        <p class="font-bold text-brand-700">// 1. قم بربط المجلد مع مجلد دائم (Persistent Volume) في الاستضافة</p>
                        <p class="text-emerald-700 font-bold">export DB_PATH=/var/data/data.db</p>
                        <p class="font-bold text-brand-700">// 2. أو قم بتشغيل الخادم بالمرور التالي:</p>
                        <p>DB_PATH=/var/data/data.db uvicorn main:app --reload</p>
                    </div>
                </div>

                <!-- Backup & Restore Actions Card -->
                <div class="bg-white p-6 rounded-2xl border border-brand-200 shadow-sm space-y-6">
                    <h3 class="text-base font-bold text-brand-900 flex items-center gap-2">
                        <i class="fa-solid fa-floppy-disk text-brand-600"></i>
                        النسخ الاحتياطي والاستعادة الفورية
                    </h3>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- Download Backup -->
                        <div class="border border-brand-200 p-5 rounded-xl bg-brand-50/40 space-y-3">
                            <h4 class="font-bold text-sm text-gray-800">تحميل نسخة احتياطية (Download Backup)</h4>
                            <p class="text-xs text-gray-500">قم بتنزيل ملف SQLite يحتوي على جميع السجلات الحالية لحفظها على جهازك.</p>
                            <a href="/api/backup" download="data.db" class="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-bold px-4 py-2.5 rounded-xl text-xs shadow-xs transition">
                                <i class="fa-solid fa-download"></i>
                                تنزيل قاعدة البيانات (.db)
                            </a>
                        </div>

                        <!-- Restore Backup -->
                        <div class="border border-brand-200 p-5 rounded-xl bg-brand-50/40 space-y-3">
                            <h4 class="font-bold text-sm text-gray-800">استعادة قاعدة بيانات (Restore Database)</h4>
                            <p class="text-xs text-gray-500">اختر ملف قاعدة البيانات السابق لرفع البيانات واستبدال السجلات.</p>
                            <label class="inline-flex items-center gap-2 bg-amber-600 hover:bg-amber-700 text-white font-bold px-4 py-2.5 rounded-xl text-xs shadow-xs cursor-pointer transition">
                                <i class="fa-solid fa-upload"></i>
                                <span>رفع ملف واستعادة البيانات</span>
                                <input type="file" id="restore-file-input" onchange="uploadBackup(event)" class="hidden" accept=".db,.sqlite">
                            </label>
                        </div>
                    </div>
                </div>
            </section>

        </div>
    </main>

    <!-- MODAL 1: ADD / EDIT RESIGNATION -->
    <div id="modal-r" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 modal-backdrop">
        <div class="bg-white w-full max-w-2xl rounded-2xl shadow-2xl border border-brand-200 overflow-hidden transform transition-all">
            <div class="bg-brand-600 px-6 py-4 flex items-center justify-between text-white">
                <h3 id="modal-r-title" class="font-bold text-base flex items-center gap-2">
                    <i class="fa-solid fa-user-minus"></i>
                    تسجيل طلب استقالة جديد
                </h3>
                <button onclick="closeModal('r')" class="text-brand-200 hover:text-white text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <form id="form-r" onsubmit="saveRecord(event, 'r')" class="p-6 space-y-4 text-xs">
                <input type="hidden" id="r-id" value="">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">اسم الموظف <span class="text-red-500">*</span></label>
                        <input type="text" id="r-name" required class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">المسمى الوظيفي</label>
                        <input type="text" id="r-title" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">الفرع / القسم</label>
                        <input type="text" id="r-branch" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">تاريخ التعيين <span class="text-red-500">*</span></label>
                        <input type="date" id="r-hire_date" required class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">تاريخ تقديم الاستقالة <span class="text-red-500">*</span></label>
                        <input type="date" id="r-resign_date" required class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">آخر يوم عمل <span class="text-red-500">*</span></label>
                        <input type="date" id="r-last_day" required class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">صافي الراتب المستحق (EGP)</label>
                        <input type="number" step="any" id="r-net_pay" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">المدير المباشر</label>
                        <input type="text" id="r-manager" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">المستلم / الموجه إليه (Recipient)</label>
                        <input type="text" id="r-recipient" placeholder="مثال: Mr. Ahmed / Manager" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">سبب الاستقالة</label>
                        <input type="text" id="r-reason" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                </div>
                <div class="pt-4 flex justify-end gap-3 border-t border-brand-100 mt-4">
                    <button type="button" onclick="closeModal('r')" class="px-5 py-2.5 rounded-xl border border-gray-300 font-bold text-gray-600 hover:bg-gray-100">إلغاء</button>
                    <button type="submit" class="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold shadow-md">حفظ البيانات</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL 2: ADD / EDIT NEW HIRE -->
    <div id="modal-h" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 modal-backdrop">
        <div class="bg-white w-full max-w-3xl rounded-2xl shadow-2xl border border-brand-200 overflow-hidden transform transition-all">
            <div class="bg-brand-600 px-6 py-4 flex items-center justify-between text-white">
                <h3 id="modal-h-title" class="font-bold text-base flex items-center gap-2">
                    <i class="fa-solid fa-user-plus"></i>
                    تسجيل تعيين جديد (New Hire Form)
                </h3>
                <button onclick="closeModal('h')" class="text-brand-200 hover:text-white text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <form id="form-h" onsubmit="saveRecord(event, 'h')" class="p-6 space-y-4 text-xs">
                <input type="hidden" id="h-id" value="">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="md:col-span-1">
                        <label class="block font-bold text-gray-700 mb-1">اسم الموظف <span class="text-red-500">*</span></label>
                        <input type="text" id="h-name" required class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">المسمى الوظيفي</label>
                        <input type="text" id="h-title" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">الفرع / الإدارة</label>
                        <input type="text" id="h-branch" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">تاريخ المباشرة <span class="text-red-500">*</span></label>
                        <input type="date" id="h-hire_date" required class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">الدرجة الوظيفية (Grading)</label>
                        <input type="text" id="h-grading" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">المؤهل الدراسي</label>
                        <input type="text" id="h-education" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">السن</label>
                        <input type="text" id="h-age" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">العنوان</label>
                        <input type="text" id="h-address" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">الخبرات السابقة</label>
                        <input type="text" id="h-experience" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">المدير المباشر</label>
                        <input type="text" id="h-manager" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                    <div>
                        <label class="block font-bold text-gray-700 mb-1">المستلم (Recipient)</label>
                        <input type="text" id="h-recipient" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                    </div>
                </div>

                <!-- Salary Breakdown Section -->
                <div class="p-4 bg-brand-50 rounded-xl border border-brand-200 space-y-3">
                    <h4 class="font-bold text-brand-900">تفاصيل الراتب المستحق (Net Salary Details)</h4>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label class="block font-bold text-gray-700 mb-1">الراتب الأساسي (Net Basic)</label>
                            <input type="number" step="any" id="h-basic" class="w-full p-2.5 bg-white border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                        </div>
                        <div>
                            <label class="block font-bold text-gray-700 mb-1">البدلات (Net Allowance)</label>
                            <input type="number" step="any" id="h-allowance" class="w-full p-2.5 bg-white border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                        </div>
                        <div>
                            <label class="block font-bold text-gray-700 mb-1">الحوافز (Net KPI 100%)</label>
                            <input type="number" step="any" id="h-kpi" class="w-full p-2.5 bg-white border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                        </div>
                    </div>
                </div>

                <div class="pt-4 flex justify-end gap-3 border-t border-brand-100 mt-4">
                    <button type="button" onclick="closeModal('h')" class="px-5 py-2.5 rounded-xl border border-gray-300 font-bold text-gray-600 hover:bg-gray-100">إلغاء</button>
                    <button type="submit" class="px-6 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-bold shadow-md">حفظ البيانات</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL 3: EMAIL & TEMPLATE PREVIEW -->
    <div id="modal-preview" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 modal-backdrop">
        <div class="bg-white w-full max-w-4xl h-[90vh] rounded-2xl shadow-2xl border border-brand-200 flex flex-col overflow-hidden">
            <div class="bg-brand-700 px-6 py-4 flex items-center justify-between text-white">
                <h3 class="font-bold text-base flex items-center gap-2">
                    <i class="fa-solid fa-envelope-open-text"></i>
                    معاينة النموذج الرسمي الموجه للاعتماد (Email Form Preview)
                </h3>
                <button onclick="closePreviewModal()" class="text-brand-200 hover:text-white text-lg"><i class="fa-solid fa-xmark"></i></button>
            </div>
            
            <div class="p-4 bg-brand-50 border-b border-brand-200 flex flex-wrap items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                    <label class="text-xs font-bold text-gray-700">إضافة ملاحظة على الخطاب:</label>
                    <input type="text" id="preview-note-input" placeholder="اكتب ملاحظة هنا..." class="text-xs p-2 bg-white border border-brand-200 rounded-lg w-64">
                    <button onclick="refreshPreviewFrame()" class="text-xs font-bold bg-brand-600 text-white px-3 py-2 rounded-lg hover:bg-brand-700">تحديث المعاينة</button>
                </div>
                
                <div class="flex items-center gap-2">
                    <button onclick="triggerSendEmailModal()" class="text-xs font-bold bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 flex items-center gap-1.5">
                        <i class="fa-solid fa-paper-plane"></i>
                        إرسال عبر البريد الإلكتروني
                    </button>
                </div>
            </div>

            <div class="flex-1 bg-gray-200 p-4 overflow-hidden">
                <iframe id="preview-iframe" class="w-full h-full rounded-xl border border-gray-300 shadow-inner bg-white"></iframe>
            </div>
        </div>
    </div>

    <!-- MODAL 4: SEND EMAIL MODAL -->
    <div id="modal-mail-send" class="fixed inset-0 z-50 hidden flex items-center justify-center p-4 modal-backdrop">
        <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl border border-brand-200 overflow-hidden">
            <div class="bg-brand-800 px-6 py-4 flex items-center justify-between text-white">
                <h3 class="font-bold text-sm">إرسال الخطاب بالبريد الإلكتروني</h3>
                <button onclick="closeMailSendModal()" class="text-brand-200 hover:text-white text-base"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <form id="form-send-mail" onsubmit="executeSendMail(event)" class="p-6 space-y-4 text-xs">
                <div>
                    <label class="block font-bold text-gray-700 mb-1">إلى (To): <span class="text-red-500">*</span></label>
                    <input type="text" id="mail-to" placeholder="manager@company.com" required class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                </div>
                <div>
                    <label class="block font-bold text-gray-700 mb-1">نسخة إلى (CC):</label>
                    <input type="text" id="mail-cc" placeholder="hr@company.com" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                </div>
                <div>
                    <label class="block font-bold text-gray-700 mb-1">عنوان الرسالة (Subject):</label>
                    <input type="text" id="mail-subject" placeholder="طلب اعتماد..." class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none">
                </div>
                <div>
                    <label class="block font-bold text-gray-700 mb-1">ملاحظات إضافية:</label>
                    <textarea id="mail-note" rows="2" class="w-full p-2.5 bg-gray-50 border border-brand-200 rounded-xl focus:ring-2 focus:ring-brand-600 outline-none"></textarea>
                </div>
                <div class="pt-3 flex justify-end gap-2">
                    <button type="button" onclick="closeMailSendModal()" class="px-4 py-2 rounded-xl border border-gray-300 font-bold text-gray-600">إلغاء</button>
                    <button type="submit" class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold">إرسال الآن</button>
                </div>
            </form>
        </div>
    </div>


    <!-- CLIENT JAVASCRIPT LOGIC -->
    <script>
        // Global App State
        const state = {
            r: [], // Resignations
            h: [], // Hires
            filterR: 'All',
            filterH: 'All',
            activePreview: { t: null, i: null },
            info: {}
        };

        // Charts Holders
        let chartComparisonInstance = null;
        let chartSalariesInstance = null;

        // On Document Ready
        document.addEventListener('DOMContentLoaded', () => {
            fetchSystemInfo();
            loadData('r');
            loadData('h');
        });

        // 1. Fetch Backend Info
        async function fetchSystemInfo() {
            try {
                const res = await fetch('/api/info');
                if (res.ok) {
                    state.info = await res.json();
                    document.getElementById('storage-path-text').innerText = state.info.db;
                    if (!state.info.persistent) {
                        document.getElementById('persistence-warning').classList.remove('hidden');
                        document.getElementById('storage-status-dot').className = 'w-2.5 h-2.5 rounded-full bg-amber-500';
                        document.getElementById('storage-status-text').innerText = 'مؤقت (غير دائم)';
                        document.getElementById('storage-status-text').className = 'text-amber-700 font-bold';
                    }
                }
            } catch (e) {
                console.warn('Backend running in standalone front-end mode or offline mode.');
            }
        }

        // 2. Load Table Data
        async function loadData(t) {
            try {
                const res = await fetch(`/api/${t}`);
                if (res.ok) {
                    state[t] = await res.json();
                }
            } catch (e) {
                console.warn(`Could not fetch /api/${t}.`);
            }
            renderTable(t);
            updateStats();
        }

        // 3. Navigation Switcher
        function switchTab(tab) {
            ['dashboard', 'resignations', 'hires', 'reports', 'settings'].forEach(view => {
                document.getElementById(`view-${view}`).classList.add('hidden');
                const nav = document.getElementById(`nav-${view}`);
                if (nav) {
                    nav.classList.remove('bg-brand-50', 'text-brand-600', 'shadow-sm');
                    nav.classList.add('text-gray-600');
                }
            });

            document.getElementById(`view-${tab}`).classList.remove('hidden');
            const activeNav = document.getElementById(`nav-${tab}`);
            if (activeNav) {
                activeNav.classList.add('bg-brand-50', 'text-brand-600', 'shadow-sm');
                activeNav.classList.remove('text-gray-600');
            }

            // Update Header Titles
            const titles = {
                'dashboard': ['لوحة التحكم الرئيسية', 'نظرة عامة على البيانات'],
                'resignations': ['سجلات طلبات الاستقالة', 'إدارة ومتابعة استقالات الموظفين'],
                'hires': ['سجلات التعيينات الجديدة', 'إدارة ومتابعة طلبات التعيين'],
                'reports': ['التقارير والتحليلات', 'رسوم بيانية توضيحية'],
                'settings': ['إعدادات قاعدة البيانات والحفظ', 'إدارة الحفظ الدائم والنسخ الاحتياطي']
            };
            document.getElementById('page-title').innerText = titles[tab][0];
            document.getElementById('page-subtitle').innerText = titles[tab][1];

            if (tab === 'reports') {
                renderCharts();
            }
        }

        // 4. Table Filter Selector
        function filterTable(t, status) {
            state[`filter${t.toUpperCase()}`] = status;
            ['All', 'Pending', 'Approved', 'Rejected'].forEach(s => {
                const btn = document.getElementById(`filter-${t}-${s}`);
                if (btn) {
                    if (s === status) {
                        btn.className = 'px-4 py-2 rounded-lg text-xs font-bold transition bg-white shadow-xs text-brand-800';
                    } else {
                        btn.className = 'px-4 py-2 rounded-lg text-xs font-bold transition text-gray-600 hover:text-brand-800';
                    }
                }
            });
            renderTable(t);
        }

        // 5. Render Tables (Resignations & Hires)
        function renderTable(t) {
            const filter = state[`filter${t.toUpperCase()}`];
            const searchVal = (document.getElementById(`search-${t}`)?.value || '').toLowerCase();
            const tbody = document.getElementById(`table-${t}-body`);
            if (!tbody) return;

            let items = state[t].filter(item => {
                const matchesFilter = (filter === 'All') || (item.status === filter);
                const matchesSearch = !searchVal || 
                    (item.name && item.name.toLowerCase().includes(searchVal)) ||
                    (item.title && item.title.toLowerCase().includes(searchVal)) ||
                    (item.branch && item.branch.toLowerCase().includes(searchVal));
                return matchesFilter && matchesSearch;
            });

            if (items.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="11" class="p-8 text-center text-gray-400">
                            <i class="fa-solid fa-folder-open text-3xl mb-2 block"></i>
                            لا توجد بيانات مطابقة للعرض حالياً
                        </td>
                    </tr>`;
                return;
            }

            if (t === 'r') {
                tbody.innerHTML = items.map((r, idx) => `
                    <tr class="hover:bg-brand-50/30 transition border-b border-gray-50">
                        <td class="p-4 text-gray-400 font-bold">${r.id || idx + 1}</td>
                        <td class="p-4 font-bold text-gray-900">${escapeHtml(r.name)}</td>
                        <td class="p-4 text-gray-600">${escapeHtml(r.title || '-')}</td>
                        <td class="p-4 text-gray-600">${escapeHtml(r.branch || '-')}</td>
                        <td class="p-4 text-gray-500">${r.hire_date || '-'}</td>
                        <td class="p-4 text-gray-500">${r.resign_date || '-'}</td>
                        <td class="p-4 text-red-600 font-semibold">${r.last_day || '-'}</td>
                        <td class="p-4 font-bold text-brand-900">${(r.net_pay || 0).toLocaleString()} EGP</td>
                        <td class="p-4">${getStatusBadge(r.status)}</td>
                        <td class="p-4 text-center">
                            <div class="flex items-center justify-center gap-1.5">
                                <button onclick="openPreviewModal('r', ${r.id})" title="معاينة الخطاب" class="p-2 text-brand-600 hover:bg-brand-100 rounded-lg"><i class="fa-solid fa-eye"></i></button>
                                <button onclick="changeStatus('r', ${r.id}, 'Approved')" title="قبول" class="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg"><i class="fa-solid fa-check"></i></button>
                                <button onclick="changeStatus('r', ${r.id}, 'Rejected')" title="رفض" class="p-2 text-red-600 hover:bg-red-50 rounded-lg"><i class="fa-solid fa-xmark"></i></button>
                                <button onclick="editRecord('r', ${r.id})" title="تعديل" class="p-2 text-amber-600 hover:bg-amber-50 rounded-lg"><i class="fa-solid fa-pen"></i></button>
                                <button onclick="deleteRecord('r', ${r.id})" title="حذف" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"><i class="fa-solid fa-trash"></i></button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = items.map((h, idx) => {
                    const total = (h.basic || 0) + (h.allowance || 0) + (h.kpi || 0);
                    return `
                    <tr class="hover:bg-brand-50/30 transition border-b border-gray-50">
                        <td class="p-4 text-gray-400 font-bold">${h.id || idx + 1}</td>
                        <td class="p-4 font-bold text-gray-900">${escapeHtml(h.name)}</td>
                        <td class="p-4 text-gray-600">${escapeHtml(h.title || '-')}</td>
                        <td class="p-4 text-gray-600">${escapeHtml(h.branch || '-')} <span class="text-[10px] bg-gray-100 px-1.5 py-0.5 rounded text-gray-500">${escapeHtml(h.grading || '')}</span></td>
                        <td class="p-4 text-gray-500">${h.hire_date || '-'}</td>
                        <td class="p-4 text-gray-600">${(h.basic || 0).toLocaleString()}</td>
                        <td class="p-4 text-gray-600">${(h.allowance || 0).toLocaleString()}</td>
                        <td class="p-4 text-gray-600">${(h.kpi || 0).toLocaleString()}</td>
                        <td class="p-4 font-bold text-emerald-700">${total.toLocaleString()} EGP</td>
                        <td class="p-4">${getStatusBadge(h.status)}</td>
                        <td class="p-4 text-center">
                            <div class="flex items-center justify-center gap-1.5">
                                <button onclick="openPreviewModal('h', ${h.id})" title="معاينة الخطاب" class="p-2 text-brand-600 hover:bg-brand-100 rounded-lg"><i class="fa-solid fa-eye"></i></button>
                                <button onclick="changeStatus('h', ${h.id}, 'Approved')" title="قبول" class="p-2 text-emerald-600 hover:bg-emerald-50 rounded-lg"><i class="fa-solid fa-check"></i></button>
                                <button onclick="changeStatus('h', ${h.id}, 'Rejected')" title="رفض" class="p-2 text-red-600 hover:bg-red-50 rounded-lg"><i class="fa-solid fa-xmark"></i></button>
                                <button onclick="editRecord('h', ${h.id})" title="تعديل" class="p-2 text-amber-600 hover:bg-amber-50 rounded-lg"><i class="fa-solid fa-pen"></i></button>
                                <button onclick="deleteRecord('h', ${h.id})" title="حذف" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"><i class="fa-solid fa-trash"></i></button>
                            </div>
                        </td>
                    </tr>
                `}).join('');
            }
        }

        // Status Badge Helper
        function getStatusBadge(status) {
            if (status === 'Approved') {
                return `<span class="bg-emerald-100 text-emerald-800 text-[11px] font-bold px-2.5 py-1 rounded-full border border-emerald-200">مقبول</span>`;
            } else if (status === 'Rejected') {
                return `<span class="bg-red-100 text-red-800 text-[11px] font-bold px-2.5 py-1 rounded-full border border-red-200">مرفوض</span>`;
            }
            return `<span class="bg-amber-100 text-amber-800 text-[11px] font-bold px-2.5 py-1 rounded-full border border-amber-200">معلق</span>`;
        }

        // 6. Update Stats Cards & Recent Table Widgets
        function updateStats() {
            // Count Badges
            document.getElementById('badge-r-count').innerText = state.r.length;
            document.getElementById('badge-h-count').innerText = state.h.length;

            // KPI 1: Resignations
            document.getElementById('stat-resignations').innerText = state.r.length;
            const rPending = state.r.filter(x => x.status === 'Pending').length;
            document.getElementById('stat-r-pending').innerText = rPending;

            // KPI 2: Hires
            document.getElementById('stat-hires').innerText = state.h.length;
            const hPending = state.h.filter(x => x.status === 'Pending').length;
            document.getElementById('stat-h-pending').innerText = hPending;

            // KPI 3: Total Monthly Payroll
            const totalPayroll = state.h.reduce((acc, curr) => acc + (curr.basic || 0) + (curr.allowance || 0) + (curr.kpi || 0), 0);
            document.getElementById('stat-total-payroll').innerText = `${totalPayroll.toLocaleString()} EGP`;

            // KPI 4: Approval Rate
            const totalAll = state.r.length + state.h.length;
            const totalApproved = state.r.filter(x => x.status === 'Approved').length + state.h.filter(x => x.status === 'Approved').length;
            const rate = totalAll > 0 ? Math.round((totalApproved / totalAll) * 100) : 0;
            document.getElementById('stat-approval-rate').innerText = `${rate}%`;

            // Dashboard Recent Snippets
            const recentR = state.r.slice(0, 5);
            document.getElementById('dash-recent-r').innerHTML = recentR.length === 0 ? 
                '<tr><td colspan="4" class="p-4 text-center text-gray-400">لا توجد استقالات</td></tr>' :
                recentR.map(r => `
                    <tr>
                        <td class="py-2.5 font-bold text-gray-800">${escapeHtml(r.name)}</td>
                        <td class="py-2.5 text-gray-600">${escapeHtml(r.title || '-')}</td>
                        <td class="py-2.5 text-red-600 font-semibold">${r.last_day || '-'}</td>
                        <td class="py-2.5">${getStatusBadge(r.status)}</td>
                    </tr>
                `).join('');

            const recentH = state.h.slice(0, 5);
            document.getElementById('dash-recent-h').innerHTML = recentH.length === 0 ?
                '<tr><td colspan="5" class="p-4 text-center text-gray-400">لا توجد تعيينات</td></tr>' :
                recentH.map(h => {
                    const total = (h.basic || 0) + (h.allowance || 0) + (h.kpi || 0);
                    return `
                    <tr>
                        <td class="py-2.5 font-bold text-gray-800">${escapeHtml(h.name)}</td>
                        <td class="py-2.5 text-gray-600">${escapeHtml(h.title || '-')}</td>
                        <td class="py-2.5 text-gray-600">${escapeHtml(h.branch || '-')}</td>
                        <td class="py-2.5 font-bold text-emerald-700">${total.toLocaleString()} EGP</td>
                        <td class="py-2.5">${getStatusBadge(h.status)}</td>
                    </tr>
                `}).join('');
        }

        // 7. Modals logic (Open/Close/Save)
        function openModal(t) {
            document.getElementById(`form-${t}`).reset();
            document.getElementById(`${t}-id`).value = '';
            document.getElementById(`modal-${t}-title`).innerHTML = t === 'r' ? 
                '<i class="fa-solid fa-user-minus"></i> تسجيل طلب استقالة جديد' : 
                '<i class="fa-solid fa-user-plus"></i> تسجيل تعيين جديد';
            document.getElementById(`modal-${t}`).classList.remove('hidden');
        }

        function closeModal(t) {
            document.getElementById(`modal-${t}`).classList.add('hidden');
        }

        function editRecord(t, id) {
            const item = state[t].find(x => x.id === id);
            if (!item) return;

            document.getElementById(`modal-${t}-title`).innerText = `تعديل السجل #${id}`;
            document.getElementById(`${t}-id`).value = id;

            // Fill form inputs
            Object.keys(item).forEach(key => {
                const el = document.getElementById(`${t}-${key}`);
                if (el) el.value = item[key];
            });

            document.getElementById(`modal-${t}`).classList.remove('hidden');
        }

        async function saveRecord(event, t) {
            event.preventDefault();
            const id = document.getElementById(`${t}-id`).value;
            const formData = {};

            // Collect form field inputs
            const fieldsR = ["name", "title", "branch", "hire_date", "resign_date", "last_day", "net_pay", "reason", "manager", "recipient"];
            const fieldsH = ["name", "title", "branch", "hire_date", "grading", "education", "age", "address", "experience", "manager", "recipient", "basic", "allowance", "kpi"];
            
            const fieldList = t === 'r' ? fieldsR : fieldsH;
            fieldList.forEach(k => {
                const val = document.getElementById(`${t}-${k}`)?.value;
                formData[k] = val;
            });

            const method = id ? 'PUT' : 'POST';
            const url = id ? `/api/${t}/${id}` : `/api/${t}`;

            try {
                const res = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                if (res.ok) {
                    showToast('تم حفظ البيانات بنجاح', 'success');
                    closeModal(t);
                    await loadData(t);
                } else {
                    const err = await res.json();
                    showToast(err.detail || 'حدث خطأ أثناء الحفظ', 'error');
                }
            } catch (e) {
                showToast('تعذر الاتصال بالخادم', 'error');
            }
        }

        async function changeStatus(t, id, status) {
            try {
                const res = await fetch(`/api/${t}/${id}/status/${status}`, { method: 'POST' });
                if (res.ok) {
                    showToast(`تم تغيير الحالة إلى ${status === 'Approved' ? 'مقبول' : 'مرفوض'}`, 'success');
                    await loadData(t);
                }
            } catch (e) {
                showToast('فشل تعديل الحالة', 'error');
            }
        }

        async function deleteRecord(t, id) {
            if (!confirm('هل أنت تأكد من رغبتك في حذف هذا السجل؟')) return;
            try {
                const res = await fetch(`/api/${t}/${id}`, { method: 'DELETE' });
                if (res.ok) {
                    showToast('تم حذف السجل بنجاح', 'success');
                    await loadData(t);
                }
            } catch (e) {
                showToast('فشل حذف السجل', 'error');
            }
        }

        // 8. Preview HTML Email Template Modal
        function openPreviewModal(t, id) {
            state.activePreview = { t, i: id };
            document.getElementById('preview-note-input').value = '';
            refreshPreviewFrame();
            document.getElementById('modal-preview').classList.remove('hidden');
        }

        function refreshPreviewFrame() {
            const { t, i } = state.activePreview;
            if (!t || !i) return;
            const note = encodeURIComponent(document.getElementById('preview-note-input').value || '');
            document.getElementById('preview-iframe').src = `/api/${t}/${i}/preview?note=${note}`;
        }

        function closePreviewModal() {
            document.getElementById('modal-preview').classList.add('hidden');
        }

        // 9. Send Email Modal
        function triggerSendEmailModal() {
            const { t, i } = state.activePreview;
            const item = state[t].find(x => x.id === i);
            if (item) {
                document.getElementById('mail-subject').value = `${t === 'r' ? 'Resignation' : 'New Hire'} Approval Request - ${item.name}`;
            }
            document.getElementById('modal-mail-send').classList.remove('hidden');
        }

        function closeMailSendModal() {
            document.getElementById('modal-mail-send').classList.add('hidden');
        }

        async function executeSendMail(e) {
            e.preventDefault();
            const { t, i } = state.activePreview;
            const payload = {
                to: document.getElementById('mail-to').value,
                cc: document.getElementById('mail-cc').value,
                subject: document.getElementById('mail-subject').value,
                note: document.getElementById('mail-note').value
            };

            try {
                const res = await fetch(`/api/${t}/${i}/mail`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    showToast('تم إرسال البريد الإلكتروني بنجاح', 'success');
                    closeMailSendModal();
                } else {
                    const err = await res.json();
                    showToast(err.detail || 'فشل إرسال البريد', 'error');
                }
            } catch (e) {
                showToast('تعذر الاتصال بالسيرفر لإرسال الإيميل', 'error');
            }
        }

        // 10. Restore Database Upload
        async function uploadBackup(event) {
            const file = event.target.files[0];
            if (!file) return;

            if (!confirm('سيتم استبدال البيانات الحالية بالكامل بملف النسخة الاحتياطية. هل تريد المتابعة؟')) return;

            try {
                const arrayBuffer = await file.arrayBuffer();
                const res = await fetch('/api/restore', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/octet-stream' },
                    body: arrayBuffer
                });

                if (res.ok) {
                    showToast('تمت استعادة قاعدة البيانات بنجاح!', 'success');
                    await loadData('r');
                    await loadData('h');
                    await fetchSystemInfo();
                } else {
                    const err = await res.json();
                    showToast(err.detail || 'الملف غير صالح', 'error');
                }
            } catch (e) {
                showToast('فشلت عملية الاستعادة', 'error');
            }
        }

        // 11. Render Analytical Charts (Chart.js)
        function renderCharts() {
            // Chart 1: Resignations vs Hires Comparison
            const ctx1 = document.getElementById('chart-comparison').getContext('2d');
            if (chartComparisonInstance) chartComparisonInstance.destroy();

            chartComparisonInstance = new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: ['إجمالي السجلات', 'معلقة Pending', 'مقبولة Approved', 'مرفوضة Rejected'],
                    datasets: [
                        {
                            label: 'التعيينات الجديدة',
                            data: [
                                state.h.length,
                                state.h.filter(x => x.status === 'Pending').length,
                                state.h.filter(x => x.status === 'Approved').length,
                                state.h.filter(x => x.status === 'Rejected').length
                            ],
                            backgroundColor: '#10B981'
                        },
                        {
                            label: 'الاستقالات',
                            data: [
                                state.r.length,
                                state.r.filter(x => x.status === 'Pending').length,
                                state.r.filter(x => x.status === 'Approved').length,
                                state.r.filter(x => x.status === 'Rejected').length
                            ],
                            backgroundColor: '#EF4444'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });

            // Chart 2: Salary Component Breakdown
            const ctx2 = document.getElementById('chart-salaries').getContext('2d');
            if (chartSalariesInstance) chartSalariesInstance.destroy();

            const sumBasic = state.h.reduce((a, b) => a + (b.basic || 0), 0);
            const sumAllowance = state.h.reduce((a, b) => a + (b.allowance || 0), 0);
            const sumKpi = state.h.reduce((a, b) => a + (b.kpi || 0), 0);

            chartSalariesInstance = new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: ['الرواتب الأساسية', 'البدلات', 'الحوافز KPI'],
                    datasets: [{
                        data: [sumBasic, sumAllowance, sumKpi],
                        backgroundColor: ['#8C5A2B', '#C08A4B', '#EADBCE']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }

        // Helper Utilities
        function escapeHtml(str) {
            return String(str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        }

        function showToast(msg, type = 'info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            const bg = type === 'success' ? 'bg-emerald-800 text-white' : type === 'error' ? 'bg-red-800 text-white' : 'bg-brand-900 text-white';
            
            toast.className = `${bg} px-4 py-3 rounded-xl shadow-xl text-xs font-bold flex items-center gap-2 transform transition-all duration-300 translate-y-2 opacity-0`;
            toast.innerHTML = `<i class="fa-solid fa-circle-info"></i> <span>${escapeHtml(msg)}</span>`;
            
            container.appendChild(toast);
            setTimeout(() => {
                toast.classList.remove('translate-y-2', 'opacity-0');
            }, 10);

            setTimeout(() => {
                toast.classList.add('opacity-0');
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }
    </script>
</body>
</html>
