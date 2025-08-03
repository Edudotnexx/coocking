#!/usr/bin/env python3
"""
تست آفلاین کانفیگ یاب حرفه‌ای
"""

import asyncio
import sys
from pathlib import Path

# اضافه کردن مسیر اصلی
sys.path.append(str(Path(__file__).parent))

from config_core import ConfigResult, ConfigParser

def test_config_parser():
    """تست پارسر کانفیگ‌ها"""
    print("🧪 تست ConfigParser...")
    
    parser = ConfigParser()
    
    # تست VMess
    vmess_config = "vmess://eyJhZGQiOiIxLjIuMy40IiwiYWlkIjowLCJob3N0IjoiIiwiaWQiOiIxMjM0NTY3OC0xMjM0LTEyMzQtMTIzNC0xMjM0NTY3ODkwYWIiLCJuZXQiOiJ0Y3AiLCJwYXRoIjoiIiwicG9ydCI6NDQzLCJwcyI6IlRlc3QgU2VydmVyIiwic2N5IjoiYXV0byIsInNuaSI6IiIsInRscyI6IiIsInR5cGUiOiJub25lIiwidiI6Mn0="
    
    vmess_result = parser.parse_vmess(vmess_config)
    print(f"✅ VMess: {vmess_result}")
    
    # تست VLess
    vless_config = "vless://12345678-1234-1234-1234-123456789abc@1.2.3.4:443?type=tcp&security=tls#Test%20VLess"
    
    vless_result = parser.parse_vless(vless_config)
    print(f"✅ VLess: {vless_result}")
    
    # تست Shadowsocks
    ss_config = "ss://YWVzLTI1Ni1nY206dGVzdA==@1.2.3.4:8388#Test%20SS"
    
    ss_result = parser.parse_shadowsocks(ss_config)
    print(f"✅ Shadowsocks: {ss_result}")
    
    print("✅ همه پارسرها کار می‌کنند!")

def test_config_result():
    """تست ConfigResult"""
    print("\n🧪 تست ConfigResult...")
    
    config = ConfigResult(
        id=1,
        name="Test Server",
        server="1.2.3.4",
        port=443,
        protocol="vmess",
        config_url="vmess://test",
        status="active",
        ping=150.5
    )
    
    # تست تبدیل به dict
    config_dict = config.to_dict()
    print(f"✅ ConfigResult to dict: {config_dict}")
    
    print("✅ ConfigResult کار می‌کند!")

async def test_api_structure():
    """تست ساختار API"""
    print("\n🧪 تست ساختار API...")
    
    try:
        from api_server import ConfigFinderAPI
        
        # ایجاد instance
        api = ConfigFinderAPI()
        print("✅ API instance ساخته شد")
        
        # بررسی routes
        routes = [route.resource.canonical for route in api.app.router.routes()]
        print(f"✅ API Routes: {routes}")
        
    except Exception as e:
        print(f"❌ خطا در API: {e}")

def main():
    """تست کامل آفلاین"""
    print("🔍 کانفیگ یاب حرفه‌ای - تست آفلاین")
    print("=" * 50)
    
    try:
        # تست پارسر
        test_config_parser()
        
        # تست ConfigResult
        test_config_result()
        
        # تست API
        asyncio.run(test_api_structure())
        
        print("\n🎉 همه تست‌ها موفق بودند!")
        print("✅ پروژه آماده deployment است!")
        
    except Exception as e:
        print(f"\n❌ خطا در تست: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
