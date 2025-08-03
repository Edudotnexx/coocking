# 🔍 کانفیگ یاب حرفه‌ای

<div dir="rtl">

یک ابزار قدرتمند و حرفه‌ای برای یافتن و تست سریعترین کانفیگ‌های رایگان VPN با استفاده از Python Backend و Web Frontend.

## ✨ ویژگی‌ها

### 🚀 عملکرد بالا
- دریافت خودکار کانفیگ‌ها از منابع متعدد
- تست همزمان با AsyncIO برای سرعت بالا
- Real-time updates با WebSocket
- کش کردن نتایج برای بهبود عملکرد

### 🔧 پشتیبانی کامل از پروتکل‌ها
- ✅ VMess
- ✅ VLess
- ✅ Shadowsocks (SS)
- ✅ Trojan
- 🔄 ShadowsocksR (SSR) - در حال توسعه
- 🔄 Hysteria - در حال توسعه
- 🔄 WireGuard - در حال توسعه

### 🎯 تست دقیق و سریع
- Ping Test (ICMP & TCP)
- HTTP Response Time
- Packet Loss Detection
- سیستم امتیازدهی هوشمند
- ترتیب‌بندی بر اساس سرعت و پایداری

### 🌐 رابط کاربری مدرن
- طراحی ریسپانسیو و زیبا
- Dark/Light Theme
- نمایش آمار Real-time
- QR Code Generator
- فیلتر پیشرفته

### 🤖 خودکارسازی
- GitHub Actions Integration
- Scheduled Updates
- Auto Config Detection
- Smart Retry Logic

## 🛠️ نصب و راه‌اندازی

### پیش‌نیازها
```bash
Python 3.8+
pip (Python Package Manager)
```

### مرحله 1: کلون کردن پروژه
```bash
git clone https://github.com/your-username/ConfigFinder.git
cd ConfigFinder
```

### مرحله 2: نصب Dependencies
```bash
pip install -r requirements.txt
```

### مرحله 3: اجرای سرور
```bash
python api_server.py
```

### مرحله 4: دسترسی به وب اپلیکیشن
```
http://localhost:8080
```

## 📋 راهنمای استفاده

### 1️⃣ دریافت کانفیگ‌ها
- منبع مورد نظر را انتخاب کنید
- روی دکمه "دریافت کانفیگ‌ها" کلیک کنید
- منتظر تکمیل دریافت باشید

### 2️⃣ تست کانفیگ‌ها
- برای تست همه: دکمه "تست همه" را کلیک کنید
- برای تست منفرد: روی دکمه "تست" در هر کارت کلیک کنید

### 3️⃣ استفاده از کانفیگ‌ها
- **کپی**: روی دکمه کپی کلیک کنید
- **QR Code**: برای اسکن با موبایل
- **جزئیات**: مشاهده اطلاعات کامل

### 4️⃣ فیلتر کردن
- **همه**: نمایش همه کانفیگ‌ها
- **فعال**: فقط کانفیگ‌های سریع
- **کند**: کانفیگ‌های با تاخیر
- **غیرفعال**: کانفیگ‌های از کار افتاده

## 🔧 پیکربندی پیشرفته

### تنظیم منابع کانفیگ
فایل `config_core.py` را ویرایش کنید:

```python
sources = {
    'custom_source': 'https://your-config-source.com/configs.txt'
}
```

### تنظیم پارامترهای تست
فایل `config_tester.py`:

```python
class ConfigTester:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent  # تعداد تست همزمان
```

### تنظیم سرور
فایل `api_server.py`:

```python
api = ConfigFinderAPI(host="0.0.0.0", port=8080)
```

## 🔌 API Documentation

### Endpoints اصلی

#### `GET /api/configs`
دریافت لیست کانفیگ‌ها

**Query Parameters:**
- `status`: فیلتر بر اساس وضعیت (all, active, slow, dead, untested)
- `limit`: تعداد نتایج (پیش‌فرض: 100)
- `offset`: شروع از رکورد (پیش‌فرض: 0)

**Response:**
```json
{
    "configs": [...],
    "total": 150,
    "offset": 0,
    "limit": 100
}
```

#### `POST /api/configs/fetch`
دریافت کانفیگ‌های جدید

**Body:**
```json
{
    "source": "vmess_iran"
}
```

#### `POST /api/configs/test`
تست همه کانفیگ‌ها

#### `GET /api/configs/{id}/test`
تست یک کانفیگ خاص

#### `GET /api/stats`
دریافت آمار کلی

**Response:**
```json
{
    "total": 150,
    "active": 45,
    "slow": 30,
    "dead": 60,
    "untested": 15
}
```

