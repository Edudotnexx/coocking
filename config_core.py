#!/usr/bin/env python3
"""
کانفیگ یاب حرفه‌ای - Core Classes
توسط: @Itsthemoein
"""

import asyncio
import aiohttp
import base64
import json
import re
import urllib.parse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConfigResult:
    """کلاس برای نگهداری نتایج کانفیگ"""
    id: int
    name: str
    server: str
    port: int
    protocol: str
    config_url: str
    status: str = "untested"  # untested, active, slow, dead
    ping: Optional[float] = None
    download_speed: Optional[float] = None
    country: Optional[str] = None
    last_tested: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """تبدیل به dictionary برای JSON"""
        result = asdict(self)
        if self.last_tested:
            result['last_tested'] = self.last_tested.isoformat()
        return result

class ConfigParser:
    """کلاس برای پارس کردن انواع کانفیگ‌ها"""
    
    @staticmethod
    def parse_vmess(config_url: str) -> Optional[Dict]:
        """پارس کانفیگ VMess"""
        try:
            if not config_url.startswith('vmess://'):
                return None
            
            # حذف vmess:// و decode base64
            encoded_data = config_url[8:]
            decoded_data = base64.b64decode(encoded_data).decode('utf-8')
            config_data = json.loads(decoded_data)
            
            return {
                'name': config_data.get('ps', 'Unknown'),
                'server': config_data.get('add', ''),
                'port': int(config_data.get('port', 443)),
                'protocol': 'vmess',
                'uuid': config_data.get('id', ''),
                'alterId': config_data.get('aid', 0),
                'security': config_data.get('scy', 'auto'),
                'network': config_data.get('net', 'tcp'),
                'type': config_data.get('type', 'none'),
                'host': config_data.get('host', ''),
                'path': config_data.get('path', ''),
                'tls': config_data.get('tls', ''),
                'sni': config_data.get('sni', '')
            }
        except Exception as e:
            logger.error(f"Error parsing VMess config: {e}")
            return None
    
    @staticmethod
    def parse_vless(config_url: str) -> Optional[Dict]:
        """پارس کانفیگ VLESS"""
        try:
            if not config_url.startswith('vless://'):
                return None
            
            # پارس URL
            parsed = urllib.parse.urlparse(config_url)
            query_params = urllib.parse.parse_qs(parsed.query)
            
            return {
                'name': urllib.parse.unquote(parsed.fragment) if parsed.fragment else 'Unknown',
                'server': parsed.hostname,
                'port': int(parsed.port) if parsed.port else 443,
                'protocol': 'vless',
                'uuid': parsed.username,
                'encryption': query_params.get('encryption', ['none'])[0],
                'security': query_params.get('security', ['none'])[0],
                'type': query_params.get('type', ['tcp'])[0],
                'host': query_params.get('host', [''])[0],
                'path': query_params.get('path', [''])[0],
                'sni': query_params.get('sni', [''])[0]
            }
        except Exception as e:
            logger.error(f"Error parsing VLESS config: {e}")
            return None
    
    @staticmethod
    def parse_shadowsocks(config_url: str) -> Optional[Dict]:
        """پارس کانفیگ Shadowsocks"""
        try:
            if not config_url.startswith('ss://'):
                return None
            
            # حذف ss://
            url_without_scheme = config_url[5:]
            
            # جدا کردن fragment (نام)
            if '#' in url_without_scheme:
                url_part, fragment = url_without_scheme.split('#', 1)
                name = urllib.parse.unquote(fragment)
            else:
                url_part = url_without_scheme
                name = 'Unknown'
            
            # decode base64
            if '@' in url_part:
                # فرمت جدید: method:password@server:port
                encoded_part, server_part = url_part.split('@', 1)
                decoded = base64.b64decode(encoded_part).decode('utf-8')
                method, password = decoded.split(':', 1)
                
                if ':' in server_part:
                    server, port = server_part.rsplit(':', 1)
                else:
                    server, port = server_part, '8388'
            else:
                # فرمت قدیمی: کل چیز encode شده
                decoded = base64.b64decode(url_part).decode('utf-8')
                method, password, server, port = decoded.replace('@', ':').split(':')
            
            return {
                'name': name,
                'server': server,
                'port': int(port),
                'protocol': 'shadowsocks',
                'method': method,
                'password': password
            }
        except Exception as e:
            logger.error(f"Error parsing Shadowsocks config: {e}")
            return None
    
    @staticmethod
    def parse_trojan(config_url: str) -> Optional[Dict]:
        """پارس کانفیگ Trojan"""
        try:
            if not config_url.startswith('trojan://'):
                return None
            
            parsed = urllib.parse.urlparse(config_url)
            query_params = urllib.parse.parse_qs(parsed.query)
            
            return {
                'name': urllib.parse.unquote(parsed.fragment) if parsed.fragment else 'Unknown',
                'server': parsed.hostname,
                'port': int(parsed.port) if parsed.port else 443,
                'protocol': 'trojan',
                'password': parsed.username,
                'sni': query_params.get('sni', [''])[0],
                'type': query_params.get('type', ['tcp'])[0],
                'security': query_params.get('security', ['tls'])[0]
            }
        except Exception as e:
            logger.error(f"Error parsing Trojan config: {e}")
            return None

