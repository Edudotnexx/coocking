#!/usr/bin/env python3
"""
اسکریپت تست کانفیگ‌ها برای GitHub Actions
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

# اضافه کردن مسیر اصلی به sys.path
sys.path.append(str(Path(__file__).parent.parent))

from config_core import ConfigResult
from config_tester import ConfigTester

async def main():
    parser = argparse.ArgumentParser(description='تست کانفیگ‌ها')
    parser.add_argument('--input', required=True, help='فایل ورودی JSON')
    parser.add_argument('--output', required=True, help='فایل خروجی JSON')
    parser.add_argument('--limit', type=int, default=20, help='حداکثر تعداد کانفیگ برای تست')
    parser.add_argument('--concurrent', type=int, default=5, help='تعداد تست همزمان')
    
    args = parser.parse_args()
    
    print(f"🔬 شروع تست کانفیگ‌ها...")
    
    try:
        # خواندن کانفیگ‌ها
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        configs_data = data.get('configs', [])
        
        if not configs_data:
            print("⚠️  هیچ کانفیگی برای تست یافت نشد")
            return
        
        # تبدیل به ConfigResult objects
        configs = []
        for i, config_data in enumerate(configs_data[:args.limit]):
            config = ConfigResult(
                id=i,
                name=config_data.get('name', f'Server {i}'),
                server=config_data.get('server', ''),
                port=config_data.get('port', 443),
                protocol=config_data.get('protocol', 'unknown'),
                config_url=config_data.get('config_url', ''),
                status='untested'
            )
            configs.append(config)
        
        print(f"📋 تعداد کانفیگ‌ها برای تست: {len(configs)}")
        
        # تست کانفیگ‌ها
        tester = ConfigTester(max_concurrent=args.concurrent)
        
        async def progress_callback(config_id: int, message: str):
            print(f"🔄 کانفیگ {config_id}: {message}")
        
        test_results = await tester.test_multiple_configs(configs, progress_callback)
        
        # بروزرسانی کانفیگ‌ها با نتایج
        updated_configs = tester.update_configs_with_results(configs, test_results)
        
        # محاسبه آمار
        stats = {
            'total': len(updated_configs),
            'active': 0,
            'slow': 0, 
            'dead': 0,
            'untested': 0
        }
        
        for config in updated_configs:
            if config.status in stats:
                stats[config.status] += 1
        
        # ذخیره نتایج
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'test_params': {
                'total_configs': len(configs_data),
                'tested_configs': len(updated_configs),
                'concurrent_tests': args.concurrent
            },
            'stats': stats,
            'configs': [config.to_dict() for config in updated_configs],
            'test_results': [
                {
                    'config_id': result.config_id,
                    'status': result.status,
                    'ping': result.ping,
                    'response_time': result.response_time,
                    'error_message': result.error_message,
                    'test_time': result.test_time.isoformat() if result.test_time else None
                }
                for result in test_results
            ]
        }
        
        # ذخیره در فایل
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ نتایج تست ذخیره شد در {args.output}")
        
        # نمایش آمار نهایی
        print("\n📊 آمار نهایی:")
        print(f"  ✅ فعال: {stats['active']}")
        print(f"  ⚠️  کند: {stats['slow']}")
        print(f"  ❌ غیرفعال: {stats['dead']}")
        print(f"  ❓ تست نشده: {stats['untested']}")
        
        # محاسبه نرخ موفقیت
        tested = stats['active'] + stats['slow'] + stats['dead']
        if tested > 0:
            success_rate = (stats['active'] + stats['slow']) / tested * 100
            print(f"  📈 نرخ موفقیت: {success_rate:.1f}%")
            
    except Exception as e:
        print(f"❌ خطا در تست کانفیگ‌ها: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
