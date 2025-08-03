#!/usr/bin/env python3
"""
تولید گزارش از کانفیگ‌ها و نتایج تست
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='تولید گزارش')
    parser.add_argument('--configs', required=True, help='فایل کانفیگ‌ها')
    parser.add_argument('--tests', help='فایل نتایج تست')
    parser.add_argument('--output', required=True, help='فایل خروجی Markdown')
    
    args = parser.parse_args()
    
    print("📋 تولید گزارش...")
    
    try:
        # خواندن کانفیگ‌ها
        with open(args.configs, 'r', encoding='utf-8') as f:
            configs_data = json.load(f)
        
        # خواندن نتایج تست (اختیاری)
        test_data = None
        if args.tests and Path(args.tests).exists():
            with open(args.tests, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        
        # تولید گزارش
        report = generate_report(configs_data, test_data)
        
        # ذخیره گزارش
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ گزارش ذخیره شد در {args.output}")
        
    except Exception as e:
        print(f"❌ خطا در تولید گزارش: {e}")

def generate_report(configs_data, test_data=None):
    """تولید گزارش Markdown"""
    
    # اطلاعات پایه
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    total_configs = len(configs_data.get('configs', []))
    
    report = f"""# 📊 گزارش کانفیگ یاب حرفه‌ای

**📅 زمان تولید:** {timestamp}

## 📈 خلاصه آمار

| آمار | تعداد |
|------|-------|
| 🔍 **کل کانفیگ‌ها** | {total_configs:,} |
"""
    
    # آمار تست (اگر موجود باشد)
    if test_data and 'stats' in test_data:
        stats = test_data['stats']
        report += f"""| ✅ **فعال** | {stats.get('active', 0):,} |
| ⚠️ **کند** | {stats.get('slow', 0):,} |
| ❌ **غیرفعال** | {stats.get('dead', 0):,} |
| ❓ **تست نشده** | {stats.get('untested', 0):,} |

"""
        
        # محاسبه نرخ موفقیت
        tested = stats.get('active', 0) + stats.get('slow', 0) + stats.get('dead', 0)
        if tested > 0:
            success_rate = (stats.get('active', 0) + stats.get('slow', 0)) / tested * 100
            report += f"**📊 نرخ موفقیت:** {success_rate:.1f}%\n\n"
    else:
        report += "\n"
    
    # آمار پروتکل‌ها
    protocols = {}
    countries = {}
    
    for config in configs_data.get('configs', []):
        protocol = config.get('protocol', 'unknown')
        protocols[protocol] = protocols.get(protocol, 0) + 1
        
        country = config.get('country', 'نامشخص')
        countries[country] = countries.get(country, 0) + 1
    
    report += "## 🔧 آمار پروتکل‌ها\n\n"
    report += "| پروتکل | تعداد | درصد |\n"
    report += "|---------|-------|-------|\n"
    
    for protocol, count in sorted(protocols.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_configs) * 100 if total_configs > 0 else 0
        protocol_emoji = {
            'vmess': '🔵',
            'vless': '🟣', 
            'shadowsocks': '🟢',
            'trojan': '🔴',
            'unknown': '⚪'
        }.get(protocol, '⚪')
        
        report += f"| {protocol_emoji} {protocol.title()} | {count:,} | {percentage:.1f}% |\n"
    
    # کشورها (اگر اطلاعات موجود باشد)
    if any(country != 'نامشخص' for country in countries.keys()):
        report += "\n## 🌍 آمار کشورها\n\n"
        report += "| کشور | تعداد |\n"
        report += "|-------|-------|\n"
        
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
            if country != 'نامشخص':
                report += f"| {country} | {count:,} |\n"
    
    # بهترین کانفیگ‌ها (اگر تست شده باشند)
    if test_data and 'configs' in test_data:
        active_configs = [
            config for config in test_data['configs'] 
            if config.get('status') == 'active' and config.get('ping')
        ]
        
        if active_configs:
            # مرتب‌سازی بر اساس پینگ
            active_configs.sort(key=lambda x: x.get('ping', 999999))
            top_configs = active_configs[:10]
            
            report += "\n## 🚀 بهترین کانفیگ‌ها (کمترین پینگ)\n\n"
            report += "| رتبه | نام | سرور | پینگ | پروتکل |\n"
            report += "|------|-----|-------|-------|----------|\n"
            
            for i, config in enumerate(top_configs, 1):
                name = config.get('name', 'نامشخص')[:30]
                server = config.get('server', 'نامشخص')[:20]
                ping = f"{config.get('ping', 0):.0f}ms"
                protocol = config.get('protocol', 'unknown')
                
                report += f"| {i} | {name} | {server} | {ping} | {protocol} |\n"
    
    # اطلاعات دانلود
    report += f"""

## 📥 دانلود

### فایل‌های موجود
- **configs.json** - تمام کانفیگ‌ها در فرمت JSON
"""
    
    if test_data:
        report += "- **test_results.json** - نتایج تست کانفیگ‌ها\n"
    
    report += """
### استفاده سریع

#### دانلود با curl
```bash
curl -O https://github.com/your-username/ConfigFinder/releases/latest/download/configs.json
```

#### دانلود با wget
```bash
wget https://github.com/your-username/ConfigFinder/releases/latest/download/configs.json
```

#### Python
```python
import requests
import json

response = requests.get('https://github.com/your-username/ConfigFinder/releases/latest/download/configs.json')
configs = response.json()
print(f"تعداد کانفیگ‌ها: {len(configs['configs'])}")
```

## 🔧 ابزارهای پیشنهادی

### کلاینت‌های VPN
- **v2rayN** (Windows)
- **v2rayNG** (Android) 
- **Shadowrocket** (iOS)
- **Clash** (همه پلتفرم‌ها)

### تست سرعت
```bash
# نصب speedtest-cli
pip install speedtest-cli

# تست سرعت
speedtest-cli
```

## ⚠️ توجهات مهم

1. **امنیت:** همیشه از منابع معتبر استفاده کنید
2. **قوانین:** قوانین محلی خود را رعایت کنید  
3. **استفاده منطقی:** از کانفیگ‌ها به طور معقول استفاده کنید
4. **بروزرسانی:** کانفیگ‌ها به طور مرتب بروزرسانی می‌شوند

## 📞 پشتیبانی

- **Telegram:** [@Itsthemoein](https://t.me/Itsthemoein)
- **کانال:** [@Sourrce_kade](https://t.me/Sourrce_kade)
- **GitHub:** [Issues](https://github.com/your-username/ConfigFinder/issues)

---

**🔄 آخرین بروزرسانی:** {timestamp}

**⭐ اگر مفید بود، ستاره بدهید!**
"""
    
    return report

if __name__ == '__main__':
    main()