class ConfigFetcher:
    """کلاس برای دریافت کانفیگ‌ها از منابع مختلف"""
    
    def __init__(self):
        self.session = None
        self.sources = {
            'vmess_iran': 'https://raw.githubusercontent.com/Farid-Karimi/Config-Collector/main/vmess_iran.txt',
            'mixed_iran': 'https://raw.githubusercontent.com/Farid-Karimi/Config-Collector/main/mixed_iran.txt',
            'arshia_mix': 'https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/mix/sub.html',
            'arshia_ss': 'https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/ss.html',
            'arshia_vless': 'https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/vless.html'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'ConfigFinder/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_configs(self, source_name: str) -> List[str]:
        """دریافت کانفیگ‌ها از یک منبع مشخص"""
        if source_name not in self.sources:
            raise ValueError(f"منبع '{source_name}' پشتیبانی نمی‌شود")
        
        url = self.sources[source_name]
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(f"HTTP {response.status}")
                
                content = await response.text()
                
                # اگر محتوا HTML است، کانفیگ‌ها را استخراج کن
                if source_name.startswith('arshia_'):
                    return self._extract_from_html(content)
                else:
                    # محتوا plain text است
                    configs = [line.strip() for line in content.split('\n') if line.strip()]
                    return configs
                    
        except Exception as e:
            logger.error(f"خطا در دریافت کانفیگ از {source_name}: {e}")
            return []
    
    def _extract_from_html(self, html_content: str) -> List[str]:
        """استخراج کانفیگ‌ها از محتوای HTML"""
        configs = []
        
        # پیدا کردن VMess configs
        vmess_pattern = r'vmess://[A-Za-z0-9+/=]+'
        vmess_configs = re.findall(vmess_pattern, html_content)
        configs.extend(vmess_configs)
        
        # پیدا کردن VLESS configs
        vless_pattern = r'vless://[A-Za-z0-9+/=@:?#&;.,-_]+'
        vless_configs = re.findall(vless_pattern, html_content)
        configs.extend(vless_configs)
        
        # پیدا کردن SS configs
        ss_pattern = r'ss://[A-Za-z0-9+/=@:?#&;.,-_]+'
        ss_configs = re.findall(ss_pattern, html_content)
        configs.extend(ss_configs)
        
        # پیدا کردن Trojan configs
        trojan_pattern = r'trojan://[A-Za-z0-9+/=@:?#&;.,-_]+'
        trojan_configs = re.findall(trojan_pattern, html_content)
        configs.extend(trojan_configs)
        
        return configs
    
    async def fetch_all_sources(self) -> Dict[str, List[str]]:
        """دریافت کانفیگ‌ها از همه منابع"""
        results = {}
        
        tasks = []
        for source_name in self.sources:
            task = asyncio.create_task(self.fetch_configs(source_name))
            tasks.append((source_name, task))
        
        for source_name, task in tasks:
            try:
                configs = await task
                results[source_name] = configs
                logger.info(f"دریافت {len(configs)} کانفیگ از {source_name}")
            except Exception as e:
                logger.error(f"خطا در دریافت از {source_name}: {e}")
                results[source_name] = []
        
        return results

class ConfigProcessor:
    """کلاس اصلی برای پردازش کانفیگ‌ها"""
    
    def __init__(self):
        self.parser = ConfigParser()
    
    def process_configs(self, raw_configs: List[str]) -> List[ConfigResult]:
        """پردازش لیست کانفیگ‌های خام"""
        processed_configs = []
        config_id = 0
        
        for config_url in raw_configs:
            config_url = config_url.strip()
            if not config_url:
                continue
            
            # تشخیص نوع پروتکل و پارس
            parsed_config = None
            
            if config_url.startswith('vmess://'):
                parsed_config = self.parser.parse_vmess(config_url)
            elif config_url.startswith('vless://'):
                parsed_config = self.parser.parse_vless(config_url)
            elif config_url.startswith('ss://'):
                parsed_config = self.parser.parse_shadowsocks(config_url)
            elif config_url.startswith('trojan://'):
                parsed_config = self.parser.parse_trojan(config_url)
            
            if parsed_config:
                config_result = ConfigResult(
                    id=config_id,
                    name=parsed_config.get('name', f'Server {config_id}'),
                    server=parsed_config.get('server', 'Unknown'),
                    port=parsed_config.get('port', 0),
                    protocol=parsed_config.get('protocol', 'unknown'),
                    config_url=config_url
                )
                processed_configs.append(config_result)
                config_id += 1
        
        return processed_configs
    
    async def process_all_sources(self) -> List[ConfigResult]:
        """دریافت و پردازش همه کانفیگ‌ها"""
        all_configs = []
        
        async with ConfigFetcher() as fetcher:
            sources_data = await fetcher.fetch_all_sources()
            
            for source_name, configs in sources_data.items():
                logger.info(f"پردازش {len(configs)} کانفیگ از {source_name}")
                processed = self.process_configs(configs)
                all_configs.extend(processed)
        
        logger.info(f"مجموع {len(all_configs)} کانفیگ پردازش شد")
        return all_configs

# تست کلاس‌ها
async def main():
    """تست کلاس‌های ساخته شده"""
    processor = ConfigProcessor()
    configs = await processor.process_all_sources()
    
    print(f"✅ {len(configs)} کانفیگ دریافت و پردازش شد")
    
    # نمایش نمونه
    for i, config in enumerate(configs[:5]):
        print(f"\n📋 کانفیگ {i+1}:")
        print(f"   نام: {config.name}")
        print(f"   سرور: {config.server}:{config.port}")
        print(f"   پروتکل: {config.protocol}")
        print(f"   وضعیت: {config.status}")

if __name__ == "__main__":
    asyncio.run(main())
