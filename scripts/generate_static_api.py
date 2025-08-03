#!/usr/bin/env python3
"""
تولید API استاتیک برای GitHub Pages
"""

import json
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='تولید API استاتیک')
    parser.add_argument('--configs', required=True, help='فایل کانفیگ‌ها')
    parser.add_argument('--output', required=True, help='مسیر خروجی API')
    
    args = parser.parse_args()
    
    try:
        # خواندن کانفیگ‌ها
        with open(args.configs, 'r', encoding='utf-8') as f:
            configs_data = json.load(f)
        
        # ایجاد مسیر خروجی
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # تولید API endpoints
        
        # 1. فایل کانفیگ‌ها
        configs_api = {
            'status': 'success',
            'data': configs_data,
            'timestamp': configs_data.get('timestamp', ''),
            'total': configs_data.get('total_configs', 0)
        }
        
        with open(output_path / 'configs.json', 'w', encoding='utf-8') as f:
            json.dump(configs_api, f, ensure_ascii=False, indent=2)
        
        # 2. آمار پروتکل‌ها
        protocols = {}
        for config in configs_data.get('configs', []):
            protocol = config.get('protocol', 'unknown')
            protocols[protocol] = protocols.get(protocol, 0) + 1
        
        stats_api = {
            'status': 'success',
            'data': {
                'protocols': protocols,
                'total_configs': len(configs_data.get('configs', [])),
                'timestamp': configs_data.get('timestamp', '')
            }
        }
        
        with open(output_path / 'stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats_api, f, ensure_ascii=False, indent=2)
        
        # 3. فایل index برای لیست endpoint ها
        index_api = {
            'status': 'success',
            'endpoints': [
                '/api/configs.json',
                '/api/stats.json'
            ],
            'description': 'کانفیگ یاب حرفه‌ای API',
            'version': '1.0.0'
        }
        
        with open(output_path / 'index.json', 'w', encoding='utf-8') as f:
            json.dump(index_api, f, ensure_ascii=False, indent=2)
        
        print(f"✅ API استاتیک در {args.output} تولید شد")
        print(f"📊 {len(protocols)} پروتکل و {len(configs_data.get('configs', []))} کانفیگ")
        
    except Exception as e:
        print(f"❌ خطا در تولید API: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())