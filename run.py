#!/usr/bin/env python3
"""
🚀 کانفیگ یاب حرفه‌ای - اجرای سریع
راه‌اندازی کل سیستم با یک دستور
"""

import asyncio
import argparse
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """بررسی وجود dependencies"""
    required_packages = ['aiohttp', 'aiohttp_cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("⚠️  پکیج‌های زیر نصب نشده‌اند:")
        for package in missing_packages:
            print(f"   - {package}")
        
        print("\n💡 برای نصب:")
        print("pip install -r requirements.txt")
        
        response = input("\n❓ آیا می‌خواهید االان نصب کنم? (y/n): ")
        if response.lower() in ['y', 'yes', 'بله']:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                print("✅ همه پکیج‌ها نصب شدند!")
            except subprocess.CalledProcessError:
                print("❌ خطا در نصب پکیج‌ها. لطفاً دستی نصب کنید.")
                sys.exit(1)
        else:
            sys.exit(1)

async def fetch_and_test():
    """دریافت و تست کانفیگ‌ها"""
    try:
        from config_core import ConfigProcessor
        from config_tester import ConfigTester
        
        print("🚀 شروع دریافت کانفیگ‌ها...")
        
        # دریافت کانفیگ‌ها
        processor = ConfigProcessor()
        configs = await processor.process_all_sources()
        
        if not configs:
            print("⚠️  هیچ کانفیگی یافت نشد!")
            return []
        
        print(f"✅ {len(configs)} کانفیگ دریافت شد")
        
        # تست نمونه‌ای از کانفیگ‌ها
        print("🧪 شروع تست نمونه...")
        
        # محدود کردن به 5 کانفیگ اول برای سرعت
        test_configs = configs[:5]
        
        tester = ConfigTester(max_concurrent=3)
        
        async def progress_callback(config_id: int, message: str):
            print(f"  🔄 کانفیگ {config_id}: {message}")
        
        test_results = await tester.test_multiple_configs(test_configs, progress_callback)
        
        # بروزرسانی کانفیگ‌ها
        updated_configs = tester.update_configs_with_results(configs, test_results)
        
        # نمایش نتایج
        active_count = sum(1 for c in updated_configs if c.status == 'active')
        print(f"✅ تست تمام شد - {active_count} کانفیگ فعال یافت شد")
        
        return updated_configs
        
    except Exception as e:
        print(f"❌ خطا در دریافت/تست: {e}")
        return []

async def start_server(host='localhost', port=8080, auto_open=True):
    """شروع سرور API"""
    try:
        from api_server import ConfigFinderAPI
        
        print(f"🚀 شروع سرور در http://{host}:{port}")
        
        api = ConfigFinderAPI(host=host, port=port)
        runner = await api.start_server()
        
        if auto_open:
            # باز کردن مرورگر
            try:
                webbrowser.open(f'http://{host}:{port}')
                print("🌐 مرورگر باز شد")
            except:
                print("⚠️  نتوانستم مرورگر را باز کنم")
        
        print("\n🎯 آماده! کلیدهای میانبر:")
        print("  Ctrl+C - توقف سرور")
        print("  F5 - رفرش صفحه")
        
        try:
            # نگه داشتن سرور
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 متوقف کردن سرور...")
        finally:
            await runner.cleanup()
            
    except Exception as e:
        print(f"❌ خطا در شروع سرور: {e}")

def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(
        description='🔍 کانفیگ یاب حرفه‌ای - اجرای سریع',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--host', default='localhost', help='آدرس سرور (پیش‌فرض: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='پورت سرور (پیش‌فرض: 8080)')
    parser.add_argument('--no-browser', action='store_true', help='مرورگر را باز نکن')
    parser.add_argument('--skip-test', action='store_true', help='تست اولیه را انجام نده')
    parser.add_argument('--fetch-only', action='store_true', help='فقط کانفیگ‌ها را دریافت کن')
    
    args = parser.parse_args()
    
    print("🔍 کانفیگ یاب حرفه‌ای")
    print("=" * 50)
    
    # بررسی dependencies
    check_dependencies()
    
    try:
        if args.fetch_only:
            # فقط دریافت کانفیگ‌ها
            configs = asyncio.run(fetch_and_test())
            print(f"\n📊 خلاصه: {len(configs)} کانفیگ آماده")
            
        else:
            # اجرای کامل
            if not args.skip_test:
                print("\n1️⃣ دریافت نمونه کانفیگ‌ها...")
                asyncio.run(fetch_and_test())
            
            print("\n2️⃣ شروع سرور وب...")
            asyncio.run(start_server(
                host=args.host, 
                port=args.port, 
                auto_open=not args.no_browser
            ))
            
    except KeyboardInterrupt:
        print("\n👋 خداحافظ!")
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
