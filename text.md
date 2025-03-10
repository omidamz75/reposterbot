توضیح کلی پروژه:  
ورژن اول یک ربات تلگرامی مدیریت تبلیغات و ریپوست است که برای مدیران کانال‌ها طراحی شده است. 

### 2️⃣ قابلیت‌های کلیدی:  
✅ مدیریت بنرها: ذخیره، ویرایش، حذف و مشاهده بنرها با قابلیت دریافت لیست به‌صورت فایل تکست.  
✅ مدیریت کانال‌ها: اضافه، حذف و دریافت لیست کانال‌ها به‌صورت فایل تکست.  
✅ زمان‌بندی:  تعیین ساعات ارسال تبلیغات
✅ماژول لاگ‌گیری: هر ماژول لاگ جداگانه دارد که توسط ماژول مرکزی مدیریت می‌شود.  

ورژن های بعدی:
✅ زمان بندی پیشرفته: تعیین ساعات ارسال تبلیغات (روز و شب)، حذف تبلیغات قبلی قبل از ارسال جدید، فاصله ارسال و ارسال تصادفی و...
✅ گزارش‌گیری: ارسال گزارش فرایندهای روزانه.    
✅ سیستم نوتیفیکیشن داخلی: نمایش اعلان‌های مهم در ربات.  
✅ ماژول بکاپ‌گیری: جهت حفظ داده‌های مهم و بازیابی در مواقع ضروری.  
✅ داشبورد مدیریت: نمایش وضعیت اشتراک، تعداد تبلیغات، زمان‌بندی‌ها و سایر اطلاعات  
کاربران پروژه  

👤 مدیر ربات:  
- کنترل کامل بر ربات  
- تأیید یا رد کاربران جدید  
- مدیریت پرداخت‌ها و اشتراک‌ها  
- مانیتورینگ وضعیت کلی ربات  

👥 کاربران (مدیران کانال‌های تلگرامی):  
- ثبت‌نام و خرید اشتراک  
- مدیریت تبلیغات و کانال‌های خود  
- تنظیم زمان‌بندی ارسال تبلیغات  
- مشاهده گزارشات مربوط به تبلیغات  


ساختار پیشنهادی فایل‌ها و پوشه‌ها:  

/bot_project
│── main.py                    # نقطه ورود اصلی ربات (اجرای کلی پروژه)
│── config.py                   # تنظیمات عمومی پروژه و متغیرهای محیطی
│── .env                        # متغیرهای حساس مثل توکن ربات و دیتابیس
│── .gitignore                  # فایل‌هایی که در گیت ذخیره نمی‌شوند
│── requirements.txt            # لیست وابستگی‌های پروژه
│── README.md                   # توضیحات پروژه
│
├── core/                       # هسته اصلی پروژه
│   ├── database.py             # مدیریت ارتباط با دیتابیس مرکزی
│   ├── scheduler.py            # مدیریت زمان‌بندی تبلیغات
│   ├── event_handler.py        # مدیریت Event-Driven Architecture
│
├── modules/                    # ماژول‌های مستقل پروژه
│   ├── ads/                    # ماژول مدیریت تبلیغات
│   │   ├── models.py           # مدل‌های دیتابیس این ماژول
│   │   ├── handlers.py         # پردازش دستورات کاربران
│   │   ├── services.py         # پردازش و مدیریت تبلیغات
│   │   ├── init.py         # پیکربندی ماژول
│
│   ├── channels/               # ماژول مدیریت کانال‌ها
│   │   ├── models.py
│   │   ├── handlers.py
│   │   ├── services.py
│   │   ├── init.py
│
│   ├── scheduler/              # ماژول پیشرفته زمان‌بندی تبلیغات
│   │   ├── models.py
│   │   ├── handlers.py
│   │   ├── scheduler.py
│   │   ├── init.py
│
│   ├── logs/                   # ماژول مرکزی لاگ‌گیری
│   │   ├── log_manager.py      # مدیریت کلی لاگ‌ها
│   │   ├── logs/               # لاگ‌های تمامی ماژول‌ها در اینجا ذخیره می‌شوند
│   │   ├── init.py
│
│   ├── backup/                 # ماژول بکاپ‌گیری
│   │   ├── backup_manager.py   # مدیریت کلی بکاپ‌ها
│   │   ├── storage/            # فایل‌های بکاپ ذخیره‌شده
│   │   ├── init.py
│
│   ├── payments/               # ماژول مدیریت پرداخت و اشتراک
│   │   ├── models.py
│   │   ├── handlers.py
│   │   ├── init.py
│
│   ├── notifications/          # ماژول سیستم نوتیفیکیشن داخلی
│   │   ├── models.py
│   │   ├── handlers.py
│   │   ├── services.py
│   │   ├── init.py
│
│   ├── ui/                     # ماژول مدیریت کیبورد و پرسش و پاسخ‌ها
│   │   ├── keyboard_manager.py # مدیریت کلیدهای ربات
│   │   ├── dialogs.py          # متون پاسخ‌دهی ربات
│   │   ├── init.py
││
└── tests/                      # پوشه مربوط به تست‌های کل سیستم