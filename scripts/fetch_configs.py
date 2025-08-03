#!/usr/bin/env python3
"""
اسکریپت دریافت کانفیگ‌ها برای GitHub Actions
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path

# اضافه کردن مسیر اصلی به sys.path
sys.path.append(str(Path(__file__).parent.parent))

from config_core import ConfigProcessor

async def main():
    parser = argparse.ArgumentParser(description='دریافت کانفیگ‌ها')
    parser.add_argument('--source', default='all', help='منبع کانفیگ')
    parser.add_argument('--output', required=True, help='فایل خروجی JSON')
    parser.add_argument('--limit', type=int, default=100, help='حداکثر تعداد کانفیگ')
    
    args = parser.parse_args()
    
    print(f"🚀 شروع دریافت کانفیگ‌ها از منبع: {args.source}")
    
    try:
        # دریافت کانفیگ‌ها
        processor = ConfigProcessor()
        configs = await processor.process_all_sources()
        
        # محدود کردن تعداد
        if args.limit and len(configs) > args.limit:
            configs = configs[:args.limit]
            print(f"⚠️  محدود شده به {args.limit} کانفیگ")
        
        # تبدیل به JSON
        output_data = {
            'timestamp': '2025-08-03T12:00:00Z',
            'source': args.source,
            'total_configs': len(configs),
            'configs': [config.to_dict() for config in configs]
        }
        
        # ذخیره در فایل
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {len(configs)} کانفیگ ذخیره شد در {args.output}")
        
        # نمایش آمار
        protocols = {}
        for config in configs:
            protocol = config.protocol
            protocols[protocol] = protocols.get(protocol, 0) + 1
        
        print("\n📊 آمار پروتکل‌ها:")
        for protocol, count in protocols.items():
            print(f"  {protocol}: {count}")
            
    except Exception as e:
        print(f"❌ خطا در دریافت کانفیگ‌ها: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
