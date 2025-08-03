# 📋 راهنمای تنظیم سابسکریپشن - کانفیگ یاب حرفه‌ای

## 🎯 مکان‌های تنظیم سابسکریپشن

### 1️⃣ فایل اصلی: `config_core.py`

```python
# خط 62-70 در config_core.py
self.sources = {
    'vmess_iran': 'https://raw.githubusercontent.com/Farid-Karimi/Config-Collector/main/vmess_iran.txt',
    'mixed_iran': 'https://raw.githubusercontent.com/Farid-Karimi/Config-Collector/main/mixed_iran.txt',
    'arshia_mix': 'https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/mix/sub.html',
    'arshia_ss': 'https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/ss.html',
    'arshia_vless': 'https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/vless.html'
}
```

### 2️⃣ فایل Frontend: `index.html`

```html
<!-- خط 630 در index.html -->
<select id="configType" class="px-4 py-2 bg-gray-800...">
    <option value="vmess_iran" selected>VMess ایران</option>
    <option value="mixed_iran">میکس ایران</option>
    <option value="arshia_mix">میکس Arshia</option>
    <option value="arshia_ss">Shadowsocks Arshia</option>
    <option value="arshia_vless">VLess Arshia</option>
</select>
```

## ➕ اضافه کردن سابسکریپشن جدید

### مرحله 1: Backend (Python)

```python
# در فایل config_core.py
self.sources = {
    # سابسکریپشن‌های موجود...
    
    # سابسکریپشن جدید شما
    'my_custom_source': 'https://your-domain.com/configs.txt',
    'telegram_channel': 'https://t.me/s/your_channel',
    'another_source': 'https://pastebin.com/raw/your_paste_id',
}
```

### مرحله 2: Frontend (HTML)

```html
<!-- اضافه کردن به dropdown -->
<option value="my_custom_source">سابسکریپشن من</option>
<option value="telegram_channel">کانال تلگرام</option>
<option value="another_source">منبع دیگر</option>
```

## 🔀 انواع منابع پشتیبانی شده

### 📄 Plain Text (متن ساده)
```
vmess://eyJ2IjoiMiIsInBzIjoi...
vless://uuid@server:port?...
ss://base64encoded@server:port#name
trojan://password@server:port?...
```

### 🌐 HTML Sources
- صفحات وب حاوی کانفیگ
- کانال‌های تلگرام
- سایت‌های pasting

### 📊 Base64 Encoded
```
# محتوای encode شده
dmVzczovL2V5SjJJam9pTWlJc0luQnpJam9pLi4u
```

## ⚙️ تنظیمات پیشرفته

### 🔄 تنظیم Headers سفارشی

```python
# در فایل config_core.py - تابع __aenter__
self.session = aiohttp.ClientSession(
    timeout=aiohttp.ClientTimeout(total=30),
    headers={
        'User-Agent': 'ConfigFinder/1.0',
        'Accept': 'text/plain,text/html',
        'Authorization': 'Bearer your-token',  # اگر نیاز باشد
    }
)
```

### 🚦 Rate Limiting

```python
# تاخیر بین درخواست‌ها
import asyncio

async def fetch_with_delay(self, url, delay=1):
    await asyncio.sleep(delay)
    # درخواست اصلی...
```

### 🔒 Authentication

```python
# برای منابع محافظت شده
async def fetch_protected(self, url, token):
    headers = {'Authorization': f'Bearer {token}'}
    async with self.session.get(url, headers=headers) as response:
        # پردازش...
```

## 📝 فرمت‌های مختلف

### 🎯 JSON Format
```json
{
    "configs": [
        {
            "name": "Server 1",
            "config": "vmess://...",
            "country": "Iran"
        }
    ]
}
```

### 📋 Custom Parser

```python
def parse_custom_format(self, content):
    """پارس فرمت سفارشی"""
    configs = []
    
    # پارس JSON
    if content.startswith('{'):
        data = json.loads(content)
        for item in data.get('configs', []):
            configs.append(item['config'])
    
    # پارس CSV
    elif ',' in content:
        lines = content.split('\n')
        for line in lines:
            parts = line.split(',')
            if len(parts) >= 2:
                configs.append(parts[1])  # config در ستون دوم
    
    return configs
```

## 🌍 منابع پیشنهادی

### 🔗 منابع رایگان معتبر

```python
RECOMMENDED_SOURCES = {
    # GitHub Repositories
    'v2ray_configs': 'https://raw.githubusercontent.com/username/repo/main/configs.txt',
    
    # Telegram Channels
    'free_configs': 'https://t.me/s/free_v2ray_configs',
    
    # Paste Sites
    'pastebin_source': 'https://pastebin.com/raw/paste_id',
    
    # Custom APIs
    'api_source': 'https://api.yoursite.com/configs',
}
```

### ⚠️ نکات امنیتی

1. **اعتماد به منابع**: فقط از منابع معتبر استفاده کنید
2. **Rate Limiting**: خیلی زیاد درخواست نفرستید
3. **Validation**: همیشه کانفیگ‌ها را validate کنید
4. **Privacy**: از IP شخصی خود محافظت کنید

## 🛠️ ابزارهای کمکی

### 📊 تست منبع جدید

```bash
# تست دستی URL
curl -H "User-Agent: ConfigFinder/1.0" https://your-source.com/configs.txt

# بررسی encoding
file your-configs.txt

# تست decode base64
echo "base64string" | base64 -d
```

### 🔍 Debug Mode

```python
# فعال‌سازی لاگ‌های تفصیلی
import logging
logging.basicConfig(level=logging.DEBUG)

# در config_core.py
logger.debug(f"Fetching from: {url}")
logger.debug(f"Response: {content[:100]}...")
```

## 📱 تنظیم از طریق UI (آینده)

در نسخه‌های بعدی می‌توانید سابسکریپشن را از رابط کاربری اضافه کنید:

```javascript
// آینده - اضافه کردن از UI
async function addSubscription() {
    const url = document.getElementById('newSubscriptionUrl').value;
    const name = document.getElementById('newSubscriptionName').value;
    
    const response = await fetch('/api/subscriptions', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url, name})
    });
    
    if (response.ok) {
        alert('سابسکریپشن اضافه شد!');
        loadSubscriptions();
    }
}
```

## 🚀 اجرای پس از تغییر

```bash
# بعد از تغییر سابسکریپشن‌ها
cd "c:\Users\Emad\Desktop\Project x\ConfigFinder"

# ری‌استارت سرور
python run.py
```

هر سوالی درباره تنظیم سابسکریپشن داشتی بپرس! 😊