#### `GET /api/ws`
WebSocket connection برای real-time updates

## 🧪 تست و توسعه

### اجرای تست‌ها
```bash
python -m pytest tests/
```

### تست مستقل کلاس‌ها
```bash
# تست دریافت کانفیگ‌ها
python config_core.py

# تست سیستم تست
python config_tester.py

# تست API سرور
python api_server.py
```

## 🐳 Docker Support

### Build Image
```bash
docker build -t config-finder .
```

### اجرا با Docker
```bash
docker run -p 8080:8080 config-finder
```

### Docker Compose
```bash
docker-compose up -d
```

## 🤖 GitHub Actions

### Automated Updates
فایل `.github/workflows/update-configs.yml`:

```yaml
name: Update Configs
on:
  schedule:
    - cron: '0 */6 * * *'  # هر 6 ساعت
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Update configs
        run: python scripts/update_configs.py
      - name: Commit results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Auto update configs" || exit 0
          git push
```

## 🔒 امنیت

### Best Practices
- استفاده از HTTPS در production
- Rate limiting برای API
- Input validation
- Secure headers

### مدیریت دسترسی
```python
# در آینده - Authentication
headers = {
    'Authorization': 'Bearer your-token'
}
```

## 📊 مانیتورینگ

### Logs
```bash
tail -f logs/config_finder.log
```

### Metrics
- تعداد کانفیگ‌های دریافتی
- نرخ موفقیت تست‌ها
- میانگین زمان پاسخ
- آپتایم سرور

## 🚀 Performance Tips

### بهینه‌سازی تعداد تست همزمان
```python
# برای سرورهای قدرتمند
tester = ConfigTester(max_concurrent=20)

# برای سیستم‌های محدود
tester = ConfigTester(max_concurrent=5)
```

### کش کردن نتایج
```python
# فعال‌سازی کش 1 ساعته
CACHE_TTL = 3600  # ثانیه
```

## 🔄 Updates

### بروزرسانی خودکار
```bash
git pull origin main
pip install -r requirements.txt --upgrade
python api_server.py
```

### Migration راهنما
هنگام بروزرسانی، فایل `CHANGELOG.md` را بخوانید.

## 🛠️ Troubleshooting

### مشکلات رایج

#### خطای اتصال به منابع
```bash
# بررسی اتصال اینترنت
ping google.com

# بررسی دسترسی به منابع
curl -I https://raw.githubusercontent.com/...
```

#### خطای نصب Dependencies
```bash
# نصب مجدد
pip install --force-reinstall -r requirements.txt

# استفاده از virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### خطای پورت در حال استفاده
```bash
# تغییر پورت
python api_server.py --port 8081

# یا قتل پروسه
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

## 🤝 مشارکت

### راهنمای مشارکت
1. Fork کردن پروژه
2. ایجاد branch جدید
3. اعمال تغییرات
4. ارسال Pull Request

### Code Style
```bash
# استفاده از Black formatter
black *.py

# لین کردن با flake8
flake8 *.py
```

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر فایل `LICENSE` را ببینید.

## 👨‍💻 سازنده

**توسعه‌دهنده:** [@Itsthemoein](https://t.me/Itsthemoein)

**کانال تلگرام:** [@Sourrce_kade](https://t.me/Sourrce_kade)

## 🙏 تشکر

از تمامی منابع و کتابخانه‌های استفاده شده در این پروژه تشکر می‌کنیم:
- aiohttp
- TailwindCSS  
- Font Awesome
- QR Code JS

## 🔗 لینک‌های مفید

- [مستندات Python AsyncIO](https://docs.python.org/3/library/asyncio.html)
- [راهنمای aiohttp](https://docs.aiohttp.org/)
- [TailwindCSS](https://tailwindcss.com/)
- [VMess Protocol](https://www.v2ray.com/chapter_02/protocols/vmess.html)

## 📈 Roadmap

### نسخه 1.1
- [ ] پشتیبانی از ShadowsocksR
- [ ] Hysteria Protocol
- [ ] Advanced Analytics
- [ ] User Management

### نسخه 1.2  
- [ ] Mobile App (React Native)
- [ ] Desktop App (Electron)
- [ ] Machine Learning Optimization
- [ ] Multi-language Support

### نسخه 2.0
- [ ] Distributed Testing
- [ ] Advanced Monitoring
- [ ] Commercial Features
- [ ] Cloud Integration

---

**⭐ اگر از این پروژه استفاده می‌کنید، لطفاً ستاره بدهید!**

</div>
