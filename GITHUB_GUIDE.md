# 🚀 راهنمای آپلود به GitHub - کانفیگ یاب حرفه‌ای

## 📋 مراحل آپلود

### روش 1: GitHub Desktop (ساده‌ترین)

1. **نصب GitHub Desktop**
   - دانلود از: https://desktop.github.com/
   - نصب و وارد شدن با اکانت GitHub

2. **ایجاد Repository جدید**
   - File → New Repository
   - نام: `ConfigFinder`
   - توضیحات: `🔍 کانفیگ یاب حرفه‌ای - ابزار قدرتمند یافتن و تست کانفیگ‌های VPN`
   - مسیر: `c:\Users\Emad\Desktop\Project x\ConfigFinder`

3. **Publish به GitHub**
   - دکمه "Publish repository"
   - تیک "Public" را بردارید اگر می‌خواهید private باشد
   - کلیک "Publish repository"

### روش 2: GitHub Web Interface

1. **ایجاد Repository در وب**
   - برو به: https://github.com/new
   - نام: `ConfigFinder`
   - توضیحات: `🔍 کانفیگ یاب حرفه‌ای - ابزار قدرتمند یافتن و تست کانفیگ‌های VPN`
   - Public یا Private انتخاب کن
   - README.md را تیک بزن
   - کلیک "Create repository"

2. **آپلود فایل‌ها**
   - کلیک "uploading an existing file"
   - تمام فایل‌های پروژه را drag & drop کن
   - Commit message: `🎉 Initial commit - ConfigFinder v1.0`

### روش 3: Git Command Line (اگر git نصب کنی)

```bash
# نصب Git از: https://git-scm.com/download/win

cd "c:\Users\Emad\Desktop\Project x\ConfigFinder"
git init
git add .
git commit -m "🎉 Initial commit - ConfigFinder v1.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ConfigFinder.git
git push -u origin main
```

## 🔧 تنظیمات Repository

### 📄 فایل‌های ضروری (موجود است)

- ✅ `README.md` - توضیحات کامل پروژه
- ✅ `requirements.txt` - Dependencies
- ✅ `Dockerfile` - برای Docker
- ✅ `docker-compose.yml` - راه‌اندازی آسان
- ✅ `.gitignore` - فایل‌های ignore شده
- ✅ `TODO.md` - برنامه توسعه

### ⚙️ تنظیمات GitHub

1. **Settings → General**
   - Features: Issues, Discussions فعال کن
   - Pull Requests فعال کن

2. **Settings → Pages** (اختیاری)
   - Source: GitHub Actions
   - برای deploy خودکار

3. **Settings → Secrets and Variables**
   - اضافه کردن secrets برای Telegram:
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHAT_ID`

## 🤖 فعال‌سازی GitHub Actions

### 1. ایجاد Bot تلگرام (اختیاری)

1. پیام به @BotFather در تلگرام
2. `/newbot`
3. نام bot: `ConfigFinder Bot`
4. Username: `configfinder_[yourname]_bot`
5. Token را کپی کن

### 2. تنظیم Secrets

در GitHub repository:
- Settings → Secrets and variables → Actions
- New repository secret:
  - نام: `TELEGRAM_BOT_TOKEN`
  - مقدار: token bot
  - نام: `TELEGRAM_CHAT_ID`
  - مقدار: chat ID شما

### 3. تست Action

فایل workflow ما خودکار هر 6 ساعت اجرا می‌شه یا می‌تونی دستی اجرا کنی:
- Actions → Update Configs → Run workflow

## 📱 استفاده از پروژه

### 🌐 GitHub Pages (آینده)

پروژه رو می‌تونی روی GitHub Pages هم deploy کنی:

```yaml
# در .github/workflows/pages.yml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v3
      - uses: actions/upload-pages-artifact@v2
        with:
          path: ./
      - uses: actions/deploy-pages@v2
```

### 🔗 دسترسی مستقیم

بعد از آپلود، کاربران می‌تونن:

```bash
# کلون کردن
git clone https://github.com/YOUR_USERNAME/ConfigFinder.git

# اجرا
cd ConfigFinder
pip install -r requirements.txt
python run.py
```

### 📦 Release خودکار

GitHub Action ما خودکار release می‌سازه که شامل:
- `configs.json` - آخرین کانفیگ‌ها
- `test_results.json` - نتایج تست
- `report.md` - گزارش کامل

## 🎯 نکات مهم

### 🔒 امنیت

1. **Secrets**: هیچوقت token ها رو commit نکن
2. **Private Info**: اطلاعات شخصی رو در .gitignore بذار
3. **API Keys**: از GitHub Secrets استفاده کن

### 📈 بهینه‌سازی

1. **فایل‌های بزرگ**: از Git LFS استفاده کن
2. **Cache**: Dependencies رو cache کن
3. **Release**: فقط فایل‌های ضروری رو release کن

### 🌟 جذابیت

1. **README**: بیشتر emoji و عکس اضافه کن
2. **Topics**: تگ‌های مرتبط اضافه کن:
   - `vpn`, `v2ray`, `shadowsocks`, `proxy`, `iran`
3. **License**: MIT License اضافه کن

## 📞 بعد از آپلود

1. **لینک GitHub**: تو توضیحات تلگرام بذار
2. **ستاره**: از دوستات بخواه ستاره بدن
3. **Share**: تو کانال‌ها معرفی کن

---

**🎉 موفق باشی! پروژه خیلی خفنی شده!**
